import os
import tempfile

_db_fd, _db_path = tempfile.mkstemp(suffix=".db")
os.close(_db_fd)

os.environ.setdefault("GOOGLE_PLACES_API_KEY", "test-key")
os.environ.setdefault("TWILIO_ACCOUNT_SID", "ACtest")
os.environ.setdefault("TWILIO_AUTH_TOKEN", "test-token")
os.environ.setdefault("TWILIO_FROM_NUMBER", "+441234567890")
os.environ.setdefault("DB_PATH", _db_path)
