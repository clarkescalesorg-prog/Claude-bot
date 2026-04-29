"""
Storefront for The UK Roofer Lead-Gen Playbook.

Routes:
  GET  /                     landing page
  POST /checkout             create Stripe Checkout session, redirect
  GET  /success              post-payment thank-you page
  GET  /download/<token>     time-limited, single-use download link
  POST /webhook              Stripe webhook (payment_intent.succeeded)

Run locally:
  pip install -r ../requirements.txt
  export $(grep -v '^#' ../.env | xargs)
  flask --app product.server run --port 5000
"""
from __future__ import annotations

import hmac
import os
import secrets
import sqlite3
import time
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

PRODUCT_DIR = Path(__file__).parent
DB_PATH = PRODUCT_DIR / "orders.db"
GUIDE_FILE = PRODUCT_DIR / "guide.md"
DOWNLOAD_TTL_SECONDS = 7 * 24 * 60 * 60  # 7 days
PRICE_GBP_PENCE = 4900  # £49.00
PRODUCT_NAME = "The UK Roofer Lead-Gen Playbook"

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
PUBLIC_BASE_URL = os.environ.get("PUBLIC_BASE_URL", "http://localhost:5000")

app = Flask(__name__, template_folder=str(PRODUCT_DIR / "templates"))


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stripe_session_id TEXT UNIQUE,
                email TEXT,
                amount_pence INTEGER,
                download_token TEXT UNIQUE,
                token_expires_at INTEGER,
                downloads_used INTEGER DEFAULT 0,
                created_at INTEGER DEFAULT (strftime('%s','now'))
            )
            """
        )
        conn.commit()
        g.db = conn
    return g.db


@app.teardown_appcontext
def _close_db(_exc):
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()


@app.route("/")
def landing():
    return render_template(
        "landing.html",
        product_name=PRODUCT_NAME,
        price_display=f"£{PRICE_GBP_PENCE / 100:.0f}",
    )


@app.route("/checkout", methods=["POST"])
def checkout():
    if not stripe.api_key:
        abort(500, "Stripe is not configured. Set STRIPE_SECRET_KEY.")

    session = stripe.checkout.Session.create(
        mode="payment",
        line_items=[
            {
                "price_data": {
                    "currency": "gbp",
                    "product_data": {
                        "name": PRODUCT_NAME,
                        "description": "PDF guide + templates bundle. Single-business licence.",
                    },
                    "unit_amount": PRICE_GBP_PENCE,
                },
                "quantity": 1,
            }
        ],
        success_url=f"{PUBLIC_BASE_URL}/success?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{PUBLIC_BASE_URL}/",
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
        "SELECT download_token FROM orders WHERE stripe_session_id = ?",
        (session_id,),
    ).fetchone()

    # Fallback: if the webhook hasn't fired yet, verify directly with Stripe
    # and create the order record now. This makes local testing painless.
    if row is None and stripe.api_key:
        sess = stripe.checkout.Session.retrieve(session_id)
        if sess.payment_status == "paid":
            row = _record_order(
                conn,
                stripe_session_id=session_id,
                email=(sess.customer_details.email if sess.customer_details else ""),
                amount_pence=sess.amount_total or PRICE_GBP_PENCE,
            )

    if row is None:
        return render_template("success.html", pending=True, download_url=None)

    token = row["download_token"]
    return render_template(
        "success.html",
        pending=False,
        download_url=url_for("download", token=token, _external=True),
    )


@app.route("/download/<token>")
def download(token: str):
    conn = get_db()
    row = conn.execute(
        "SELECT id, token_expires_at, downloads_used FROM orders WHERE download_token = ?",
        (token,),
    ).fetchone()
    if row is None:
        abort(404)
    if int(time.time()) > row["token_expires_at"]:
        abort(410, "Download link expired. Reply to your receipt to get a new one.")
    if row["downloads_used"] >= 5:
        abort(429, "Download limit reached.")

    conn.execute(
        "UPDATE orders SET downloads_used = downloads_used + 1 WHERE id = ?",
        (row["id"],),
    )
    conn.commit()
    return send_file(GUIDE_FILE, as_attachment=True, download_name="roofer-leadgen-playbook.md")


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
            _record_order(
                get_db(),
                stripe_session_id=sess["id"],
                email=(sess.get("customer_details") or {}).get("email", ""),
                amount_pence=sess.get("amount_total") or PRICE_GBP_PENCE,
            )
    return jsonify(received=True)


def _record_order(
    conn: sqlite3.Connection,
    *,
    stripe_session_id: str,
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

    token = secrets.token_urlsafe(32)
    expires = int(time.time()) + DOWNLOAD_TTL_SECONDS
    conn.execute(
        """
        INSERT INTO orders (stripe_session_id, email, amount_pence,
                            download_token, token_expires_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (stripe_session_id, email, amount_pence, token, expires),
    )
    conn.commit()
    return conn.execute(
        "SELECT * FROM orders WHERE stripe_session_id = ?",
        (stripe_session_id,),
    ).fetchone()


@app.route("/healthz")
def healthz():
    return jsonify(
        ok=True,
        stripe_configured=bool(stripe.api_key),
        webhook_configured=bool(STRIPE_WEBHOOK_SECRET),
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), debug=False)
