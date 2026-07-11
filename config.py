import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_PLACES_API_KEY = os.environ["GOOGLE_PLACES_API_KEY"]
TWILIO_ACCOUNT_SID = os.environ["TWILIO_ACCOUNT_SID"]
TWILIO_AUTH_TOKEN = os.environ["TWILIO_AUTH_TOKEN"]
TWILIO_FROM_NUMBER = os.environ["TWILIO_FROM_NUMBER"]
OUTREACH_CHANNEL = os.getenv("OUTREACH_CHANNEL", "sms")
YOUR_NAME = os.getenv("YOUR_NAME", "James")
DB_PATH = os.getenv("DB_PATH", "roofers.db")

# Only send outreach messages within this local-hour window (24h clock),
# so leads aren't texted late at night. Messages due outside the window
# stay pending and go out on the next run within the window.
SEND_HOUR_START = int(os.getenv("SEND_HOUR_START", "9"))
SEND_HOUR_END = int(os.getenv("SEND_HOUR_END", "18"))

# How often the `daemon` command checks for due follow-ups, in minutes.
FOLLOWUP_INTERVAL_MINUTES = int(os.getenv("FOLLOWUP_INTERVAL_MINUTES", "30"))
