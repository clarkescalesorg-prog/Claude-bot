from click.testing import CliRunner

from db.database import get_conn, upsert_lead
from main import cli


def test_outreach_dry_run_does_not_mutate_lead_or_queue_messages():
    conn = get_conn()
    lead_id = upsert_lead(conn, {
        "place_id": "place-dryrun-1",
        "name": "Dry Run Roofing",
        "phone": "+441111111600",
        "website": "",
        "city": "Leeds",
        "review_count": 60,
        "rating": 4.7,
    })
    conn.execute("UPDATE leads SET tier='hot' WHERE id=?", (lead_id,))
    conn.commit()

    result = CliRunner().invoke(cli, ["outreach", "--tier", "hot", "--dry-run"])

    assert result.exit_code == 0
    assert "Dry Run Roofing" in result.output

    row = conn.execute("SELECT status FROM leads WHERE id=?", (lead_id,)).fetchone()
    assert row["status"] == "new"

    count = conn.execute("SELECT COUNT(*) AS n FROM messages WHERE lead_id=?", (lead_id,)).fetchone()["n"]
    assert count == 0


def test_outreach_real_run_queues_and_sends(monkeypatch):
    import outreach.scheduler as scheduler_module

    conn = get_conn()
    lead_id = upsert_lead(conn, {
        "place_id": "place-realrun-1",
        "name": "Real Run Roofing",
        "phone": "+441111111601",
        "website": "",
        "city": "Leeds",
        "review_count": 60,
        "rating": 4.7,
    })
    conn.execute("UPDATE leads SET tier='hot' WHERE id=?", (lead_id,))
    conn.commit()

    monkeypatch.setattr(scheduler_module, "within_sending_window", lambda now=None: True)
    monkeypatch.setattr(scheduler_module, "send", lambda phone, body: "SMtest")

    result = CliRunner().invoke(cli, ["outreach", "--tier", "hot"])

    assert result.exit_code == 0
    row = conn.execute("SELECT status FROM leads WHERE id=?", (lead_id,)).fetchone()
    assert row["status"] == "contacted"

    count = conn.execute("SELECT COUNT(*) AS n FROM messages WHERE lead_id=?", (lead_id,)).fetchone()["n"]
    assert count == 3
