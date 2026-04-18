import time
from urllib.parse import urlparse

import requests

_FREE_BUILDERS = {
    "wix.com", "wixsite.com",
    "squarespace.com",
    "weebly.com",
    "yola.com",
    "moonfruit.com",
    "godaddywebsites.com",
    "myshopify.com",
    "jimdo.com",
    "webflow.io",
    "1and1.co.uk",
    "123-reg.co.uk",
}

_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; LeadScorer/1.0)"}


def score_website(url: str) -> dict:
    """
    Returns has_website, web_score (0-100, lower = worse = bigger opportunity),
    and web_issues (semicolon-separated problem list).
    """
    if not url:
        return {"has_website": False, "web_score": 0, "web_issues": "no website"}

    issues: list[str] = []
    score = 100

    parsed = urlparse(url)
    domain = parsed.netloc.lower().lstrip("www.")

    # Free site builder — big red flag
    for builder in _FREE_BUILDERS:
        if builder in domain:
            issues.append(f"free builder ({builder})")
            score -= 30
            break

    # No HTTPS in the original URL
    if parsed.scheme != "https":
        issues.append("no HTTPS")
        score -= 20

    try:
        start = time.time()
        resp = requests.get(
            url,
            timeout=10,
            headers=_HEADERS,
            allow_redirects=True,
        )
        elapsed = time.time() - start

        if elapsed > 5:
            issues.append(f"very slow ({elapsed:.1f}s)")
            score -= 25
        elif elapsed > 3:
            issues.append(f"slow ({elapsed:.1f}s)")
            score -= 15

        if resp.url.startswith("http://"):
            if "no HTTPS" not in issues:
                issues.append("no HTTPS redirect")
                score -= 20

        html = resp.text.lower()

        if "viewport" not in html:
            issues.append("not mobile-friendly")
            score -= 20

        if 'meta name="description"' not in html and "meta name='description'" not in html:
            issues.append("no meta description")
            score -= 5

        if "<title>" not in html:
            issues.append("no title tag")
            score -= 5

        # Very thin page — likely placeholder or single-page brochure
        if len(html) < 5_000:
            issues.append("very thin page")
            score -= 10

    except requests.exceptions.Timeout:
        issues.append("site timed out")
        score -= 50
    except Exception:
        issues.append("site unreachable")
        score -= 60

    return {
        "has_website": True,
        "web_score": max(0, score),
        "web_issues": "; ".join(issues) if issues else "none",
    }
