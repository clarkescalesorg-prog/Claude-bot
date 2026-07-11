from datetime import datetime, timedelta

from twilio.base.exceptions import TwilioRestException

import outreach.scheduler as scheduler_module
from db.database import get_conn, log_message, upsert_lead
from outreach.scheduler import within_sending_window


def test_within_window_during_business_hours():
    assert within_sending_window(datetime(2026, 7, 11, 12, 0)) is True


def test_outside_window_before_start_hour():
    assert within_sending_window(datetime(2026, 7, 11, 8, 59)) is False


def test_outside_window_at_end_hour():
    assert within_sending_window(datetime(2026, 7, 11, 18, 0)) is False


def test_just_inside_start_hour():
    assert within_sending_window(datetime(2026, 7, 11, 9, 0)) is True


def _due_lead_with_message(conn):
    lead_id = upsert_lead(conn, {
        "place_id": "place-window-1",
        "name": "Window Roofing",
        "phone": "+441111111199",
        "website": "",
        "city": "York",
        "review_count": 55,
        "rating": 4.9,
    })
    due = (datetime.utcnow() - timedelta(minutes=1)).isoformat(sep=" ", timespec="seconds")
    log_message(conn, lead_id, 1, "sms", "hello", due)
    return lead_id


def test_process_due_skips_send_outside_window(monkeypatch):
    conn = get_conn()
    lead_id = _due_lead_with_message(conn)

    monkeypatch.setattr(scheduler_module, "within_sending_window", lambda now=None: False)

    sent, failed = scheduler_module.process_due(conn)

    assert (sent, failed) == (0, 0)
    row = conn.execute("SELECT status FROM messages WHERE lead_id=?", (lead_id,)).fetchone()
    assert row["status"] == "pending"


def test_process_due_dry_run_ignores_window(monkeypatch, capsys):
    conn = get_conn()
    lead_id = _due_lead_with_message(conn)

    monkeypatch.setattr(scheduler_module, "within_sending_window", lambda now=None: False)

    sent, failed = scheduler_module.process_due(conn, dry_run=True)

    assert (sent, failed) == (1, 0)


def test_process_due_paces_between_multiple_sends(monkeypatch):
    conn = get_conn()
    # Clear any leftover pending messages from earlier tests so the count below is deterministic.
    conn.execute("UPDATE messages SET status='sent' WHERE status='pending'")
    conn.commit()

    due = (datetime.utcnow() - timedelta(minutes=1)).isoformat(sep=" ", timespec="seconds")
    for i, place_id in enumerate(["place-pace-1", "place-pace-2"]):
        lead_id = upsert_lead(conn, {
            "place_id": place_id,
            "name": f"Pace Roofing {i}",
            "phone": f"+44111111120{i}",
            "website": "",
            "city": "Hull",
            "review_count": 40,
            "rating": 4.5,
        })
        log_message(conn, lead_id, 1, "sms", f"hi {i}", due)

    monkeypatch.setattr(scheduler_module, "within_sending_window", lambda now=None: True)
    monkeypatch.setattr(scheduler_module, "send", lambda phone, body: "SMfake")
    sleeps = []
    monkeypatch.setattr(scheduler_module.time, "sleep", lambda seconds: sleeps.append(seconds))

    sent, failed = scheduler_module.process_due(conn)

    assert (sent, failed) == (2, 0)
    assert sleeps == [scheduler_module.SEND_DELAY_SECONDS]


def test_process_due_marks_lead_unsubscribed_on_carrier_opt_out_error(monkeypatch):
    conn = get_conn()
    lead_id = upsert_lead(conn, {
        "place_id": "place-optout-1",
        "name": "Opted Out Roofing",
        "phone": "+441111111300",
        "website": "",
        "city": "Bath",
        "review_count": 33,
        "rating": 4.2,
    })
    due = (datetime.utcnow() - timedelta(minutes=1)).isoformat(sep=" ", timespec="seconds")
    log_message(conn, lead_id, 1, "sms", "hi", due)

    err = TwilioRestException(status=400, uri="/Messages", msg="blocked", code=21610)
    monkeypatch.setattr(scheduler_module, "within_sending_window", lambda now=None: True)

    def _raise(phone, body):
        raise err

    monkeypatch.setattr(scheduler_module, "send", _raise)

    sent, failed = scheduler_module.process_due(conn)

    assert (sent, failed) == (0, 1)
    row = conn.execute("SELECT status FROM leads WHERE id=?", (lead_id,)).fetchone()
    assert row["status"] == "unsubscribed"


def test_process_due_marks_failed_without_unsubscribe_on_other_twilio_error(monkeypatch):
    conn = get_conn()
    lead_id = upsert_lead(conn, {
        "place_id": "place-other-error-1",
        "name": "Other Error Roofing",
        "phone": "+441111111301",
        "website": "",
        "city": "Bath",
        "review_count": 33,
        "rating": 4.2,
    })
    due = (datetime.utcnow() - timedelta(minutes=1)).isoformat(sep=" ", timespec="seconds")
    log_message(conn, lead_id, 1, "sms", "hi", due)

    err = TwilioRestException(status=400, uri="/Messages", msg="invalid number", code=21211)
    monkeypatch.setattr(scheduler_module, "within_sending_window", lambda now=None: True)

    def _raise(phone, body):
        raise err

    monkeypatch.setattr(scheduler_module, "send", _raise)

    sent, failed = scheduler_module.process_due(conn)

    assert (sent, failed) == (0, 1)
    row = conn.execute("SELECT status FROM leads WHERE id=?", (lead_id,)).fetchone()
    assert row["status"] == "new"
