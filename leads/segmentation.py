import sqlite3
from db.database import fetch_leads, get_conn


def assign_tiers(conn: sqlite3.Connection) -> dict[str, int]:
    leads = fetch_leads(conn)
    counts = {"hot": 0, "warm": 0, "cold": 0}

    for lead in leads:
        tier = _tier_for(lead["review_count"])
        conn.execute(
            "UPDATE leads SET tier=?, updated_at=datetime('now') WHERE id=?",
            (tier, lead["id"]),
        )
        counts[tier] += 1

    conn.commit()
    return counts


def _tier_for(review_count: int) -> str:
    if review_count >= 50:
        return "hot"
    if review_count >= 20:
        return "warm"
    return "cold"
