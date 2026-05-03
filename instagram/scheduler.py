#!/usr/bin/env python3
"""Run the Instagram prompt generator every hour using APScheduler."""

import logging
from pathlib import Path

from apscheduler.schedulers.blocking import BlockingScheduler
from rich.console import Console

from instagram.prompt_generator import generate_batch, save_prompts

console = Console()
logging.basicConfig(level=logging.WARNING)

OUTPUT_DIR = Path(__file__).parent / "output"


def job():
    prompts = generate_batch(10)
    filepath = save_prompts(prompts, OUTPUT_DIR)
    console.print(f"\n[bold cyan]--- Hourly batch ({len(prompts)} prompts) ---[/bold cyan]")
    for p in prompts:
        console.print(f"  [yellow][{p['number']:02d}] {p['type']} — {p['niche']}[/yellow]")
        console.print(f"       {p['prompt']}")
    console.print(f"\n[green]Saved →[/green] {filepath}\n")


if __name__ == "__main__":
    console.print("[bold]Instagram Prompt Scheduler — running every hour[/bold]")
    console.print("[dim]Press Ctrl+C to stop.[/dim]\n")

    # Run immediately on startup, then every hour
    job()

    scheduler = BlockingScheduler()
    scheduler.add_job(job, "interval", hours=1, id="instagram_prompts")
    scheduler.start()
