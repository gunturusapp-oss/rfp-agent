"""
RFP Email Sender
What it does: Emails the daily AZ bid report to your clients
This is your product delivery system
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from openai import OpenAI
import datetime

# ── Setup ──────────────────────────────────────────────────────
GMAIL_USER     = os.environ.get('GMAIL_USER')
GMAIL_PASSWORD = os.environ.get('GMAIL_APP_PASSWORD')
GITHUB_TOKEN   = os.environ.get('GITHUB_TOKEN')

client = OpenAI(
    base_url='https://models.inference.ai.azure.com',
    api_key=GITHUB_TOKEN
)

today = datetime.date.today().strftime('%B %d, %Y')

# ── Sample bids (same as rfp_scraper.py) ──────────────────────
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
    }
]

# ── Step 1: Generate AI summaries ─────────────────────────────
print("Generating AI summaries...")

email_body = f"""
<html>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">

<h2 style="color: #1a1a1a;">🏗️ Arizona Construction Bids — {today}</h2>
<p style="color: #666;">Here are today's open government bids matching your trade. 
Each bid has been reviewed and summarized by AI to save you time.</p>
<hr>
"""

for i, bid in enumerate(bids, 1):
    prompt = f"""
You are helping an Arizona construction subcontractor evaluate a bid.

Bid: {bid['title']}
Agency: {bid['agency']}
Deadline: {bid['deadline']}
Value: {bid['value']}
Details: {bid['description']}

Write exactly 3 lines:
Line 1: What the work is (plain English)
Line 2: Key requirement or challenge
Line 3: Verdict — worth bidding or not and why

Be direct. One sentence per line. No bullet points.
"""

    response = client.chat.completions.create(
        model='gpt-4o-mini',
        messages=[{'role': 'user', 'content': prompt}],
        max_tokens=120
    )

    summary = response.choices[0].message.content.strip()

    email_body += f"""
<div style="margin: 20px 0; padding: 15px; border-left: 4px solid #0066cc; background: #f9f9f9;">
  <h3 style="margin: 0 0 5px; color: #0066cc;">{bid['title']}</h3>
  <p style="margin: 0 0 8px; color: #888; font-size: 13px;">
    {bid['agency']} &nbsp;|&nbsp; Deadline: {bid['deadline']} &nbsp;|&nbsp; Est. Value: {bid['value']}
  </p>
  <p style="margin: 0; color: #333; line-height: 1.6;">{summary.replace(chr(10), '<br>')}</p>
</div>
"""

    print(f"  ✅ Bid {i} summarized: {bid['title'][:40]}...")

email_body += """
<hr>
<p style="color: #999; font-size: 12px;">
  Powered by AZ Bid Intel — Your daily construction bid digest.<br>
  Reply to this email to request bids for a specific trade or county.
</p>
</body>
</html>
"""

# ── Step 2: Send the email ─────────────────────────────────────
print("\nSending email...")

# LEARN: This is how you send HTML email from Python
# MIMEMultipart = email container
# MIMEText = the actual content (HTML in this case)
# smtplib = Python's built-in email sending library

msg = MIMEMultipart('alternative')
msg['Subject'] = f"🏗️ {len(bids)} New AZ Construction Bids — {today}"
msg['From']    = GMAIL_USER
msg['To']      = GMAIL_USER  # Sending to yourself first as a test

msg.attach(MIMEText(email_body, 'html'))

# Connect to Gmail and send
with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
    server.login(GMAIL_USER, GMAIL_PASSWORD)
    server.sendmail(GMAIL_USER, GMAIL_USER, msg.as_string())

print(f"✅ Email sent to {GMAIL_USER}")
print("Check your Gmail inbox — you should see it within 30 seconds.")
print("\nNext step: Replace GMAIL_USER in msg['To'] with your client's email.")
