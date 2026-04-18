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
@click.argument("lead_id", type=int)
@click.argument("new_status", type=click.Choice(["new", "contacted", "replied", "booked", "rejected", "unsubscribed"]))
def update(lead_id: int, new_status: str):
    """Manually update a lead's status (e.g. when they reply or book)."""
    from db.database import get_conn, update_lead_status

    conn = get_conn()
    update_lead_status(conn, lead_id, new_status)
    console.print(f"[green]Lead {lead_id} updated to '{new_status}'.[/green]")


@cli.command("enrich-fb")
def enrich_fb():
    """Find each lead's public Facebook Page via their website and store public metadata."""
    from db.database import fetch_leads_missing_fb, get_conn, update_fb_enrichment
    from leads.facebook_pages import enrich

    conn = get_conn()
    leads = fetch_leads_missing_fb(conn)
    if not leads:
        console.print("[yellow]No leads need Facebook enrichment.[/yellow]")
        return

    console.print(f"[cyan]Enriching {len(leads)} leads from Facebook Graph API...[/cyan]")
    found = 0
    for lead in leads:
        fb = enrich(lead["website"])
        if fb is None:
            fb = {k: None for k in (
                "fb_page_id", "fb_page_url", "fb_username", "fb_category",
                "fb_fan_count", "fb_rating", "fb_rating_count", "fb_verified",
                "fb_is_active", "fb_last_post_at",
            )}
        else:
            found += 1
            console.print(
                f"  [green]+[/green] {lead['name']}: {fb['fb_username']} "
                f"({fb['fb_fan_count'] or 0} fans, active={bool(fb['fb_is_active'])})"
            )
        update_fb_enrichment(conn, lead["id"], fb)

    console.print(f"\n[bold green]Done.[/bold green] Matched {found}/{len(leads)} to a Facebook Page.")


@cli.command("export-fb")
@click.option("--out", "out_path", default="leads_facebook.csv", show_default=True, help="CSV output path")
@click.option("--min-fans", default=500, show_default=True, help="Minimum fan count")
@click.option("--include-inactive", is_flag=True, help="Include Pages with no recent posts")
def export_fb(out_path: str, min_fans: int, include_inactive: bool):
    """Export leads with a matched, active, high-fan Facebook Page to CSV."""
    from pathlib import Path

    from db.database import fetch_fb_leads, get_conn
    from leads.csv_export import write_csv

    conn = get_conn()
    rows = fetch_fb_leads(conn, active_only=not include_inactive, min_fans=min_fans)
    if not rows:
        console.print("[yellow]No leads match. Run `enrich-fb` first or lower --min-fans.[/yellow]")
        return

    n = write_csv(rows, Path(out_path))
    console.print(f"[bold green]Wrote {n} leads[/bold green] to [cyan]{out_path}[/cyan]")


if __name__ == "__main__":
    cli()
