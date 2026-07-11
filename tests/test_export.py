import csv
import os

from click.testing import CliRunner

from db.database import get_conn, upsert_lead
from main import cli


def test_export_writes_filtered_leads_to_csv(tmp_path):
    conn = get_conn()
    upsert_lead(conn, {
        "place_id": "place-export-hot",
        "name": "Export Hot Roofing",
        "phone": "+441111111400",
        "website": "https://example.com",
        "city": "Bristol",
        "review_count": 80,
        "rating": 4.9,
    })
    upsert_lead(conn, {
        "place_id": "place-export-cold",
        "name": "Export Cold Roofing",
        "phone": "+441111111401",
        "website": "",
        "city": "Bristol",
        "review_count": 3,
        "rating": 3.9,
    })
    conn.execute("UPDATE leads SET tier='hot' WHERE place_id='place-export-hot'")
    conn.execute("UPDATE leads SET tier='cold' WHERE place_id='place-export-cold'")
    conn.commit()

    out_path = tmp_path / "hot_leads.csv"
    result = CliRunner().invoke(cli, ["export", "--tier", "hot", "--out", str(out_path)])

    assert result.exit_code == 0
    assert os.path.exists(out_path)

    with open(out_path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    names = {row["name"] for row in rows}
    assert "Export Hot Roofing" in names
    assert "Export Cold Roofing" not in names
