import csv
import sqlite3
from pathlib import Path

COLUMNS = [
    "name", "city", "phone", "website",
    "review_count", "rating",
    "fb_page_url", "fb_username", "fb_category",
    "fb_fan_count", "fb_rating", "fb_rating_count", "fb_verified",
    "fb_is_active", "fb_last_post_at",
]


def write_csv(rows: list[sqlite3.Row], path: Path) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({c: row[c] for c in COLUMNS})
    return len(rows)
