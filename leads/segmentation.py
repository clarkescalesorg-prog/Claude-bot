import sqlite3
from db.database import fetch_leads, get_conn


def assign_tiers(conn: sqlite3.Connection) -> dict[str, int]:
    leads = fetch_leads(conn)
    counts = {"hot": 0, "warm": 0, "cold": 0}

    for lead in leads:
        tier = _tier_for(lead["website_score"])
        conn.execute(
            "UPDATE leads SET tier=?, updated_at=datetime('now') WHERE id=?",
            (tier, lead["id"]),
        )
        counts[tier] += 1

    conn.commit()
    return counts


def _tier_for(website_score) -> str:
    """Tier by website quality — worst sites are the best prospects."""
    if website_score is None or website_score == 0:
        return "hot"   # no website at all
    if website_score == 1:
        return "warm"  # site exists but is poor quality
    return "cold"      # site looks adequate
