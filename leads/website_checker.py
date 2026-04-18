import requests

_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; LeadScorer/1.0)"}
_TIMEOUT = 10


def score_website(url: str) -> int:
    """Return a website quality score.

    0 = no website (best prospect — needs one built from scratch)
    1 = poor website (good prospect — site exists but is low quality)
    2 = adequate website (lower priority)
    """
    if not url:
        return 0

    try:
        resp = requests.get(url, timeout=_TIMEOUT, headers=_HEADERS, allow_redirects=True)
    except Exception:
        return 0

    if resp.status_code != 200:
        return 0

    html = resp.text.lower()
    score = 1  # baseline: site loads

    is_https = resp.url.startswith("https://")
    has_viewport = 'name="viewport"' in html
    has_content = len(html) > 15_000

    # Needs at least HTTPS + mobile viewport + substantial content to be "adequate"
    if is_https and has_viewport and has_content:
        score = 2

    return score
