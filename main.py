#!/usr/bin/env python3
import click
from rich.console import Console

console = Console()


@click.group()
def cli():
    """Roofer Outreach Bot — find UK roofers, segment by reviews, send SMS/WhatsApp."""


@cli.command()
@click.option("--city", required=True, help="UK city to search (e.g. 'Manchester')")
@click.option("--max", "max_results", default=60, show_default=True, help="Max leads to fetch")
def fetch(city: str, max_results: int):
    """Fetch roofer leads from Google Places API."""
    from db.database import get_conn, upsert_lead
    from leads.google_places import fetch_roofers

    conn = get_conn()
    console.print(f"[cyan]Searching for roofers in {city}...[/cyan]")

    leads = fetch_roofers(city, max_results)
    new = 0
    for lead in leads:
        lead["city"] = lead.get("city") or city
        upsert_lead(conn, lead)
        new += 1
        console.print(f"  [green]+[/green] {lead['name']} ({lead['review_count']} reviews)")

    console.print(f"\n[bold green]Done.[/bold green] Imported {new} leads from {city}.")


@cli.command()
def segment():
    """Score and assign tiers (hot/warm/cold) to all leads based on review count."""
    from db.database import get_conn
    from leads.segmentation import assign_tiers

    conn = get_conn()
    counts = assign_tiers(conn)
    console.print("[bold]Segmentation complete:[/bold]")
    console.print(f"  [red]Hot[/red]  (50+ reviews): {counts['hot']}")
    console.print(f"  [yellow]Warm[/yellow] (20-49 reviews): {counts['warm']}")
    console.print(f"  [blue]Cold[/blue] (<20 reviews):  {counts['cold']}")


@cli.command()
@click.option("--tier", default="hot", type=click.Choice(["hot", "warm", "cold"]), show_default=True)
@click.option("--dry-run", is_flag=True, help="Print messages without sending")
def outreach(tier: str, dry_run: bool):
    """Queue and send initial outreach to leads in a given tier."""
    from db.database import fetch_leads, get_conn
    from outreach.scheduler import process_due, queue_outreach

    conn = get_conn()
    leads = fetch_leads(conn, tier=tier, status="new")

    if not leads:
        console.print(f"[yellow]No new {tier} leads to contact.[/yellow]")
        return

    console.print(f"[cyan]Queueing outreach for {len(leads)} {tier} leads...[/cyan]")
    for lead in leads:
        queue_outreach(conn, lead)

    sent, failed = process_due(conn, dry_run=dry_run)
    label = "[DRY RUN] " if dry_run else ""
    console.print(f"\n[bold]{label}Sent: {sent}  Failed: {failed}[/bold]")


@cli.command()
@click.option("--dry-run", is_flag=True, help="Print messages without sending")
def followup(dry_run: bool):
    """Process all due follow-up messages (steps 2 and 3)."""
    from db.database import get_conn
    from outreach.scheduler import process_due

    conn = get_conn()
    sent, failed = process_due(conn, dry_run=dry_run)
    label = "[DRY RUN] " if dry_run else ""
    console.print(f"[bold]{label}Follow-ups — Sent: {sent}  Failed: {failed}[/bold]")


@cli.command()
def status():
    """Show the full pipeline dashboard."""
    from db.database import get_conn
    from reports.dashboard import show_pipeline

    conn = get_conn()
    show_pipeline(conn)


@cli.command()
@click.option("--host", default="0.0.0.0", show_default=True)
@click.option("--port", default=5000, show_default=True)
def serve(host: str, port: int):
    """Run the inbound webhook server that catches SMS/WhatsApp replies (incl. STOP opt-outs)."""
    from outreach.webhook import app as webhook_app

    console.print(f"[cyan]Starting webhook server on {host}:{port}...[/cyan]")
    console.print("[dim]Point your Twilio number's messaging webhook to POST https://<your-domain>/sms[/dim]")
    webhook_app.run(host=host, port=port)


@cli.command()
@click.option("--host", default="0.0.0.0", show_default=True)
@click.option("--port", default=5000, show_default=True)
def daemon(host: str, port: int):
    """Run unattended: inbound reply webhook + scheduled follow-up sends, until interrupted."""
    from config import FOLLOWUP_INTERVAL_MINUTES, SEND_HOUR_END, SEND_HOUR_START
    from outreach.daemon import run

    console.print(f"[cyan]Starting daemon on {host}:{port}...[/cyan]")
    console.print(f"[dim]Follow-ups checked every {FOLLOWUP_INTERVAL_MINUTES} min, "
                   f"sent only between {SEND_HOUR_START}:00-{SEND_HOUR_END}:00.[/dim]")
    console.print("[dim]Point your Twilio number's messaging webhook to POST https://<your-domain>/sms[/dim]")
    run(host, port)


@cli.command()
@click.argument("lead_id", type=int)
@click.argument("new_status", type=click.Choice(["new", "contacted", "replied", "booked", "rejected", "unsubscribed"]))
def update(lead_id: int, new_status: str):
    """Manually update a lead's status (e.g. when they reply or book)."""
    from db.database import get_conn, update_lead_status

    conn = get_conn()
    update_lead_status(conn, lead_id, new_status)
    console.print(f"[green]Lead {lead_id} updated to '{new_status}'.[/green]")


if __name__ == "__main__":
    cli()
