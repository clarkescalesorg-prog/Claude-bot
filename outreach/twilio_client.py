import time

from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER, OUTREACH_CHANNEL

_client: Client | None = None
_RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}
_RETRY_BACKOFF_SECONDS = 2


def _get_client() -> Client:
    global _client
    if _client is None:
        _client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    return _client


def send(to: str, body: str, *, _allow_retry: bool = True) -> str:
    """Send SMS or WhatsApp message. Returns the Twilio message SID.

    Retries once after a short backoff on transient (429/5xx) Twilio errors —
    anything else (bad number, unsubscribed, etc.) fails immediately.
    """
    client = _get_client()

    from_number = TWILIO_FROM_NUMBER
    to_number = to

    if OUTREACH_CHANNEL == "whatsapp":
        if not from_number.startswith("whatsapp:"):
            from_number = f"whatsapp:{from_number}"
        if not to_number.startswith("whatsapp:"):
            to_number = f"whatsapp:{to_number}"

    try:
        message = client.messages.create(body=body, from_=from_number, to=to_number)
        return message.sid
    except TwilioRestException as exc:
        if _allow_retry and exc.status in _RETRYABLE_STATUS_CODES:
            time.sleep(_RETRY_BACKOFF_SECONDS)
            return send(to, body, _allow_retry=False)
        raise
