import sqlite3
from db.database import fetch_leads, get_conn


def assign_tiers(conn: sqlite3.Connection) -> dict[str, int]:
    leads = fetch_leads(conn)
    counts = {"hot": 0, "warm": 0, "cold": 0}

    for lead in leads:
        tier = _tier_for(lead["review_count"], lead["web_score"], lead["has_website"])
        conn.execute(
            "UPDATE leads SET tier=?, updated_at=datetime('now') WHERE id=?",
            (tier, lead["id"]),
        )
        counts[tier] += 1

    conn.commit()
    return counts


def _tier_for(review_count: int, web_score: int | None, has_website: int | None) -> str:
    base = _base_tier(review_count)

    # No website or terrible website — upgrade one tier (cold→warm, warm→hot)
    web_is_bad = has_website == 0 or (web_score is not None and web_score < 40)
    if web_is_bad:
        if base == "cold":
            return "warm"
        return "hot"

    return base


def _base_tier(review_count: int) -> str:
    if review_count >= 50:
        return "hot"
    if review_count >= 20:
        return "warm"
    return "cold"
