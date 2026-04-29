"""
Storefront for digital products.

Currently sells two products via Stripe Checkout:
  • The UK Roofer Lead-Gen Playbook  (slug: roofer-playbook)  — £49
  • The UK Money-Back Pack            (slug: money-back-pack)  — £19

Routes:
  GET  /                          index — lists all products
  GET  /p/<slug>                  product landing page
  POST /checkout/<slug>           create Stripe Checkout session, redirect
  GET  /success                   post-payment thank-you page
  GET  /download/<token>          time-limited download link
  POST /webhook                   Stripe webhook
  GET  /check                     free Money-Back eligibility checker (lead magnet)
  POST /check                     submit checker answers, render results

Run locally:
  pip install -r ../requirements.txt
  export $(grep -v '^#' ../.env | xargs)
  flask --app product.server run --port 5000
"""
from __future__ import annotations

import io
import os
import secrets
import sqlite3
import time
import zipfile
from dataclasses import dataclass
from pathlib import Path

import stripe
from flask import (
    Flask,
    abort,
    g,
    jsonify,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)

from product.moneyback.checker import QUESTIONS, evaluate, total_potential

PRODUCT_DIR = Path(__file__).parent
DB_PATH = PRODUCT_DIR / "orders.db"
DOWNLOAD_TTL_SECONDS = 7 * 24 * 60 * 60  # 7 days
DOWNLOAD_LIMIT = 5

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
PUBLIC_BASE_URL = os.environ.get("PUBLIC_BASE_URL", "http://localhost:5000")

app = Flask(__name__, template_folder=str(PRODUCT_DIR / "templates"))


@dataclass(frozen=True)
class Product:
    slug: str
    name: str
    tagline: str
    price_pence: int
    landing_template: str
    download_filename: str
    # Files (relative to PRODUCT_DIR) to bundle into the download.
    # If a single .md file, it's served directly. Otherwise a zip is built.
    bundle_files: tuple[str, ...]
    description: str  # short description shown to Stripe at checkout

    @property
    def price_display(self) -> str:
        return f"£{self.price_pence / 100:.0f}"

    @property
    def is_zip(self) -> bool:
        return len(self.bundle_files) > 1 or any(
            not f.endswith(".md") for f in self.bundle_files
        )


