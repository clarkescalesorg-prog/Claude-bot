from config import YOUR_NAME

_TEMPLATES = {
    1: (
        "Hi {first_name}, I came across {business} on Google — impressive reviews! "
        "I run a marketing agency helping UK roofers get more jobs through Google Ads, SEO & social media. "
        "We've helped similar companies add £10k+/month in new work. "
        "Quick 10-min call to show you what's possible? – {your_name}"
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


def render(step: int, business_name: str, city: str) -> str:
    first_name = business_name.split()[0].rstrip(".,!") if business_name else "there"
    return _TEMPLATES[step].format(
        first_name=first_name,
        business=business_name,
        city=city or "your area",
        your_name=YOUR_NAME,
    )
