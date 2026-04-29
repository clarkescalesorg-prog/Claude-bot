"""
Eligibility checker for The UK Money-Back Pack.

Pure logic: a single function `evaluate(answers)` that takes a dict of
answers from the storefront's free checker form and returns a list of
applicable claim items, sorted by estimated value (highest first).

Used by `product/server.py` at the `/check` route.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Claim:
    slug: str
    title: str
    estimated_min_gbp: int
    estimated_max_gbp: int
    headline: str
    why_you_qualify: str
    next_step: str
    gov_uk_link: str

    @property
    def estimated_label(self) -> str:
        if self.estimated_min_gbp == self.estimated_max_gbp:
            return f"£{self.estimated_min_gbp:,}"
        return f"£{self.estimated_min_gbp:,}–£{self.estimated_max_gbp:,}"


QUESTIONS = [
    {
        "key": "married",
        "label": "Are you married or in a civil partnership?",
        "options": ["yes", "no"],
    },
    {
        "key": "spouse_low_earner",
        "label": "If yes, does one of you earn under £12,570 and the other between £12,571 and £50,270?",
        "options": ["yes", "no", "not_sure", "n/a"],
    },
    {
        "key": "sole_adult",
        "label": "Are you the only adult (18+) living at your home?",
        "options": ["yes", "no"],
    },
    {
        "key": "owns_home",
        "label": "Do you own (or are buying with a mortgage) the home you live in?",
        "options": ["yes", "no"],
    },
    {
        "key": "neighbours_lower_band",
        "label": "If yes, are at least half of nearby similar homes in a lower Council Tax band than yours?",
        "options": ["yes", "no", "not_sure", "n/a"],
    },
    {
        "key": "children_under_12",
        "label": "Do you have children under 12 in childcare or nursery?",
        "options": ["yes", "no"],
    },
    {
        "key": "over_state_pension_age",
        "label": "Are you (or a relative you help) over State Pension age (66+)?",
        "options": ["yes", "no"],
    },
    {
        "key": "pensioner_low_income",
        "label": "If yes, is their weekly income under ~£218 (single) or ~£333 (couple)?",
        "options": ["yes", "no", "not_sure", "n/a"],
    },
    {
        "key": "health_affects_daily_life",
        "label": "Does a health condition or disability affect daily life for you or someone in your household?",
        "options": ["yes", "no"],
    },
    {
        "key": "wfh_pre_2022",
        "label": "Did you work from home for any period before April 2022 (and never claimed the WFH tax relief)?",
        "options": ["yes", "no"],
    },
    {
        "key": "uniform_or_tools",
        "label": "Do you wear a branded uniform to work or buy your own tools/specialist clothing?",
        "options": ["yes", "no"],
    },
    {
        "key": "higher_rate_pension",
        "label": "Do you earn over £50,270 and pay into a personal pension (not via salary sacrifice)?",
        "options": ["yes", "no", "not_sure"],
    },
    {
        "key": "credit_card_dispute",
        "label": "Have you ever paid £100+ on a credit card for something that wasn't delivered, was faulty, or where the supplier went bust?",
        "options": ["yes", "no"],
    },
    {
        "key": "energy_credit",
        "label": "Has your energy account been in credit for 3+ months (bigger than one month's direct debit)?",
        "options": ["yes", "no", "not_sure"],
    },
    {
        "key": "packaged_account",
        "label": "Do you (or did you) pay £10+/month for a 'packaged' bank current account whose perks you didn't fully use?",
        "options": ["yes", "no"],
    },
]


def evaluate(answers: dict[str, str]) -> list[Claim]:
    """Return the list of claims the user likely qualifies for, ranked by max value."""
    a = {k: (v or "").strip().lower() for k, v in answers.items()}
    results: list[Claim] = []

    # §1 — Council Tax band challenge
    if a.get("owns_home") == "yes" and a.get("neighbours_lower_band") in ("yes", "not_sure"):
        confidence = "Strong" if a.get("neighbours_lower_band") == "yes" else "Worth checking"
        results.append(Claim(
            slug="council_tax_band",
            title="Council Tax band challenge",
            estimated_min_gbp=400,
            estimated_max_gbp=1500,
            headline="Refund of overpaid council tax — plus £100–£400/year ongoing.",
            why_you_qualify=f"{confidence} — you own your home and similar homes nearby may be in a lower band.",
            next_step="Use the neighbour-check at gov.uk/council-tax-bands, then submit a free review with the VOA. See letters/council_tax_band_challenge.md.",
            gov_uk_link="https://www.gov.uk/challenge-council-tax-band",
        ))

    # §2 — Single Person Discount
    if a.get("sole_adult") == "yes":
        results.append(Claim(
            slug="single_person_discount",
            title="Single Person Discount on Council Tax",
            estimated_min_gbp=400,
            estimated_max_gbp=600,
            headline="25% off your council tax bill — backdatable up to 6 years.",
            why_you_qualify="You're the only adult at your address.",
            next_step="Apply on your council's website. Explicitly request backdating to the date you became the sole adult. See letters/single_person_discount.md.",
            gov_uk_link="https://www.gov.uk/council-tax/discounts-for-disabled-people",
        ))

    # §4 — Marriage Allowance
    if a.get("married") == "yes" and a.get("spouse_low_earner") in ("yes", "not_sure"):
        results.append(Claim(
            slug="marriage_allowance",
            title="Marriage Allowance",
            estimated_min_gbp=252,
            estimated_max_gbp=1260,
            headline="£252/year — backdate 4 years for up to ~£1,260 total.",
            why_you_qualify="One spouse earns under the personal allowance (£12,570) and the other is a basic-rate taxpayer.",
            next_step="The lower earner applies at gov.uk/marriage-allowance — tick ALL 4 backdate years. See letters/marriage_allowance_steps.md.",
            gov_uk_link="https://www.gov.uk/marriage-allowance",
        ))

    # §5 — Working from Home tax relief (pre-2022)
    if a.get("wfh_pre_2022") == "yes":
        results.append(Claim(
            slug="wfh_tax_relief",
            title="Working from Home tax relief",
            estimated_min_gbp=125,
            estimated_max_gbp=500,
            headline="Backdated WFH tax relief for 2020–21 and 2021–22.",
            why_you_qualify="You worked from home during a tax year before April 2022 but haven't claimed.",
            next_step="Apply via gov.uk/tax-relief-for-employees/working-at-home using your Government Gateway login.",
            gov_uk_link="https://www.gov.uk/tax-relief-for-employees/working-at-home",
        ))

    # §6 — Uniform / tools tax relief
    if a.get("uniform_or_tools") == "yes":
        results.append(Claim(
            slug="uniform_relief",
            title="Uniform / tools tax relief",
            estimated_min_gbp=60,
            estimated_max_gbp=700,
            headline="Trade-specific flat-rate allowance — backdate 4 years.",
            why_you_qualify="You wear a uniform or buy your own tools for work.",
            next_step="Apply at gov.uk/tax-relief-for-employees/uniforms-work-clothing-and-tools — flat rate £60–£140/year by trade.",
            gov_uk_link="https://www.gov.uk/tax-relief-for-employees/uniforms-work-clothing-and-tools",
        ))

    # §7 — Higher-rate pension top-up
    if a.get("higher_rate_pension") == "yes":
        results.append(Claim(
            slug="pension_top_up",
            title="Higher-rate pension tax relief",
            estimated_min_gbp=200,
            estimated_max_gbp=4000,
            headline="Reclaim 20% extra on every pension contribution.",
            why_you_qualify="You're a higher-rate taxpayer paying into a relief-at-source pension.",
            next_step="Add contributions to your Self Assessment, or write to HMRC. Backdatable 4 years.",
            gov_uk_link="https://www.gov.uk/tax-on-your-private-pension/pension-tax-relief",
        ))

    # §8 — Tax-Free Childcare
    if a.get("children_under_12") == "yes":
        results.append(Claim(
            slug="tax_free_childcare",
            title="Tax-Free Childcare",
            estimated_min_gbp=500,
            estimated_max_gbp=2000,
            headline="Government adds 25% to your childcare account — up to £2,000/year per child.",
            why_you_qualify="You have a child under 12 in childcare.",
            next_step="Open a Tax-Free Childcare account at gov.uk/tax-free-childcare. Reconfirm every 3 months.",
            gov_uk_link="https://www.gov.uk/tax-free-childcare",
        ))
        results.append(Claim(
            slug="free_childcare_hours",
            title="Free childcare hours (England)",
            estimated_min_gbp=4000,
            estimated_max_gbp=8000,
            headline="15 or 30 hours/week of free childcare for eligible working parents.",
            why_you_qualify="You have a child in the eligible age range and are working.",
            next_step="Apply for an eligibility code at gov.uk/30-hours-free-childcare before the term you want it.",
            gov_uk_link="https://www.gov.uk/30-hours-free-childcare",
        ))

    # §10 — Pension Credit
    if a.get("over_state_pension_age") == "yes" and a.get("pensioner_low_income") in ("yes", "not_sure"):
        results.append(Claim(
            slug="pension_credit",
            title="Pension Credit (and the schemes it unlocks)",
            estimated_min_gbp=3900,
            estimated_max_gbp=6000,
            headline="Average award £3,900/year — plus Warm Home Discount, Cold Weather Payment, Council Tax Reduction, free TV licence (over 75s).",
            why_you_qualify="The applicant is over State Pension age with low weekly income.",
            next_step="Phone 0800 99 1234 — apply by phone (faster than online). Backdate 3 months. See letters/pension_credit_check.md.",
            gov_uk_link="https://www.gov.uk/pension-credit",
        ))

    # §11 — Attendance Allowance
    if a.get("over_state_pension_age") == "yes" and a.get("health_affects_daily_life") == "yes":
        results.append(Claim(
            slug="attendance_allowance",
            title="Attendance Allowance",
            estimated_min_gbp=3840,
            estimated_max_gbp=5740,
            headline="£73.90 or £110.40 per week — tax-free, not means-tested.",
            why_you_qualify="Over State Pension age and a health condition affects daily life.",
            next_step="Request form AA1 from 0800 731 0122. Get help from Citizens Advice or Age UK to fill it in.",
            gov_uk_link="https://www.gov.uk/attendance-allowance",
        ))

    # §12 — PIP
    if a.get("over_state_pension_age") == "no" and a.get("health_affects_daily_life") == "yes":
        results.append(Claim(
            slug="pip",
            title="Personal Independence Payment (PIP)",
            estimated_min_gbp=1500,
            estimated_max_gbp=9750,
            headline="£29.20 to £187.45 per week — tax-free, not means-tested.",
            why_you_qualify="A health condition or disability affects daily life and you're under State Pension age.",
            next_step="Phone 0800 917 2222 to start the claim. Get help from Citizens Advice or a disability charity.",
            gov_uk_link="https://www.gov.uk/pip",
        ))

    # §16 — Section 75
    if a.get("credit_card_dispute") == "yes":
        results.append(Claim(
            slug="section_75",
            title="Section 75 chargeback (credit card)",
            estimated_min_gbp=100,
            estimated_max_gbp=30000,
            headline="Full refund from your card issuer — they're jointly liable with the merchant.",
            why_you_qualify="You paid £100+ on a credit card for something that went wrong.",
            next_step="Send the Section 75 letter to the card issuer's disputes team. See letters/section_75_claim.md.",
            gov_uk_link="https://www.fca.org.uk/consumers/claim-using-section-75-credit-consumer-act",
        ))

    # §17 — Energy credit balance
    if a.get("energy_credit") in ("yes", "not_sure"):
        results.append(Claim(
            slug="energy_credit_refund",
            title="Energy supplier credit balance refund",
            estimated_min_gbp=150,
            estimated_max_gbp=800,
            headline="Cash refund of any credit on your energy account — and you can lower your direct debit too.",
            why_you_qualify="Your account has been in credit longer than reasonable.",
            next_step="Submit fresh meter readings, then send the credit-refund letter. See letters/energy_credit_refund.md.",
            gov_uk_link="https://www.ofgem.gov.uk/information-consumers/energy-advice-households",
        ))

    # §18 — Mis-sold packaged account
    if a.get("packaged_account") == "yes":
        results.append(Claim(
            slug="packaged_account",
            title="Mis-sold packaged bank account refund",
            estimated_min_gbp=500,
            estimated_max_gbp=3000,
            headline="Refund of monthly fees plus 8% statutory interest.",
            why_you_qualify="You paid for a packaged account whose bundled perks you couldn't use.",
            next_step="Write to the bank's customer relations. If rejected, escalate to the Financial Ombudsman within 6 months.",
            gov_uk_link="https://www.financial-ombudsman.org.uk/consumers/complaints-can-help/banking-payment/packaged-bank-account",
        ))

    results.sort(key=lambda c: c.estimated_max_gbp, reverse=True)
    return results


def total_potential(claims: list[Claim]) -> tuple[int, int]:
    """Return (min_total, max_total) GBP across all flagged claims."""
    return (
        sum(c.estimated_min_gbp for c in claims),
        sum(c.estimated_max_gbp for c in claims),
    )
