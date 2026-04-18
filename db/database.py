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
    conn.commit()


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
