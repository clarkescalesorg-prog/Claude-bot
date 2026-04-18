import sqlite3
import os
from pathlib import Path

_conn: sqlite3.Connection | None = None


def get_conn(db_path: str = None) -> sqlite3.Connection:
    global _conn
    if _conn is None:
        if db_path is None:
            from config import DB_PATH
            db_path = DB_PATH
        _conn = sqlite3.connect(db_path, check_same_thread=False)
        _conn.row_factory = sqlite3.Row
        _conn.execute("PRAGMA journal_mode=WAL")
        _init_schema(_conn)
    return _conn


def _init_schema(conn: sqlite3.Connection) -> None:
    schema_path = Path(__file__).parent / "schema.sql"
    conn.executescript(schema_path.read_text())
    _migrate(conn)
    conn.commit()


_LEAD_COLUMNS: list[tuple[str, str]] = [
    ("fb_page_id", "TEXT"),
    ("fb_page_url", "TEXT"),
    ("fb_username", "TEXT"),
    ("fb_category", "TEXT"),
    ("fb_fan_count", "INTEGER"),
    ("fb_rating", "REAL"),
    ("fb_rating_count", "INTEGER"),
    ("fb_verified", "TEXT"),
    ("fb_is_active", "INTEGER"),
    ("fb_last_post_at", "TEXT"),
    ("fb_checked_at", "TEXT"),
]


def _migrate(conn: sqlite3.Connection) -> None:
    existing = {row["name"] for row in conn.execute("PRAGMA table_info(leads)")}
    for col, col_type in _LEAD_COLUMNS:
        if col not in existing:
            conn.execute(f"ALTER TABLE leads ADD COLUMN {col} {col_type}")


def upsert_lead(conn: sqlite3.Connection, lead: dict) -> int:
    cur = conn.execute(
        """
        INSERT INTO leads (place_id, name, phone, website, city, review_count, rating)
        VALUES (:place_id, :name, :phone, :website, :city, :review_count, :rating)
        ON CONFLICT(place_id) DO UPDATE SET
            name         = excluded.name,
            phone        = excluded.phone,
            website      = excluded.website,
            review_count = excluded.review_count,
            rating       = excluded.rating,
            updated_at   = datetime('now')
        """,
        lead,
    )
    conn.commit()
    if cur.lastrowid:
        return cur.lastrowid
    row = conn.execute("SELECT id FROM leads WHERE place_id = ?", (lead["place_id"],)).fetchone()
    return row["id"]


def fetch_leads(conn: sqlite3.Connection, tier: str = None, status: str = None) -> list[sqlite3.Row]:
    query = "SELECT * FROM leads WHERE 1=1"
    params: list = []
    if tier:
        query += " AND tier = ?"
        params.append(tier)
    if status:
        query += " AND status = ?"
        params.append(status)
    query += " ORDER BY review_count DESC"
    return conn.execute(query, params).fetchall()


def log_message(conn: sqlite3.Connection, lead_id: int, step: int, channel: str, body: str, due_at: str) -> None:
    conn.execute(
        """
        INSERT OR IGNORE INTO messages (lead_id, step, channel, body, due_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (lead_id, step, channel, body, due_at),
    )
    conn.commit()


def fetch_due_messages(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute(
        """
        SELECT m.*, l.name, l.phone, l.city
        FROM messages m
        JOIN leads l ON l.id = m.lead_id
        WHERE m.status = 'pending'
          AND m.due_at <= datetime('now')
          AND l.status NOT IN ('rejected','unsubscribed')
        ORDER BY m.due_at
        """
    ).fetchall()


def mark_message_sent(conn: sqlite3.Connection, message_id: int, twilio_sid: str) -> None:
    conn.execute(
        "UPDATE messages SET status='sent', twilio_sid=?, sent_at=datetime('now') WHERE id=?",
        (twilio_sid, message_id),
    )
    conn.commit()


def mark_message_failed(conn: sqlite3.Connection, message_id: int) -> None:
    conn.execute("UPDATE messages SET status='failed' WHERE id=?", (message_id,))
    conn.commit()


def update_lead_status(conn: sqlite3.Connection, lead_id: int, status: str) -> None:
    conn.execute(
        "UPDATE leads SET status=?, updated_at=datetime('now') WHERE id=?",
        (status, lead_id),
    )
    conn.commit()


def update_fb_enrichment(conn: sqlite3.Connection, lead_id: int, fb: dict) -> None:
    conn.execute(
        """
        UPDATE leads SET
            fb_page_id      = :fb_page_id,
            fb_page_url     = :fb_page_url,
            fb_username     = :fb_username,
            fb_category     = :fb_category,
            fb_fan_count    = :fb_fan_count,
            fb_rating       = :fb_rating,
            fb_rating_count = :fb_rating_count,
            fb_verified     = :fb_verified,
            fb_is_active    = :fb_is_active,
            fb_last_post_at = :fb_last_post_at,
            fb_checked_at   = datetime('now'),
            updated_at      = datetime('now')
        WHERE id = :id
        """,
        {"id": lead_id, **fb},
    )
    conn.commit()


def fetch_fb_leads(
    conn: sqlite3.Connection,
    active_only: bool = True,
    min_fans: int = 0,
) -> list[sqlite3.Row]:
    query = "SELECT * FROM leads WHERE fb_page_id IS NOT NULL"
    params: list = []
    if active_only:
        query += " AND COALESCE(fb_is_active, 0) = 1"
    if min_fans:
        query += " AND COALESCE(fb_fan_count, 0) >= ?"
        params.append(min_fans)
    query += " ORDER BY fb_fan_count DESC"
    return conn.execute(query, params).fetchall()


def fetch_leads_missing_fb(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM leads WHERE fb_checked_at IS NULL AND website IS NOT NULL AND website != ''"
    ).fetchall()
