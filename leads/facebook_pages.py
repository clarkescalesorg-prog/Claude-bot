"""Enrich leads with public Facebook Page data via the Graph API.

Flow: we already have each lead's website (from Google Places). We fetch the
homepage, extract the first facebook.com/<username> link, then call the Graph
API for the Page's public fields. This only reads data Pages choose to publish.
"""
import re
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse

import requests

from config import FACEBOOK_GRAPH_TOKEN, FACEBOOK_GRAPH_VERSION

GRAPH_BASE = f"https://graph.facebook.com/{FACEBOOK_GRAPH_VERSION}"
PAGE_FIELDS = "id,name,link,username,category,verification_status,fan_count,rating_count,overall_star_rating"
ACTIVE_WINDOW_DAYS = 90

_USERNAME_RE = re.compile(r"facebook\.com/(?!sharer|dialog|tr|plugins|privacy|policies|help)([A-Za-z0-9.\-]+)", re.I)
_RESERVED = {"pages", "pg", "people", "profile.php", "home.php", "login", "watch", "groups"}


def find_page_username(website: str, timeout: float = 8.0) -> str | None:
    """Fetch the site's homepage and return the first Facebook page username."""
    try:
        resp = requests.get(website, timeout=timeout, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
    except requests.RequestException:
        return None

    for match in _USERNAME_RE.finditer(resp.text):
        username = match.group(1).strip("/").split("?")[0].split("#")[0]
        if username and username.lower() not in _RESERVED:
            return username
    return None


def fetch_page(username_or_id: str) -> dict | None:
    """Call Graph API for a Page. Returns None if not found or unauthorised."""
    resp = requests.get(
        f"{GRAPH_BASE}/{username_or_id}",
        params={"fields": PAGE_FIELDS, "access_token": FACEBOOK_GRAPH_TOKEN},
        timeout=10,
    )
    if resp.status_code != 200:
        return None
    return resp.json()


def fetch_last_post_time(page_id: str) -> str | None:
    """Return ISO timestamp of the Page's most recent published post, or None."""
    resp = requests.get(
        f"{GRAPH_BASE}/{page_id}/posts",
        params={"fields": "created_time", "limit": 1, "access_token": FACEBOOK_GRAPH_TOKEN},
        timeout=10,
    )
    if resp.status_code != 200:
        return None
    data = resp.json().get("data") or []
    return data[0]["created_time"] if data else None


def _is_active(last_post_at: str | None) -> bool:
    if not last_post_at:
        return False
    try:
        dt = datetime.fromisoformat(last_post_at.replace("Z", "+00:00"))
    except ValueError:
        return False
    return dt >= datetime.now(timezone.utc) - timedelta(days=ACTIVE_WINDOW_DAYS)


def enrich(website: str) -> dict | None:
    """Return enrichment dict for a lead, or None if no FB page found.

    Dict keys match update_fb_enrichment's expected parameters.
    """
    if not website or not urlparse(website).netloc:
        return None

    username = find_page_username(website)
    if not username:
        return None

    page = fetch_page(username)
    if not page:
        return None

    last_post_at = fetch_last_post_time(page["id"])

    return {
        "fb_page_id": page.get("id"),
        "fb_page_url": page.get("link"),
        "fb_username": page.get("username") or username,
        "fb_category": page.get("category"),
        "fb_fan_count": page.get("fan_count"),
        "fb_rating": page.get("overall_star_rating"),
        "fb_rating_count": page.get("rating_count"),
        "fb_verified": page.get("verification_status"),
        "fb_is_active": 1 if _is_active(last_post_at) else 0,
        "fb_last_post_at": last_post_at,
    }
