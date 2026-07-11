from db.database import get_conn, upsert_lead


def test_upsert_lead_update_returns_correct_id_even_after_other_inserts():
    conn = get_conn()

    lead_a_id = upsert_lead(conn, {
        "place_id": "place-regress-a",
        "name": "Regress A Roofing",
        "phone": "+441111111500",
        "website": "",
        "city": "Derby",
        "review_count": 10,
        "rating": 4.0,
    })

    # A different lead's insert bumps the connection's most-recent-insert
    # rowid to something unrelated to lead A.
    upsert_lead(conn, {
        "place_id": "place-regress-b",
        "name": "Regress B Roofing",
        "phone": "+441111111501",
        "website": "",
        "city": "Derby",
        "review_count": 10,
        "rating": 4.0,
    })

    # Re-upserting lead A hits the ON CONFLICT DO UPDATE branch (no new
    # insert). It must still return A's id, not a stale lastrowid left over
    # from lead B's insert.
    updated_id = upsert_lead(conn, {
        "place_id": "place-regress-a",
        "name": "Regress A Roofing Updated",
        "phone": "+441111111500",
        "website": "",
        "city": "Derby",
        "review_count": 25,
        "rating": 4.5,
    })

    assert updated_id == lead_a_id
    row = conn.execute("SELECT name, review_count FROM leads WHERE id=?", (lead_a_id,)).fetchone()
    assert row["name"] == "Regress A Roofing Updated"
    assert row["review_count"] == 25
