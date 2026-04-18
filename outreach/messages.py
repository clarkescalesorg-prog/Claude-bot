from config import YOUR_NAME

_TEMPLATES = {
    1: (
        "Hi {first_name}, I noticed {business} doesn't have a strong web presence — "
        "I help Miami roofing companies get more jobs with a professional website and Google/Facebook ad creatives. "
        "We've helped similar contractors add $8k-$15k/month in new work. "
        "Open to a free 10-min call to see what's possible? – {your_name}"
    ),
    2: (
        "Hi {first_name}, following up from my last message. "
        "I work with roofing companies across {city} and have a couple of openings this month. "
        "We handle everything: new website, Google Ads, Facebook ad creatives & SEO — starting at $1,500/month. "
        "Worth a quick chat? – {your_name}"
    ),
    3: (
        "Last one from me, {first_name} — totally understand if the timing isn't right. "
        "If you ever want more consistent roofing leads through a better website and targeted ads, feel free to reach back out. "
        "Best of luck! – {your_name}"
    ),
}


def render(step: int, business_name: str, city: str) -> str:
    first_name = business_name.split()[0].rstrip(".,!") if business_name else "there"
    return _TEMPLATES[step].format(
        first_name=first_name,
        business=business_name,
        city=city or "Miami",
        your_name=YOUR_NAME,
    )
