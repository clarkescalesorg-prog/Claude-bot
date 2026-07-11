from flask import Flask, Response, abort, request
from twilio.request_validator import RequestValidator

from config import TWILIO_AUTH_TOKEN
from db.database import find_lead_by_phone, get_conn, log_reply, update_lead_status

app = Flask(__name__)

STOP_WORDS = {"stop", "unsubscribe", "cancel", "end", "quit"}
_TERMINAL_STATUSES = {"booked", "rejected", "unsubscribed"}


def _twilio_signature_valid() -> bool:
    validator = RequestValidator(TWILIO_AUTH_TOKEN)
    signature = request.headers.get("X-Twilio-Signature", "")
    return validator.validate(request.url, request.form.to_dict(), signature)


@app.route("/sms", methods=["POST"])
def inbound_sms():
    """Receive inbound SMS/WhatsApp replies from Twilio, log them, and update lead status."""
    if not _twilio_signature_valid():
        abort(403)

    from_number = request.form.get("From", "").removeprefix("whatsapp:")
    body = (request.form.get("Body") or "").strip()

    conn = get_conn()
    lead = find_lead_by_phone(conn, from_number)
    if lead:
        log_reply(conn, lead["id"], body, from_number)
        if body.lower() in STOP_WORDS:
            update_lead_status(conn, lead["id"], "unsubscribed")
        elif lead["status"] not in _TERMINAL_STATUSES:
            update_lead_status(conn, lead["id"], "replied")

    return Response("<Response></Response>", mimetype="text/xml")
