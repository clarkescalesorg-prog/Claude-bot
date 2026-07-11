# Roofer Outreach Bot

Finds UK roofing contractors on Google Places, segments them into hot/warm/cold
tiers by review count, and runs a 3-step SMS/WhatsApp outreach sequence
pitching your agency's marketing services. Replies (including STOP opt-outs)
are captured automatically via an inbound webhook.

## Setup

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then fill in your real keys
```

Required environment variables (see `.env.example`):

| Variable | Description |
|---|---|
| `GOOGLE_PLACES_API_KEY` | Google Places API key, used to find roofers |
| `TWILIO_ACCOUNT_SID` / `TWILIO_AUTH_TOKEN` | Twilio credentials |
| `TWILIO_FROM_NUMBER` | Number to send from (E.164, or `whatsapp:+...`) |
| `OUTREACH_CHANNEL` | `sms` or `whatsapp` |
| `YOUR_NAME` | Sign-off name used in message templates |
| `DB_PATH` | SQLite file path (defaults to `roofers.db`) |
| `SEND_HOUR_START` / `SEND_HOUR_END` | Local-hour window outreach is allowed to send in (default `9`-`18`) |
| `FOLLOWUP_INTERVAL_MINUTES` | How often `daemon` checks for due follow-ups (default `30`) |

`.env` and `*.db` are gitignored — they hold real API secrets and prospect
contact details, so never commit them.

## Day-to-day workflow

```bash
python main.py fetch --city "Manchester" --max 60   # pull leads from Google Places
python main.py segment                               # tier by review count
python main.py outreach --tier hot                    # queue + send step 1
python main.py followup                               # send any due step 2/3 follow-ups
python main.py status                                 # dashboard: pipeline, messages, replies
```

Add `--dry-run` to `outreach`/`followup` to preview messages without sending.

Real sends (not dry runs) only go out between `SEND_HOUR_START` and
`SEND_HOUR_END` local time — messages due outside that window just stay
queued and go out on the next run inside it, so leads never get texted at
2am.

## Running unattended (`daemon`)

```bash
python main.py daemon --port 5000
```

One process that does both:

- Runs the inbound webhook (see below) so replies/STOPs are captured live.
- Checks for due follow-ups every `FOLLOWUP_INTERVAL_MINUTES` and sends them
  (respecting the sending-hours window above) — so steps 2 (day 3) and 3
  (day 7) go out automatically with nothing to remember to run.

Use `python main.py serve` instead if you only want the webhook (e.g. you're
already triggering `followup` from your own cron).

## Capturing replies

Whichever of `serve`/`daemon` you run, point your Twilio number's inbound
messaging webhook at `https://<your-domain>/sms` (use a tunnel like ngrok for
local testing). Every inbound reply is:

- Logged to the `replies` table and shown in `python main.py status`.
- Auto-marked as `replied` on the lead, so you know who to call back — no
  need to dig through the Twilio console.
- Auto-marked as `unsubscribed` if the reply is `STOP`/`UNSUBSCRIBE`/etc.,
  so opted-out leads are permanently excluded from future sends.

Requests are verified against Twilio's `X-Twilio-Signature` header, so only
genuine Twilio callbacks are accepted.

## Manual status updates

```bash
python main.py update <lead_id> booked
```

Valid statuses: `new`, `contacted`, `replied`, `booked`, `rejected`, `unsubscribed`.

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```
