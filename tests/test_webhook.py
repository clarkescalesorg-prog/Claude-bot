from twilio.request_validator import RequestValidator

from config import TWILIO_AUTH_TOKEN
from db.database import get_conn, upsert_lead
from outreach.webhook import app

_URL = "http://localhost/sms"


def _make_lead(conn, place_id: str, phone: str):
    lead = {
        "place_id": place_id,
        "name": "Acme Roofing",
        "phone": phone,
        "website": "",
        "city": "Leeds",
        "review_count": 60,
        "rating": 4.8,
    }
    return upsert_lead(conn, lead)


def _signed_post(client, params):
    signature = RequestValidator(TWILIO_AUTH_TOKEN).compute_signature(_URL, params)
    return client.post(
        "/sms",
        base_url="http://localhost",
        data=params,
        headers={"X-Twilio-Signature": signature},
    )


def test_rejects_request_with_missing_or_bad_signature():
    client = app.test_client()
    resp = client.post("/sms", data={"From": "+441234500000", "Body": "hi"})
    assert resp.status_code == 403


def test_valid_reply_marks_lead_replied():
    conn = get_conn()
    lead_id = _make_lead(conn, "place-reply-1", "+441111111111")

    resp = _signed_post(app.test_client(), {"From": "+441111111111", "Body": "Yes please call me"})

    assert resp.status_code == 200
    row = conn.execute("SELECT status FROM leads WHERE id=?", (lead_id,)).fetchone()
    assert row["status"] == "replied"

    reply = conn.execute("SELECT body FROM replies WHERE lead_id=?", (lead_id,)).fetchone()
    assert reply["body"] == "Yes please call me"


def test_stop_keyword_unsubscribes_lead():
    conn = get_conn()
    lead_id = _make_lead(conn, "place-reply-2", "+441111111112")

    resp = _signed_post(app.test_client(), {"From": "+441111111112", "Body": "STOP"})

    assert resp.status_code == 200
    row = conn.execute("SELECT status FROM leads WHERE id=?", (lead_id,)).fetchone()
    assert row["status"] == "unsubscribed"


def test_reply_from_unknown_number_is_ignored_without_error():
    resp = _signed_post(app.test_client(), {"From": "+449999999999", "Body": "hello?"})
    assert resp.status_code == 200


def test_whatsapp_prefix_is_stripped_before_lookup():
    conn = get_conn()
    lead_id = _make_lead(conn, "place-reply-3", "+441111111113")

    resp = _signed_post(app.test_client(), {"From": "whatsapp:+441111111113", "Body": "Interested"})

    assert resp.status_code == 200
    row = conn.execute("SELECT status FROM leads WHERE id=?", (lead_id,)).fetchone()
    assert row["status"] == "replied"
