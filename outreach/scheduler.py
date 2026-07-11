import sqlite3
import time
from datetime import datetime, timedelta

from config import OUTREACH_CHANNEL, SEND_DELAY_SECONDS, SEND_HOUR_END, SEND_HOUR_START
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


def within_sending_window(now: datetime | None = None) -> bool:
    """Whether it's currently an acceptable local time to send outreach messages."""
    now = now or datetime.now()
    return SEND_HOUR_START <= now.hour < SEND_HOUR_END


def queue_outreach(conn: sqlite3.Connection, lead: sqlite3.Row) -> None:
    """Queue all 3 message steps for a lead, spaced by FOLLOW_UP_DAYS."""
    now = datetime.utcnow()
    for step, day_offset in FOLLOW_UP_DAYS.items():
        due = now + timedelta(days=day_offset)
        body = render(step, lead["name"], lead["city"])
        log_message(conn, lead["id"], step, OUTREACH_CHANNEL, body, due.isoformat(sep=" ", timespec="seconds"))

    update_lead_status(conn, lead["id"], "contacted")


def process_due(conn: sqlite3.Connection, dry_run: bool = False) -> tuple[int, int]:
    """Send all due messages. Returns (sent, failed) counts.

    Outside dry runs, real sends are skipped when it's outside the configured
    SEND_HOUR_START/SEND_HOUR_END window — due messages simply stay pending
    and go out on the next run within the window.
    """
    due = fetch_due_messages(conn)
    sent = failed = 0

    if due and not dry_run and not within_sending_window():
        print(f"[skip] {len(due)} message(s) due but outside sending hours "
              f"({SEND_HOUR_START}:00-{SEND_HOUR_END}:00) — will retry later.")
        return sent, failed

    for i, msg in enumerate(due):
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

        if SEND_DELAY_SECONDS > 0 and i < len(due) - 1:
            time.sleep(SEND_DELAY_SECONDS)

    return sent, failed
