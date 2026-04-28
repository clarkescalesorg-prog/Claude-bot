# The UK Roofer Outreach Playbook

> A practical guide to turning a list of UK roofing companies into booked
> surveys, using SMS, WhatsApp, and email — without getting reported as spam.

---

## 1. The opportunity

There are roughly 18,000 active roofing businesses in the UK. Most of them:

- Have a Google Business Profile but fewer than 30 reviews.
- Don't run paid ads — they survive on word of mouth and Checkatrade.
- Quote 20–40 jobs a month and close 4–8.
- Have no CRM and no follow-up system.

If you can deliver a steady stream of pre-qualified survey requests, you can
charge £150–£400 per booked job, or £800–£2,000/month on retainer.

## 2. Sourcing leads

The cleanest source is the Google Places API. Search `"roofer in {city}"`
across the 60 largest UK cities and you'll surface 5,000–7,000 distinct
businesses with phone numbers, websites, and review counts.

Avoid scraping Checkatrade, Trustpilot, or Yell directly — their terms forbid
it and the data goes stale fast. The bundled `leads/google_places.py` script
in the Roofer Outreach Bot already does this correctly.

## 3. Segmentation: why review count matters

Review count is the single best free signal of lead quality:

| Tier | Reviews | Why it matters |
|------|---------|----------------|
| Hot  | 50+     | Established. Already getting work. Will pay for *better* leads. |
| Warm | 20–49   | Growing. Hungry. Most likely to reply to outreach. |
| Cold | <20     | New or inactive. Reply rate under 3%. Skip unless you have spare capacity. |

Always lead with **warm tier first**. Hot tier converts but is harder to
reach; cold tier wastes your sender reputation.

## 4. Compliance (UK PECR + GDPR)

**Before you send a single message, read this section.**

- B2B SMS to a sole trader's mobile is treated as B2C under PECR. You need
  consent **or** a soft opt-in **or** a legitimate-interest balancing test
  with a clear opt-out.
- Limited companies are easier — a "corporate subscriber" can be contacted
  without prior consent, but they can still object.
- Every message must include an opt-out: `Reply STOP to unsubscribe.`
- Keep a suppression list. The bundled bot writes one to
  `db/unsubscribed.csv`.
- Never claim to have worked with someone you haven't.
- Never imply the recipient asked to be contacted when they didn't.

If in doubt, default to email — it's a softer channel and PECR enforcement
is rare for genuine B2B prospecting.

## 5. The 3-step cadence

```
Day 0   — Initial message     (high specificity, low ask)
Day 3   — Soft follow-up      (acknowledge silence, restate value)
Day 9   — Final break-up      ("closing the file" — drives the most replies)
```

Don't send more than 3 messages. The 4th gets you reported.

## 6. The opening message — what works

Three things every opener needs:

1. **Specificity** — name the city, the business, or a recent review.
2. **A concrete number** — "5 booked surveys" beats "more leads".
3. **A 1-tap reply path** — "Worth a quick chat?" beats a calendar link.

Bad:

> Hi, we help roofers get more leads. Interested?

Good:

> Hi {name}, saw {business_name} has {review_count} reviews on Google —
> nice work. We send pre-qualified survey requests to 4 roofers in {city}
> and the {city} slot is open. Worth a quick chat Thursday?

## 7. Reply handling

Most replies fall into 5 buckets. Have a canned response for each:

- **"How much?"** → Give a range, then ask about volume.
- **"Send info"** → One paragraph + one link. Never a PDF on first reply.
- **"Not interested"** → "No problem — I'll close the file. All the best."
- **"Already have someone"** → "Understood. If that ever changes, my number
  stays the same."
- **"STOP"** → Add to suppression list immediately. No reply.

## 8. Booking the call

Use a 15-minute slot, not 30. Roofers are busy and a shorter slot converts
better. Confirm by SMS the morning of the call. No-show rate drops from
~35% to under 15% with a same-day reminder.

## 9. Pricing your service

Three models, in order of difficulty:

1. **Per-lead** — £40–£80 per qualified survey request. Easiest to sell,
   hardest to scale.
2. **Retainer** — £800–£2,000/month for exclusivity in a postcode area.
3. **Rev-share** — 10–15% of closed job value. Highest upside, requires
   trust and tracking.

Start with per-lead, move to retainer once you have 2 case studies.

## 10. Scaling

Once one city is profitable, the move is **horizontal**: same playbook,
different city. Don't try to bolt on plumbers or electricians until you've
saturated 5 roofing markets — the templates and objections are different
enough that you'll halve your win rate.

---

## Appendix A — KPIs to track

| Metric | Target |
|--------|--------|
| Delivery rate | >97% |
| Reply rate (warm tier) | 8–14% |
| Reply-to-call rate | 30–50% |
| Call-to-booked rate | 40–60% |
| Cost per booked survey | <£25 |

## Appendix B — Recommended tooling

- **Sourcing**: Google Places API (free tier covers ~3 cities/day).
- **Sending**: Twilio for SMS, Twilio Conversations or 360dialog for WhatsApp.
- **CRM**: SQLite + the bundled bot is enough for the first 10,000 leads.
- **Calls**: Cal.com (self-hosted) or Calendly.

## Appendix C — Common mistakes

1. Sending on Sunday evening "to catch them when they're free." You won't.
   Send Tue–Thu, 10am–4pm.
2. Using emojis in cold SMS. Reply rate drops 30–40%.
3. Linking to a website on first contact. Recipients treat it as phishing.
4. Forgetting the opt-out. One complaint to ICO and your sender ID is
   blacklisted.
