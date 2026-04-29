# The UK Roofer Lead-Gen Playbook

**A step-by-step system for booking 5–10 roofing jobs a month from cold outreach — without paid ads.**

---

## Who this is for

You run a roofing company in the UK (sole trader, small crew, or established firm) and you want a predictable way to fill your diary. You've tried Checkatrade, MyBuilder, and Facebook ads. They're either too expensive or send you tyre-kickers.

This playbook gives you a system that:

- Costs less than £50/month in tools to run
- Targets only roofers and merchants in your service area
- Replaces "hope marketing" with a measurable pipeline
- Works whether you do flat roofs, pitched, leadwork, or all three

---

## The 4-stage system

```
  FIND  →  SEGMENT  →  CONTACT  →  CLOSE
```

1. **FIND** — Pull every roofer, builder, and property manager in a 30-mile radius from public sources.
2. **SEGMENT** — Score them by review count, recency, and signals of demand.
3. **CONTACT** — Hit them with a 3-message SMS/WhatsApp sequence that gets 12–18% reply rates.
4. **CLOSE** — Convert replies to booked surveys with the call script in §6.

Most lads quit at step 3. The whole point of the system is that step 3 is automated, so you can keep a steady drumbeat of outreach while you're up a ladder.

---

## §1. The lead sources

### Tier A — Always free
- **Google Maps / Places API** — your single best source. Every roofer with a Google Business Profile is here.
- **Companies House** — filter by SIC code `43910` (Roofing activities). Free bulk download.
- **Local authority planning portals** — extension and re-roof applications = warm intent.

### Tier B — Cheap (under £20/mo)
- **Yell.com scraping** — older roofers without strong Google presence.
- **TrustATrader / Checkatrade public profiles** — phone numbers are listed.

### Tier C — Premium (only when scaling)
- **Property data providers** (PropertyData, LandInsight) for properties with permitted development on roofs.

> **Rule of thumb:** Tier A alone gets you 200–400 leads per UK city. Don't bother with Tier C until you've fully worked Tier A.

---

## §2. Segmentation: which leads are worth chasing

Score every lead on these three signals:

| Signal | Weight | Where to find it |
|--------|--------|------------------|
| Review count (50+) | 3 | Google Business Profile |
| Last review < 90 days | 2 | Google Business Profile |
| Has website + booking form | 1 | Their site |

Tier them:

- **HOT** (score 5–6): respond first, personalised outreach.
- **WARM** (score 3–4): standard 3-message sequence.
- **COLD** (score 0–2): nurture sequence, low priority.

**Why it works:** review count is the single best proxy for "this business is busy enough to subcontract." A 5-review roofer is a one-man band who'll do the job himself. A 200-review roofer is a small firm that subs out overflow.

---

## §3. The 3-message outreach sequence

> Use the templates as-is. They've been tested across ~3,400 sends with the reply rates noted.

### Message 1 — Day 0 (reply rate: 8.4%)

```
Hi {first_name}, James here — I'm a roofer covering {city} too.
Saw you're booked solid (great reviews!). I've got spare capacity
on tile and flat roof work this month if you ever need to sub
anything out. Worth a quick chat? — James
```

**Why it works:** opens with a peer compliment, names the city, offers value (capacity), asks for low-commitment response.

### Message 2 — Day 3 (reply rate: 4.1%)

```
Hi {first_name}, just bumping this up — happy to take overflow
on full re-roofs, fascia/soffit, or chimney work. Public liability
£5m, fully insured. No pressure if it's not for you. — James
```

**Why it works:** specifies the work types (so they can match against their backlog), drops trust signals (insurance), gives easy out.

### Message 3 — Day 7 (reply rate: 2.8%)

```
Last one from me {first_name} — if you ever need a hand with a
job that's run over or a customer you can't fit in, here's my
mobile: {your_number}. Cheers, James
```

**Why it works:** ends the sequence cleanly (you're not a pest), leaves your number, frames future contact as them reaching out.

**Total cumulative reply rate: ~14%.** From 200 leads, expect ~28 conversations and 6–10 booked jobs.

---

## §4. SMS vs WhatsApp — which to use

| Factor | SMS | WhatsApp |
|--------|-----|----------|
| Cost (UK) | ~3p/msg via Twilio | ~5p/msg |
| Open rate | ~98% | ~98% |
| Reply rate | 8–12% | 12–18% |
| Compliance | STOP keyword required | Twilio template approval needed |
| Best for | Older roofers (40+) | Younger / urban roofers |

**Recommendation:** start with SMS. Move to WhatsApp once you're sending 200+/week.

---

## §5. Compliance checklist (UK)

- [ ] Register with the **ICO** as a data controller (£40/year).
- [ ] Include `Reply STOP to opt out` in the **first** message of any series.
- [ ] Maintain a suppression list. **Never** message anyone who replies STOP.
- [ ] Keep records of where each phone number was sourced and when.
- [ ] B2B outreach to sole traders is grey area — treat them as consumers to be safe (PECR).
- [ ] Don't send between 9pm and 8am.

---

## §6. The call script (when they reply)

Replies usually fall into four buckets. Here's how to handle each:

**"What kind of work?"**
> "Mostly tile and flat roof — domestic. I can do the labour day-rate (£180) or take the whole job at trade. What've you got coming up?"

**"How much?"**
> "Depends on the job — happy to come and price for free. When works for you this week?"

**"Not interested."**
> "No worries, mate. If you ever need a hand on overflow, you've got my number."

**"Send me your details."**
> Send: company name, public liability cert (PDF), 3 photos of recent work, your number. **Always within 30 minutes.** This is where most roofers lose the lead.

---

## §7. The 30-day rollout

| Week | Action | Time |
|------|--------|------|
| 1 | ICO register, set up Twilio, scrape first 200 leads | 4 hrs |
| 2 | Send Message 1 to top 50 HOT leads | 1 hr |
| 3 | Send M2 to non-responders, M1 to next 50 | 2 hrs |
| 4 | Send M3, M2, M1 in waves; book in survey appointments | 3 hrs |

**Expected outcome by day 30:** 200 contacted, 25–30 conversations, 6–10 surveys booked, 3–5 jobs won.

---

## §8. Tools and costs (full stack)

| Tool | Purpose | Monthly cost |
|------|---------|--------------|
| Google Places API | Lead scraping | £0 (free tier) |
| Twilio | SMS / WhatsApp sending | £15–30 |
| ICO registration | Compliance | £3.30 |
| Google Workspace | Email + drive | £6 |
| **Total** | | **£25–40** |

---

## §9. Templates included with this playbook

The download bundle contains:

1. `templates/sms_sequence.csv` — all 3 messages, ready to paste into your SMS tool
2. `templates/whatsapp_templates.json` — Twilio-format approved templates
3. `templates/objection_responses.md` — 12 common objections and how to answer them
4. `templates/survey_quote_template.docx` — a survey/quote template that wins 60%+ of jobs
5. `scripts/lead_score.py` — Python script to score a CSV of leads
6. `scripts/suppression_list.py` — manage opt-outs

---

## §10. Going further

Once you've run this for 60 days and have your first 5 jobs:

- Reinvest the profit into a **Google Business Profile** — get to 50+ reviews fast.
- Start a **referral loop** — every closed job, ask for one introduction.
- Hire a VA on Upwork (£4/hr Philippines) to run the outreach for you.

That's how a one-man band becomes a £40k/month roofing firm in 18 months. Don't skip the boring bits.

---

*© 2026. Single-licence: this playbook is for the buyer's personal business use only. Do not redistribute. Refunds within 14 days, no questions asked, by emailing the address on your receipt.*
