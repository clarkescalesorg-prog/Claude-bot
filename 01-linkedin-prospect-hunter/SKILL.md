# Skill: LinkedIn Prospect Hunter

## Overview

Finds and imports B2B prospects from LinkedIn into the lead pipeline. Searches for roofing contractors and related trades by job title, location, and company size, then stores enriched contact records ready for segmentation and outreach.

## What It Does

1. Searches LinkedIn for prospects matching configurable criteria (job title, geography, industry)
2. Extracts structured contact data: name, company, location, phone (where public), LinkedIn URL
3. Deduplicates against existing leads using phone number or LinkedIn URL as the key
4. Upserts records into the `leads` table with `source = 'linkedin'`
5. Leaves new records in `status = 'new'` so they flow into the normal `segment → outreach` pipeline

## When to Use

Use this skill when Google Places coverage is thin for a target city, when you want to reach decision-makers by name rather than business listing, or when you need to target specific job titles (e.g. "Owner", "Director", "MD") at roofing firms.

## Inputs

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--query` | string | `"roofing contractor"` | LinkedIn search query (job title or keywords) |
| `--location` | string | required | City or region, e.g. `"Manchester, UK"` |
| `--max` | int | `50` | Maximum prospects to import per run |
| `--dry-run` | flag | off | Print prospects without writing to database |

## Outputs

- Prospects upserted into the `leads` table
- Summary printed to stdout: new records added, duplicates skipped, failures
- `--dry-run` prints a Rich table preview instead of writing

## Configuration

Add the following to your `.env` file:

```env
LINKEDIN_EMAIL=your@email.com
LINKEDIN_PASSWORD=your_password
# OR use a cookie-based session token (preferred):
LINKEDIN_LI_AT_COOKIE=your_li_at_cookie_value
```

`li_at` cookie authentication is more stable than password login and less likely to trigger account restrictions. Retrieve it from browser DevTools → Application → Cookies → `www.linkedin.com`.

## Usage

```bash
# Preview prospects in Leeds without writing to DB
python main.py linkedin-hunt --location "Leeds, UK" --dry-run

# Import up to 40 owner/director prospects in Birmingham
python main.py linkedin-hunt --query "roofing director" --location "Birmingham, UK" --max 40

# Segment and outreach after import (standard pipeline)
python main.py segment
python main.py outreach --tier hot
```

## Integration with the Pipeline

```
linkedin-hunt  ──┐
fetch (Google)  ──┼──► leads table ──► segment ──► outreach ──► followup
                  │
             (both sources feed the same table)
```

LinkedIn leads flow through the same `tier` and `status` lifecycle as Google Places leads. The `source` column (`'google'` vs `'linkedin'`) is stored for reporting but does not affect downstream behaviour.

## Rate Limiting & Safety

- Introduces a 3–8 second randomised delay between profile fetches to avoid triggering LinkedIn's bot detection
- Stops immediately if a CAPTCHA or login-wall is detected and logs a warning
- Keeps a session warm across multiple `--max` batches; re-authenticates automatically on session expiry
- Never stores LinkedIn credentials in the database

## Limitations

- LinkedIn does not expose phone numbers in most profiles; expect ~15–30 % of prospects to have a phone number available
- Prospects without a phone number are imported with `phone = NULL` and will be skipped by the SMS/WhatsApp outreach scheduler automatically
- LinkedIn's Terms of Service restrict automated scraping; use this skill responsibly and only for your own prospecting activity
- Accuracy of extracted phone numbers depends on what the prospect has made public; always verify before calling

## Files

```
01-linkedin-prospect-hunter/
├── SKILL.md              # This file
├── linkedin_hunter.py    # Core search & extraction logic
└── li_session.py         # Session management & auth helpers
```
