"""
Arizona Construction RFP Scraper
What it does: Finds open government bids for AZ construction companies
Who buys this: HVAC, electrical, plumbing, concrete subs in Arizona
Your price: $199-399/month per client
"""

import requests
from openai import OpenAI
import os

# ── Setup ──────────────────────────────────────────────────────
client = OpenAI(
    base_url='https://models.inference.ai.azure.com',
    api_key=os.environ.get('GITHUB_TOKEN')
)

print("=" * 60)
print("ARIZONA CONSTRUCTION RFP SCRAPER")
print("=" * 60)

# ── LEARN: What is this data? ──────────────────────────────────
# SAM.gov = US government's official bid posting site
# Every federal agency posts contracts here
# Construction subs MISS these because they don't know where to look
# YOUR JOB: Find them, summarize them, email them daily
# THEIR VALUE: One won bid = $50K-500K contract

# ── Sample bids (real format from SAM.gov) ────────────────────
# We use sample data first to build and test the logic
# Once SAM.gov API key arrives, swap in real data — same code

bids = [
    {
        'title': 'HVAC Replacement - Phoenix VA Medical Center',
        'agency': 'Dept of Veterans Affairs',
        'deadline': '2026-05-15',
        'value': '$450,000',
        'description': 'Replace 12 rooftop HVAC units at Phoenix VA Medical Center Building 10. Work includes removal of existing equipment, structural support modifications, new unit installation, ductwork connections, and commissioning. Contractor must be licensed in Arizona.'
    },
    {
        'title': 'Electrical Panel Upgrades - Tucson Federal Building',
        'agency': 'GSA Public Buildings Service',
        'deadline': '2026-05-20',
        'value': '$180,000',
        'description': 'Replace main electrical panels and upgrade to 400-amp service in 3 locations. Three-phase work required. Must meet NEC 2023 standards. Work to be performed after hours to avoid disruption.'
    },
    {
        'title': 'Parking Lot Repaving - Mesa Post Office',
        'agency': 'US Postal Service',
        'deadline': '2026-05-10',
        'value': '$95,000',
        'description': 'Repave 40,000 sqft parking area. Includes full depth reclamation, curb repair, ADA ramp upgrades, restriping, and LED lighting replacement. Must complete within 30 days of award.'
    },
    {
        'title': 'Plumbing Renovation - Scottsdale Social Security Office',
        'agency': 'Social Security Administration',
        'deadline': '2026-05-25',
        'value': '$67,000',
        'description': 'Replace all plumbing fixtures in 2-story building. Includes restrooms, break rooms, and utility areas. Water-efficient fixtures required. Building remains occupied during work.'
    },
    {
        'title': 'Concrete Sidewalk Repair - Luke Air Force Base',
        'agency': 'Dept of the Air Force',
        'deadline': '2026-06-01',
        'value': '$120,000',
        'description': 'Repair and replace approximately 15,000 sqft of damaged concrete sidewalks and curbs throughout base housing area. Security clearance required for all workers. Must use Davis-Bacon wage rates.'
    }
]

print(f"\nFound {len(bids)} open bids in Arizona\n")
print("-" * 60)

# ── LEARN: The AI loop ────────────────────────────────────────
# This is the core of your product
# For each bid, we send the raw government text to AI
# AI rewrites it in plain English a contractor can act on
# This saves contractors 2-3 hours of reading per week
# That time savings = why they pay $299/month

for i, bid in enumerate(bids, 1):

    print(f"\nBid {i} of {len(bids)}: {bid['title']}")
    print(f"Agency:   {bid['agency']}")
    print(f"Deadline: {bid['deadline']}")
    print(f"Value:    {bid['value']}")

    # ── LEARN: This is a prompt ───────────────────────────────
    # A prompt is instructions you give the AI
    # The better your prompt, the more useful the output
    # This is a skill — you'll get better at it as we build

    prompt = f"""
You are helping an Arizona construction subcontractor quickly 
understand a government bid opportunity.

Bid: {bid['title']}
Agency: {bid['agency']}
Deadline: {bid['deadline']}
Estimated Value: {bid['value']}
Details: {bid['description']}

Write a 3-line summary:
Line 1: What work is needed (plain English, no jargon)
Line 2: Key requirements or challenges to know about
Line 3: Why this is worth bidding (or a red flag if not)

Be direct. Sound like a contractor talking to another contractor.
"""

    # ── LEARN: This is the API call ───────────────────────────
    # We send the prompt to GPT-4o-mini
    # It returns a response we can print or email
    # This same pattern works for ANY AI task you build

    response = client.chat.completions.create(
        model='gpt-4o-mini',
        messages=[{'role': 'user', 'content': prompt}],
        max_tokens=150        # Keep summaries short
    )

    summary = response.choices[0].message.content.strip()

    print(f"\nAI Summary:")
    print(summary)
    print("-" * 60)

print("\n✅ Done! This output becomes your daily email to clients.")
print("Next step: Connect to real SAM.gov data and automate the email.")
