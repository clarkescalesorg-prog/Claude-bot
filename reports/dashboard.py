import sqlite3
from rich.console import Console
from rich.table import Table

console = Console()


def show_pipeline(conn: sqlite3.Connection) -> None:
    _show_lead_summary(conn)
    _show_message_summary(conn)
    _show_recent_leads(conn)


def _show_lead_summary(conn: sqlite3.Connection) -> None:
    rows = conn.execute(
        """
        SELECT
            COALESCE(tier,'untiered') AS tier,
            status,
            COUNT(*) AS cnt
        FROM leads
        GROUP BY tier, status
        ORDER BY tier, status
        """
    ).fetchall()

    table = Table(title="Lead Pipeline", show_lines=True)
    table.add_column("Tier", style="bold cyan")
    table.add_column("Status", style="bold yellow")
    table.add_column("Count", justify="right")

    for row in rows:
        table.add_row(row["tier"], row["status"], str(row["cnt"]))

    console.print(table)


def _show_message_summary(conn: sqlite3.Connection) -> None:
    rows = conn.execute(
        """
        SELECT step, status, COUNT(*) AS cnt
        FROM messages
        GROUP BY step, status
        ORDER BY step, status
        """
    ).fetchall()

    table = Table(title="Message Stats", show_lines=True)
    table.add_column("Step", style="bold magenta")
    table.add_column("Status", style="bold yellow")
    table.add_column("Count", justify="right")

    for row in rows:
        table.add_row(str(row["step"]), row["status"], str(row["cnt"]))

    console.print(table)


def _show_recent_leads(conn: sqlite3.Connection) -> None:
    rows = conn.execute(
        """
        SELECT name, city, tier, review_count, status
        FROM leads
        ORDER BY created_at DESC
        LIMIT 20
        """
    ).fetchall()

    table = Table(title="Recent Leads (last 20)", show_lines=True)
    table.add_column("Business")
    table.add_column("City")
    table.add_column("Tier", style="bold cyan")
    table.add_column("Reviews", justify="right")
    table.add_column("Status", style="bold yellow")

    for row in rows:
        table.add_row(
            row["name"],
            row["city"] or "—",
            row["tier"] or "—",
            str(row["review_count"]),
            row["status"],
        )

    console.print(table)
