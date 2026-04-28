# Digital product storefront

Sells **The UK Roofer Lead-Gen Playbook** (`guide.md`) for £49 via Stripe Checkout, with a time-limited download link issued after payment.

## Files

```
product/
├── guide.md              # the digital product itself
├── server.py             # Flask app: landing, checkout, webhook, download
├── templates/
│   ├── landing.html      # sales page
│   └── success.html      # post-purchase page with download
├── orders.db             # SQLite, created on first run
└── README.md
```

## Run locally

```bash
pip install -r ../requirements.txt
cp ../.env.example ../.env       # fill in STRIPE_SECRET_KEY etc.
export $(grep -v '^#' ../.env | xargs)
flask --app product.server run --port 5000
```

Visit http://localhost:5000.

## Stripe setup

1. Create a Stripe account → grab test API keys.
2. Set `STRIPE_SECRET_KEY` and `PUBLIC_BASE_URL` in `.env`.
3. For local webhook testing:
   ```bash
   stripe listen --forward-to localhost:5000/webhook
   ```
   Stripe CLI prints a `whsec_…` secret — set it as `STRIPE_WEBHOOK_SECRET`.
4. Test with card `4242 4242 4242 4242`, any future expiry, any CVC.

## Going to production

- Deploy on Fly.io, Railway, or Render. Any platform that runs a Python web service works.
- Set `PUBLIC_BASE_URL=https://yourdomain.com`.
- Switch to live Stripe keys.
- Configure the live webhook endpoint in the Stripe dashboard pointing at `/webhook`.
- Put the Flask app behind gunicorn: `gunicorn product.server:app`.
- Persist `orders.db` on a volume (or migrate to Postgres for multi-instance deploys).

## How the flow works

1. Visitor lands on `/`, clicks **Buy now**.
2. `POST /checkout` creates a Stripe Checkout session and 303-redirects.
3. After payment, Stripe sends them to `/success?session_id=…`.
4. The webhook at `/webhook` records the order and mints a download token.
   - The success page also has a fallback: if the webhook is delayed, it
     calls Stripe directly to confirm payment and creates the order itself.
5. `/download/<token>` serves `guide.md`. The token is valid for 7 days and
   permits up to 5 downloads.

## Pricing & licence

Price is hardcoded as `PRICE_GBP_PENCE = 4900` in `server.py`. Change there.
The playbook is sold under a single-business licence (see footer of `guide.md`).
