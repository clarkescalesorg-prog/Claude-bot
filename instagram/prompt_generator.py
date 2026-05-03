#!/usr/bin/env python3
"""Generate 10 Instagram post prompts for a marketing agency and save to file."""

import random
from datetime import datetime
from pathlib import Path

NICHES = [
    "roofing", "plumbing", "electrical", "landscaping", "painting",
    "HVAC", "cleaning", "construction", "carpentry", "fencing",
]

POST_TYPES = [
    "before_after",
    "tip",
    "testimonial",
    "behind_the_scenes",
    "promotion",
    "educational",
    "seasonal",
    "myth_busting",
    "faq",
    "social_proof",
]

TEMPLATES = {
    "before_after": [
        "Post a before-and-after photo of a {niche} job. Caption: 'From {problem} to perfect. Swipe to see the transformation. DM us to book your free quote.'",
        "Share a dramatic before-and-after reel for a {niche} project. Use trending audio. Caption: 'This is what we do. Tag someone whose home needs this.'",
        "Carousel: 3 before photos followed by 3 after photos from a {niche} job. Caption: 'Results speak louder than words. Link in bio to get started.'",
    ],
    "tip": [
        "Share '3 signs your {niche} needs attention this season'. Use a bold graphic with each tip. End caption with: 'Save this post for later!'",
        "Post a quick video tip: 'How to spot a {niche} problem before it becomes expensive'. Caption: 'Follow us for weekly homeowner tips.'",
        "Infographic: '5 things every homeowner should know about {niche}'. Caption: 'Which one surprised you? Comment below.'",
    ],
    "testimonial": [
        "Share a customer review screenshot with a branded graphic overlay. Caption: 'Another happy client sorted. Read more reviews at [link in bio].'",
        "Post a short video testimonial from a {niche} client. Caption: '{quote}. This is why we do what we do.'",
        "Graphic: Big quote from a 5-star {niche} review. Caption: 'We let our work — and our clients — do the talking.'",
    ],
    "behind_the_scenes": [
        "Time-lapse reel of your team completing a {niche} job from start to finish. Caption: 'A day in the life. Every job, done right.'",
        "Photo of your team on-site for a {niche} project. Caption: 'Meet the crew behind the results. Tag a tradesperson you respect.'",
        "Short clip of your morning team briefing or van loading. Caption: 'Early starts, great results. What are you working on today?'",
    ],
    "promotion": [
        "Limited-time offer graphic: '10% off all {niche} bookings this month'. Caption: 'DM us NOW to lock in your discount. Spots are limited.'",
        "Seasonal promotion: 'Get your {niche} sorted before winter. Book this week and save.' Use urgency-driven graphic.",
        "Referral offer post: 'Refer a friend and both of you save £50 on your next {niche} job.' Bright, shareable graphic.",
    ],
    "educational": [
        "Carousel: 'How much does {niche} actually cost in the UK?' Break down realistic price ranges. Caption: 'Save this before you get any quotes.'",
        "Reel: 'What to expect when hiring a {niche} contractor — step by step'. Caption: 'First time? This is for you. Follow for more homeowner guides.'",
        "Graphic: 'DIY vs Professional {niche} — the honest truth'. Caption: 'We know which one we'd choose. What about you?'",
    ],
    "seasonal": [
        "Post: 'Is your {niche} ready for {season}? Here's your checklist.' Branded graphic with 5 action items. Caption: 'Save this and tick them off!'",
        "Reel: '{season} is coming — here's what {niche} problems to watch out for.' Caption: 'React with a ❤️ if you found this useful.'",
        "Infographic: 'Best time of year to book {niche} work — and why.' Caption: 'Planning ahead saves you money. Follow us for more tips.'",
    ],
    "myth_busting": [
        "Graphic: 'MYTH: {niche} work is always expensive. FACT: Catching problems early saves thousands.' Caption: 'Drop a 🔥 if you didn't know this.'",
        "Carousel: '5 {niche} myths — busted.' Bold myth on each slide followed by the truth. Caption: 'Which one did you believe? Be honest.'",
        "Reel: 'We need to talk about this {niche} myth...' Hook viewers in the first 3 seconds. Caption: 'Share this with someone who needs to hear it.'",
    ],
    "faq": [
        "Post answering 'How long does a typical {niche} job take?' with a clear, simple graphic. Caption: 'Got more questions? Drop them below.'",
        "Reel: Quick-fire FAQ — answer 5 common {niche} questions in under 60 seconds. Caption: 'Follow us so you never miss another tip like this.'",
        "Carousel: 'Your top {niche} questions, answered.' One question per slide. Caption: 'Save this for when you need it.'",
    ],
    "social_proof": [
        "Post your total number of completed {niche} jobs as a bold graphic. Caption: 'X jobs completed. Zero shortcuts taken. DM us to be next.'",
        "Share a stat: '98% of our {niche} clients would recommend us.' Caption: 'We earn that every single day. Link in bio to book.'",
        "Before/after collage of your best {niche} jobs this month. Caption: 'Our best work from this month. Which one is your favourite?'",
    ],
}

SEASONS = ["winter", "spring", "summer", "autumn"]
PROBLEMS = {
    "roofing": "leaks and missing tiles",
    "plumbing": "drips and blockages",
    "electrical": "outdated wiring",
    "landscaping": "overgrown chaos",
    "painting": "peeling and faded walls",
    "HVAC": "inefficient heating",
    "cleaning": "years of grime",
    "construction": "structural issues",
    "carpentry": "damaged woodwork",
    "fencing": "rotten panels",
}


def generate_prompt(post_type: str, niche: str) -> str:
    template = random.choice(TEMPLATES[post_type])
    season = random.choice(SEASONS)
    problem = PROBLEMS.get(niche, "common problems")
    quote = "From the first call to the final clean-up, absolutely faultless"
    return template.format(niche=niche, season=season, problem=problem, quote=quote)


def generate_batch(count: int = 10) -> list[dict]:
    prompts = []
    used = set()
    attempts = 0
    while len(prompts) < count and attempts < count * 5:
        attempts += 1
        post_type = random.choice(POST_TYPES)
        niche = random.choice(NICHES)
        key = (post_type, niche)
        if key in used:
            continue
        used.add(key)
        prompts.append({
            "number": len(prompts) + 1,
            "type": post_type.replace("_", " ").title(),
            "niche": niche.title(),
            "prompt": generate_prompt(post_type, niche),
        })
    return prompts


def save_prompts(prompts: list[dict], output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    filepath = output_dir / f"instagram_prompts_{timestamp}.txt"
    lines = [
        f"Instagram Post Prompts — {datetime.now().strftime('%d %b %Y %H:%M')}",
        "=" * 60,
        "",
    ]
    for p in prompts:
        lines += [
            f"[{p['number']:02d}] {p['type']} — {p['niche']}",
            f"     {p['prompt']}",
            "",
        ]
    filepath.write_text("\n".join(lines))
    return filepath


def main():
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text

    console = Console()
    output_dir = Path(__file__).parent / "output"

    prompts = generate_batch(10)
    filepath = save_prompts(prompts, output_dir)

    console.print(Panel("[bold cyan]Instagram Post Prompts — Marketing Agency[/bold cyan]", expand=False))
    for p in prompts:
        console.print(f"\n[bold yellow][{p['number']:02d}] {p['type']} — {p['niche']}[/bold yellow]")
        console.print(f"     {p['prompt']}")

    console.print(f"\n[green]Saved {len(prompts)} prompts to:[/green] {filepath}")


if __name__ == "__main__":
    main()
