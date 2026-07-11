CREATE TABLE IF NOT EXISTS leads (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    place_id    TEXT    UNIQUE NOT NULL,
    name        TEXT    NOT NULL,
    phone       TEXT,
    website     TEXT,
    city        TEXT,
    review_count INTEGER DEFAULT 0,
    rating      REAL    DEFAULT 0.0,
    tier        TEXT    CHECK(tier IN ('hot','warm','cold')) DEFAULT NULL,
    status      TEXT    CHECK(status IN ('new','contacted','replied','booked','rejected','unsubscribed')) DEFAULT 'new',
    created_at  TEXT    DEFAULT (datetime('now')),
    updated_at  TEXT    DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS messages (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    lead_id     INTEGER NOT NULL REFERENCES leads(id),
    step        INTEGER NOT NULL CHECK(step IN (1,2,3)),
    channel     TEXT    NOT NULL CHECK(channel IN ('sms','whatsapp')),
    body        TEXT    NOT NULL,
    twilio_sid  TEXT,
    status      TEXT    CHECK(status IN ('pending','sent','failed')) DEFAULT 'pending',
    due_at      TEXT    NOT NULL,
    sent_at     TEXT,
    UNIQUE(lead_id, step)
);

CREATE TABLE IF NOT EXISTS replies (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    lead_id     INTEGER NOT NULL REFERENCES leads(id),
    body        TEXT    NOT NULL,
    from_number TEXT,
    received_at TEXT    DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_messages_due ON messages(due_at, status);
CREATE INDEX IF NOT EXISTS idx_leads_tier   ON leads(tier, status);
CREATE INDEX IF NOT EXISTS idx_leads_phone  ON leads(phone);
CREATE INDEX IF NOT EXISTS idx_replies_lead ON replies(lead_id);
