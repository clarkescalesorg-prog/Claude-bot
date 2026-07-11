---
name: roofer-outreach
description: Operate the roofer lead-gen and SMS/WhatsApp outreach bot in this repo (main.py) — fetch UK roofer leads from Google Places, segment them by tier, preview/send cold outreach, check the pipeline dashboard, handle replies/opt-outs, and export leads to CSV. Use whenever the user asks to find roofer leads, run/check outreach or follow-ups, look at the lead pipeline or replies, or export leads for this agency's roofer campaign.
---

# Roofer Outreach Bot

This repo is a CLI tool (`main.py`) that runs a UK-roofer lead-gen and
cold-outreach pipeline for the agency: find roofing companies on Google
Places → tier them by review count → pitch them the agency's marketing
services over SMS/WhatsApp → capture replies/opt-outs automatically → track
everything in a local SQLite CRM (`db/schema.sql`).

Full command reference and design notes live in `README.md` — read it if
anything below is unclear or out of date.

## Before running anything

1. Make sure dependencies are installed: `pip install -r requirements.txt`
   (add `requirements-dev.txt` too if running tests).
2. Make sure `.env` exists and is filled in (copy `.env.example`). `config.py`
   reads `GOOGLE_PLACES_API_KEY`, `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`,
   `TWILIO_FROM_NUMBER` eagerly at import time — every command, even
   `--dry-run` ones, fails immediately if these aren't set. If the user
   hasn't configured real keys yet, say so rather than trying to fetch/send;
   dry-run/status/export can still work against whatever's already in the
   local DB.
3. All commands run as `python main.py <command>` from the repo root.

## Command reference

| Command | What it does |
|---|---|
| `fetch --city "<City>" [--max N]` | Pull roofer leads from Google Places into the DB |
| `segment` | Tier all leads: hot (50+ reviews), warm (20-49), cold (<20) |
| `outreach --tier hot\|warm\|cold [--dry-run]` | Queue + send the 3-step message sequence to `status=new` leads in that tier. `--dry-run` only previews step 1's rendered text — it makes **no DB changes** (added deliberately; earlier it mutated state even in dry-run, which was a bug) |
| `followup [--dry-run]` | Send any already-queued step 2/3 messages that are now due |
| `status` | Dashboard: pipeline counts, message stats, recent leads, recent replies |
| `export [--tier T] [--status S] [--out path.csv]` | Dump leads to CSV |
| `update <lead_id> <new_status>` | Manually set a lead's status (`new`, `contacted`, `replied`, `booked`, `rejected`, `unsubscribed`) |
| `serve [--host] [--port]` | Run only the inbound reply webhook (`/sms`) |
| `daemon [--host] [--port]` | Run the webhook **and** a scheduled job that sends due follow-ups — this is what should stay running unattended |

## Guardrails already built in — don't work around them

- **Sending hours**: real sends only happen between `SEND_HOUR_START` and
  `SEND_HOUR_END` (env vars, default 9–18 local time). Messages due outside
  that window just stay queued.
- **Opt-outs**: a reply of STOP/UNSUBSCRIBE/etc. (via the webhook) or a
  Twilio carrier-level opt-out error auto-marks the lead `unsubscribed`.
  Never manually re-queue or hand-send to an unsubscribed lead.
- **Send pacing**: `SEND_DELAY_SECONDS` paces sends within a batch — don't
  bypass `outreach`/`followup` to blast messages faster.
- Do not send real outreach to a large batch of leads without the user's
  explicit go-ahead — always offer `--dry-run` first for anything the user
  hasn't already approved sending.

## Typical requests and how to handle them

- **"Find/pull leads in <city>"** → `fetch --city "<City>"`, then usually
  `segment` right after so tiers are up to date.
- **"Show me the pipeline" / "how are we doing" / "any replies?"** →
  `status`. Read the "Recent Replies" table back to the user in plain
  English rather than just dumping the table.
- **"Send outreach to the hot leads"** → run `outreach --tier hot --dry-run`
  first, show the user what would go out, and only run it for real
  (`outreach --tier hot`) after they confirm — unless they've explicitly
  said to skip the preview.
- **"Send today's follow-ups"** → `followup` (or `--dry-run` to preview).
- **"Export leads"** → `export`, with `--tier`/`--status` filters if the
  user specified a subset; report the output path back.
- **"Mark <lead> as booked/rejected"** → look up the lead id via `status`
  or a DB query if not already known, then `update <id> <status>`.
- **"Start it up so it runs on its own"** → `daemon`, and mention it needs a
  public URL registered as the Twilio number's inbound webhook to receive
  replies (ngrok for testing, a real domain in production).

## Testing changes to this tool

If asked to modify the bot itself (not just operate it), run
`pytest` (needs `requirements-dev.txt`) before considering the change done —
see `tests/` for existing coverage and `tests/conftest.py` for how dummy env
vars are set up for tests.
