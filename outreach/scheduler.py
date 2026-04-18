import sqlite3
from datetime import datetime, timedelta

from config import OUTREACH_CHANNEL
from db.database import (
    fetch_due_messages,
    log_message,
    mark_message_failed,
    mark_message_sent,
    update_lead_status,
)
from outreach.messages import render
from outreach.twilio_client import send

FOLLOW_UP_DAYS = {1: 0, 2: 3, 3: 7}


def queue_outreach(conn: sqlite3.Connection, lead: sqlite3.Row) -> None:
    """Queue all 3 message steps for a lead, spaced by FOLLOW_UP_DAYS."""
    now = datetime.utcnow()
    for step, day_offset in FOLLOW_UP_DAYS.items():
        due = now + timedelta(days=day_offset)
        body = render(
            step,
            lead["name"],
            lead["city"],
            has_website=lead["has_website"],
            web_score=lead["web_score"],
        )
        log_message(conn, lead["id"], step, OUTREACH_CHANNEL, body, due.isoformat(sep=" ", timespec="seconds"))

    update_lead_status(conn, lead["id"], "contacted")


def process_due(conn: sqlite3.Connection, dry_run: bool = False) -> tuple[int, int]:
    """Send all due messages. Returns (sent, failed) counts."""
    due = fetch_due_messages(conn)
    sent = failed = 0

    for msg in due:
        phone = msg["phone"]
        if not phone:
            mark_message_failed(conn, msg["id"])
            failed += 1
            continue

        if dry_run:
            print(f"[DRY RUN] → {phone} (step {msg['step']})\n{msg['body']}\n")
            sent += 1
            continue

        try:
            sid = send(phone, msg["body"])
            mark_message_sent(conn, msg["id"], sid)
            sent += 1
        except Exception as exc:
            print(f"Failed to send to {phone}: {exc}")
            mark_message_failed(conn, msg["id"])
            failed += 1

    return sent, failed
