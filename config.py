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

# Facebook Graph API — app token (format: "{app_id}|{app_secret}") gives access
# to public Page fields. Leave unset to skip enrichment.
FACEBOOK_GRAPH_TOKEN = os.getenv("FACEBOOK_GRAPH_TOKEN", "")
FACEBOOK_GRAPH_VERSION = os.getenv("FACEBOOK_GRAPH_VERSION", "v21.0")
