from apscheduler.schedulers.background import BackgroundScheduler

from config import FOLLOWUP_INTERVAL_MINUTES
from db.database import get_conn
from outreach.scheduler import process_due
from outreach.webhook import app as webhook_app


def _run_followups() -> None:
    conn = get_conn()
    sent, failed = process_due(conn)
    if sent or failed:
        print(f"[followup] sent={sent} failed={failed}")


def run(host: str, port: int) -> None:
    """Run the inbound webhook server plus a background job that sends due
    follow-ups every FOLLOWUP_INTERVAL_MINUTES. Runs until interrupted."""
    scheduler = BackgroundScheduler()
    scheduler.add_job(_run_followups, "interval", minutes=FOLLOWUP_INTERVAL_MINUTES)
    scheduler.start()
    try:
        webhook_app.run(host=host, port=port)
    finally:
        scheduler.shutdown()
