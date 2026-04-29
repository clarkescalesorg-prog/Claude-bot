# Digital product storefront

Sells two UK-focused digital products via Stripe Checkout, with time-limited
download links issued after payment.

| Slug              | Product                            | Price |
|-------------------|------------------------------------|-------|
| `roofer-playbook` | The UK Roofer Lead-Gen Playbook    | £49   |
| `money-back-pack` | The UK Money-Back Pack             | £19   |

The Money-Back Pack also has a free public **eligibility checker** at `/check`
that flags which UK rebates / tax reliefs / refund schemes the visitor is
likely entitled to — used as a lead magnet for the paid pack.

## Files

```
product/
├── __init__.py
├── server.py                 # Flask app: index, landings, checkout, webhook, download, /check
├── README.md
├── orders.db                 # SQLite, created on first run
├── guide.md                  # Roofer playbook (single-file product)
├── moneyback/                # Money-Back Pack (multi-file product)
│   ├── __init__.py
│   ├── guide.md              # 18-section main guide
│   ├── checker.py            # eligibility-check logic (questions + evaluate())
│   ├── claims_tracker.csv    # spreadsheet template buyers fill in
│   └── letters/              # copy-and-paste letter templates
│       ├── council_tax_band_challenge.md
│       ├── single_person_discount.md
│       ├── marriage_allowance_steps.md
│       ├── section_75_claim.md
│       ├── energy_credit_refund.md
│       └── pension_credit_check.md
└── templates/
    ├── index.html              # lists both products + free checker CTA
    ├── landing.html            # roofer-playbook sales page
    ├── moneyback_landing.html  # money-back-pack sales page
    ├── check.html              # free eligibility checker (form + results)
    └── success.html            # post-purchase page (product-aware)
```

## Run locally

```bash
pip install -r ../requirements.txt
cp ../.env.example ../.env       # fill in STRIPE_SECRET_KEY etc.
export $(grep -v '^#' ../.env | xargs)
flask --app product.server run --port 5000
```

Visit:

- http://localhost:5000/                       — index (both products)
- http://localhost:5000/p/roofer-playbook      — roofer landing
- http://localhost:5000/p/money-back-pack      — money-back-pack landing
- http://localhost:5000/check                  — free eligibility checker
- http://localhost:5000/healthz                — quick config check

## Stripe setup

1. Create a Stripe account → grab test API keys.
2. Set `STRIPE_SECRET_KEY` and `PUBLIC_BASE_URL` in `.env`.
3. For local webhook testing:
   ```bash
   stripe listen --forward-to localhost:5000/webhook
   ```
   Stripe CLI prints a `whsec_…` secret — set it as `STRIPE_WEBHOOK_SECRET`.
4. Test with card `4242 4242 4242 4242`, any future expiry, any CVC.

The product slug is sent to Stripe as session `metadata.product_slug` — the
webhook and the success-page fallback both use it to mint the right download.

## Going to production

- Deploy on Fly.io, Railway, or Render. Any platform that runs a Python web service works.
- Set `PUBLIC_BASE_URL=https://yourdomain.com`.
- Switch to live Stripe keys.
- Configure the live webhook endpoint in the Stripe dashboard pointing at `/webhook`.
- Put the Flask app behind gunicorn: `gunicorn product.server:app`.
- Persist `orders.db` on a volume (or migrate to Postgres for multi-instance deploys).

## How the flow works

1. Visitor lands on `/`, picks a product, lands on `/p/<slug>`, clicks **Buy now**.
2. `POST /checkout/<slug>` creates a Stripe Checkout session (with `product_slug`
   in metadata) and 303-redirects to Stripe.
3. After payment, Stripe sends them to `/success?session_id=…`.
4. The webhook at `/webhook` records the order, including the product slug,
   and mints a download token.
   - The success page also has a fallback: if the webhook is delayed, it
     calls Stripe directly to confirm payment and creates the order itself.
5. `/download/<token>` serves the right artefact:
   - **Single-file products** (roofer-playbook): the `.md` directly.
   - **Multi-file products** (money-back-pack): a zip built on the fly from
     `Product.bundle_files`.
   The token is valid for 7 days, max 5 downloads.

## Adding a new product

1. Add an entry to `PRODUCTS` in `server.py` with slug, name, price, landing
   template, and `bundle_files`.
2. Drop the artefact files under `product/` (a single `.md` or a folder).
3. Add a landing template under `templates/`.
4. Optional: add a section/CTA in `templates/index.html`.

The download flow handles single-file vs multi-file automatically based on the
`bundle_files` tuple.

## Pricing & licence

Prices are set in the `PRODUCTS` registry at the top of `server.py`. Both
products are sold under a single-buyer licence (see footer of each guide).
