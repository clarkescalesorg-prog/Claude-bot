from config import YOUR_NAME

_TEMPLATES = {
    # Step 1 — review-based opener (default)
    "1_reviews": (
        "Hi {first_name}, I came across {business} on Google — impressive reviews! "
        "I run a marketing agency helping UK roofers get more jobs through Google Ads, SEO & social media. "
        "We've helped similar companies add £10k+/month in new work. "
        "Quick 10-min call to show you what's possible? – {your_name}"
    ),
    # Step 1 — website gap opener (used when web_score < 40 or no website)
    "1_website": (
        "Hi {first_name}, I looked up {business} online — your Google reviews are great, "
        "but your website is holding you back from winning bigger jobs. "
        "I help UK roofers get a proper web presence + Google Ads setup that fills the diary. "
        "Worth a 10-min call? – {your_name}"
    ),
    # Step 1 — no website opener
    "1_no_website": (
        "Hi {first_name}, I searched for {business} online and couldn't find a website. "
        "Customers are Googling roofers right now and picking whoever shows up first — "
        "I can fix that fast. Quick 10-min call to explain how? – {your_name}"
    ),
    2: (
        "Hi {first_name}, following up from my last message. "
        "I work with roofing companies across {city} and have a couple of slots open this month. "
        "Full-service marketing — Google Ads, SEO, social & website — for £2,500/month. "
        "Are you open to a quick chat? – {your_name}"
    ),
    3: (
        "Last one from me, {first_name} — if now's not the right time that's totally fine. "
        "If you ever want more consistent roofing leads through Google, feel free to reach back out. "
        "Best of luck! – {your_name}"
    ),
}


def render(step: int, business_name: str, city: str, has_website: int | None = None, web_score: int | None = None) -> str:
    first_name = business_name.split()[0].rstrip(".,!") if business_name else "there"
    ctx = dict(first_name=first_name, business=business_name, city=city or "your area", your_name=YOUR_NAME)

    if step == 1:
        if has_website == 0:
            template = _TEMPLATES["1_no_website"]
        elif web_score is not None and web_score < 40:
            template = _TEMPLATES["1_website"]
        else:
            template = _TEMPLATES["1_reviews"]
    else:
        template = _TEMPLATES[step]

    return template.format(**ctx)