PRODUCTS: dict[str, Product] = {
    "roofer-playbook": Product(
        slug="roofer-playbook",
        name="The UK Roofer Lead-Gen Playbook",
        tagline="Book 5–10 roofing jobs a month from cold outreach.",
        price_pence=4900,
        landing_template="landing.html",
        download_filename="roofer-leadgen-playbook.md",
        bundle_files=("guide.md",),
        description="PDF guide + templates bundle. Single-business licence.",
    ),
    "money-back-pack": Product(
        slug="money-back-pack",
        name="The UK Money-Back Pack",
        tagline="18 things UK households are leaving on the table — and how to claim them back.",
        price_pence=1900,
        landing_template="moneyback_landing.html",
        download_filename="uk-money-back-pack.zip",
        bundle_files=(
            "moneyback/guide.md",
            "moneyback/claims_tracker.csv",
            "moneyback/letters/council_tax_band_challenge.md",
            "moneyback/letters/single_person_discount.md",
            "moneyback/letters/marriage_allowance_steps.md",
            "moneyback/letters/section_75_claim.md",
            "moneyback/letters/energy_credit_refund.md",
            "moneyback/letters/pension_credit_check.md",
        ),
        description="Guide + 6 letter templates + claims tracker. Single-household licence.",
    ),
}


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stripe_session_id TEXT UNIQUE,
                product_slug TEXT NOT NULL DEFAULT 'roofer-playbook',
                email TEXT,
                amount_pence INTEGER,
                download_token TEXT UNIQUE,
                token_expires_at INTEGER,
                downloads_used INTEGER DEFAULT 0,
                created_at INTEGER DEFAULT (strftime('%s','now'))
            )
            """
        )
        # Forward-migrate older DBs that don't have product_slug yet.
        cols = {r["name"] for r in conn.execute("PRAGMA table_info(orders)").fetchall()}
        if "product_slug" not in cols:
            conn.execute(
                "ALTER TABLE orders ADD COLUMN product_slug TEXT NOT NULL DEFAULT 'roofer-playbook'"
            )
        conn.commit()
        g.db = conn
    return g.db


@app.teardown_appcontext
def _close_db(_exc):
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()


# --------------------------------------------------------------------- routes


@app.route("/")
def index():
    return render_template("index.html", products=list(PRODUCTS.values()))


@app.route("/p/<slug>")
def product_landing(slug: str):
    product = PRODUCTS.get(slug)
    if product is None:
        abort(404)
    return render_template(
        product.landing_template,
        product=product,
        product_name=product.name,
        price_display=product.price_display,
    )


@app.route("/checkout/<slug>", methods=["POST"])
def checkout(slug: str):
    product = PRODUCTS.get(slug)
    if product is None:
        abort(404)
    if not stripe.api_key:
        abort(500, "Stripe is not configured. Set STRIPE_SECRET_KEY.")

    session = stripe.checkout.Session.create(
        mode="payment",
        line_items=[{
            "price_data": {
                "currency": "gbp",
                "product_data": {"name": product.name, "description": product.description},
                "unit_amount": product.price_pence,
            },
            "quantity": 1,
        }],
        metadata={"product_slug": product.slug},
        success_url=f"{PUBLIC_BASE_URL}/success?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{PUBLIC_BASE_URL}/p/{product.slug}",
        allow_promotion_codes=True,
    )
    return redirect(session.url, code=303)


@app.route("/success")
def success():
    session_id = request.args.get("session_id", "")
    if not session_id:
        abort(400)

    conn = get_db()
    row = conn.execute(
        "SELECT product_slug, download_token FROM orders WHERE stripe_session_id = ?",
        (session_id,),
    ).fetchone()

    # Fallback: if the webhook hasn't fired yet, verify directly with Stripe
    # and create the order record now. This makes local testing painless.
    if row is None and stripe.api_key:
        sess = stripe.checkout.Session.retrieve(session_id)
        if sess.payment_status == "paid":
            slug = (sess.metadata or {}).get("product_slug", "roofer-playbook")
            row = _record_order(
                conn,
                stripe_session_id=session_id,
                product_slug=slug,
                email=(sess.customer_details.email if sess.customer_details else ""),
                amount_pence=sess.amount_total or PRODUCTS[slug].price_pence,
            )

    if row is None:
        return render_template("success.html", pending=True, download_url=None, product=None)

    product = PRODUCTS.get(row["product_slug"]) or next(iter(PRODUCTS.values()))
    return render_template(
        "success.html",
        pending=False,
        download_url=url_for("download", token=row["download_token"], _external=True),
        product=product,
    )


@app.route("/download/<token>")
def download(token: str):
    conn = get_db()
    row = conn.execute(
        "SELECT id, product_slug, token_expires_at, downloads_used "
        "FROM orders WHERE download_token = ?",
        (token,),
    ).fetchone()
    if row is None:
        abort(404)
    if int(time.time()) > row["token_expires_at"]:
        abort(410, "Download link expired. Reply to your receipt to get a new one.")
    if row["downloads_used"] >= DOWNLOAD_LIMIT:
        abort(429, "Download limit reached.")

    product = PRODUCTS.get(row["product_slug"])
    if product is None:
        abort(500, "Order references an unknown product.")

    conn.execute(
        "UPDATE orders SET downloads_used = downloads_used + 1 WHERE id = ?",
        (row["id"],),
    )
    conn.commit()

    return _serve_bundle(product)


@app.route("/webhook", methods=["POST"])
def webhook():
    payload = request.data
    sig = request.headers.get("Stripe-Signature", "")
    if not STRIPE_WEBHOOK_SECRET:
        abort(500, "Webhook secret not configured.")
    try:
        event = stripe.Webhook.construct_event(payload, sig, STRIPE_WEBHOOK_SECRET)
    except (ValueError, stripe.error.SignatureVerificationError):
        abort(400)

    if event["type"] == "checkout.session.completed":
        sess = event["data"]["object"]
        if sess.get("payment_status") == "paid":
            slug = (sess.get("metadata") or {}).get("product_slug", "roofer-playbook")
            _record_order(
                get_db(),
                stripe_session_id=sess["id"],
                product_slug=slug,
                email=(sess.get("customer_details") or {}).get("email", ""),
                amount_pence=sess.get("amount_total") or PRODUCTS[slug].price_pence,
            )
    return jsonify(received=True)


# --- Free Money-Back eligibility checker (lead magnet) ----------------------


@app.route("/check", methods=["GET", "POST"])
def check():
    moneyback = PRODUCTS["money-back-pack"]
    if request.method == "GET":
        return render_template(
            "check.html",
            questions=QUESTIONS,
            results=None,
            answers={},
            min_total=0,
            max_total=0,
            product=moneyback,
        )

    answers = {q["key"]: request.form.get(q["key"], "") for q in QUESTIONS}
    results = evaluate(answers)
    min_total, max_total = total_potential(results)
    return render_template(
        "check.html",
        questions=QUESTIONS,
        results=results,
        answers=answers,
        min_total=min_total,
        max_total=max_total,
        product=moneyback,
    )


# --- helpers ----------------------------------------------------------------


def _record_order(
    conn: sqlite3.Connection,
    *,
    stripe_session_id: str,
    product_slug: str,
    email: str,
    amount_pence: int,
) -> sqlite3.Row:
    """Insert an order row idempotently and return it."""
    existing = conn.execute(
        "SELECT * FROM orders WHERE stripe_session_id = ?",
        (stripe_session_id,),
    ).fetchone()
    if existing:
        return existing

    if product_slug not in PRODUCTS:
        product_slug = "roofer-playbook"

    token = secrets.token_urlsafe(32)
    expires = int(time.time()) + DOWNLOAD_TTL_SECONDS
    conn.execute(
        """
        INSERT INTO orders (stripe_session_id, product_slug, email, amount_pence,
                            download_token, token_expires_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (stripe_session_id, product_slug, email, amount_pence, token, expires),
    )
    conn.commit()
    return conn.execute(
        "SELECT * FROM orders WHERE stripe_session_id = ?",
        (stripe_session_id,),
    ).fetchone()


def _serve_bundle(product: Product):
    """Serve a single file directly, or build a zip from multiple files."""
    if not product.is_zip:
        path = PRODUCT_DIR / product.bundle_files[0]
        return send_file(path, as_attachment=True, download_name=product.download_filename)

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for rel in product.bundle_files:
            src = PRODUCT_DIR / rel
            if not src.exists():
                continue
            # Strip the top-level "moneyback/" so the zip is rooted at the product.
            arcname = rel.split("/", 1)[1] if "/" in rel else rel
            zf.write(src, arcname=arcname)
    buf.seek(0)
    return send_file(
        buf,
        mimetype="application/zip",
        as_attachment=True,
        download_name=product.download_filename,
    )


@app.route("/healthz")
def healthz():
    return jsonify(
        ok=True,
        stripe_configured=bool(stripe.api_key),
        webhook_configured=bool(STRIPE_WEBHOOK_SECRET),
        products=list(PRODUCTS.keys()),
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), debug=False)
