# SMS Templates

Placeholders match the Roofer Outreach Bot CLI variables: `{name}`,
`{business_name}`, `{city}`, `{review_count}`.

Every SMS must end with `Reply STOP to opt out.` (PECR requirement).

---

## Hot tier (50+ reviews) — Day 0

```
Hi {name}, {business_name} clearly has the work locked down ({review_count}
Google reviews — impressive). Quick question: are you turning jobs away in
{city} right now? If yes, I might be able to help. — Reply STOP to opt out.
```

```
Hi {name}, saw {business_name} on Google in {city}. We work with 1 roofer
per postcode area on a survey-fee basis. Slot in {city} just opened. Worth
a 10-min chat this week? — Reply STOP to opt out.
```

## Hot tier — Day 3 follow-up

```
Hi {name}, following up — happy to send through last month's numbers from
the {city} roofer we worked with before they got too booked. Want me to
send them over? — Reply STOP to opt out.
```

## Hot tier — Day 9 break-up

```
Hi {name}, last one from me — I'll close the file unless you want me to
keep your number. Either reply YES or just ignore this and I won't message
again. — Reply STOP to opt out.
```

---

## Warm tier (20–49 reviews) — Day 0

```
Hi {name}, saw {business_name} in {city} has {review_count} Google reviews
— solid foundation. We send 4–6 pre-qualified survey requests a week to
roofers in your area. Worth a quick chat Thursday? — Reply STOP to opt out.
```

```
Hi {name}, quick one — we've got survey requests coming in for {city}
roofers and we're 1 short. {business_name} looks like a fit. Want me to
send the next one your way as a no-cost trial? — Reply STOP to opt out.
```

## Warm tier — Day 3 follow-up

```
Hi {name}, no rush — just wanted to flag that the trial survey for {city}
is still open. Free, you only pay if it converts. Want me to send it? —
Reply STOP to opt out.
```

## Warm tier — Day 9 break-up

```
Hi {name}, closing the file on this one. If lead-flow ever gets thin, my
number stays the same. All the best with {business_name}. — Reply STOP to
opt out.
```

---

## Cold tier (<20 reviews) — Day 0

```
Hi {name}, saw {business_name} is fairly new on Google in {city}. We help
roofers get the first 50 reviews and book steady survey work. Free 10-min
call if useful? — Reply STOP to opt out.
```

## Cold tier — Day 9 break-up only (skip middle follow-up)

```
Hi {name}, last message — happy to share the review-building checklist we
use even if we don't end up working together. Reply YES and I'll send it.
— Reply STOP to opt out.
```

---

## Booking confirmation

```
Hi {name}, confirmed for {time} {date}. I'll call {phone}. Should take
10–15 mins. If anything changes reply here. — {sender_name}
```

## Same-day reminder

```
Hi {name}, quick reminder — call at {time} today. Anything you'd like me
to prep, just reply. — {sender_name}
```

## No-show recovery

```
Hi {name}, missed you at {time} — totally understand, roofs don't wait.
Want me to grab another slot tomorrow morning? — {sender_name}
```
