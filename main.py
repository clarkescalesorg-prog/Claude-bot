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


@cli.command(name="linkedin-hunt")
@click.option("--location", required=True, help="City or region (e.g. 'Manchester, UK')")
@click.option("--query", default="roofing contractor", show_default=True, help="Search keywords")
@click.option("--max", "max_results", default=50, show_default=True, help="Max prospects to import")
@click.option("--dry-run", is_flag=True, help="Print prospects without writing to database")
def linkedin_hunt(location: str, query: str, max_results: int, dry_run: bool):
    """Find LinkedIn prospects and import into the lead pipeline."""
    from leads.linkedin_hunter import search_prospects
    from db.database import get_conn, upsert_linkedin_lead
    from rich.table import Table

    console.print(f"[cyan]Searching LinkedIn for '{query}' in {location}...[/cyan]")
    prospects = search_prospects(location=location, query=query, max_results=max_results)

    if not prospects:
        console.print("[yellow]No prospects found.[/yellow]")
        return

    if dry_run:
        table = Table(title=f"LinkedIn Prospects — {location} (dry run)", show_lines=True)
        table.add_column("Name")
        table.add_column("Headline")
        table.add_column("Phone")
        table.add_column("LinkedIn URL")
        for p in prospects:
            table.add_row(
                p["name"],
                p.get("_headline") or "",
                p.get("phone") or "[dim]—[/dim]",
                p.get("linkedin_url") or "",
            )
        console.print(table)
        console.print(f"[dim]Would import {len(prospects)} prospects.[/dim]")
        return

    conn = get_conn()
    added = 0
    for p in prospects:
        p.pop("_headline", None)
        upsert_linkedin_lead(conn, p)
        added += 1
        icon = "[green]+[/green]" if p.get("phone") else "[yellow]~[/yellow]"
        console.print(f"  {icon} {p['name']} — {p.get('linkedin_url', '')}")

    console.print(f"\n[bold green]Done.[/bold green] Imported {added} LinkedIn prospects from {location}.")


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
