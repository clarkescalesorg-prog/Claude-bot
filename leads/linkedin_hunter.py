import re
import time
import random


def search_prospects(location: str, query: str = "roofing contractor", max_results: int = 50) -> list[dict]:
    from leads.li_session import voyager_get

    leads: list[dict] = []
    start = 0
    per_page = 10

    while len(leads) < max_results:
        data = voyager_get(
            "search/blended",
            params={
                "keywords": f"{query} {location}",
                "origin": "GLOBAL_SEARCH_HEADER",
                "q": "all",
                "filters": "List(resultType->PEOPLE)",
                "count": per_page,
                "start": start,
            },
        )

        hits = _extract_hits(data)
        if not hits:
            break

        for hit in hits:
            lead = _build_lead(hit, location)
            if lead:
                leads.append(lead)
            if len(leads) >= max_results:
                return leads

        if len(hits) < per_page:
            break

        start += per_page
        time.sleep(random.uniform(3, 8))

    return leads


def _extract_hits(data: dict) -> list[dict]:
    hits: list[dict] = []
    for group in data.get("data", {}).get("elements", []):
        for element in group.get("elements", []):
            hits.append(element)
    return hits


def _build_lead(hit: dict, location: str) -> dict | None:
    target_urn = hit.get("targetUrn", "")
    member_id = _parse_member_id(target_urn)
    if not member_id:
        return None

    nav_url = hit.get("navigationUrl", "")
    public_id = _parse_public_id(nav_url)
    linkedin_url = f"https://www.linkedin.com/in/{public_id}" if public_id else nav_url

    name = ((hit.get("title") or {}).get("text") or "").strip() or "Unknown"
    headline = ((hit.get("primarySubtitle") or {}).get("text") or "").strip()

    phone = None
    if public_id:
        phone = _get_phone(public_id)
        time.sleep(random.uniform(1, 3))

    return {
        "place_id": f"li_{member_id}",
        "name": name,
        "phone": phone,
        "website": None,
        "city": location,
        "review_count": 0,
        "rating": 0.0,
        "source": "linkedin",
        "linkedin_url": linkedin_url,
        "_headline": headline,
    }


def _get_phone(public_id: str) -> str | None:
    try:
        from leads.li_session import voyager_get
        data = voyager_get(f"identity/profiles/{public_id}/profileContactInfo")
        phones = (data.get("data") or {}).get("phoneNumbers") or []
        if phones:
            return phones[0].get("number")
    except Exception:
        pass
    return None


def _parse_member_id(urn: str) -> str | None:
    m = re.search(r":member:(\d+)", urn)
    if m:
        return m.group(1)
    m = re.search(r":fsd_profile:([A-Za-z0-9_-]+)", urn)
    if m:
        return m.group(1)
    return None


def _parse_public_id(url: str) -> str | None:
    m = re.search(r"linkedin\.com/in/([^/?#]+)", url)
    return m.group(1) if m else None
