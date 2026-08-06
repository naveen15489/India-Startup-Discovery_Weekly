#!/usr/bin/env python3
"""
Weekly India Agri Startup Digest -> Gmail draft.

Simplified version: uses a Gmail "App Password" over IMAP instead of the full
Gmail API OAuth flow. No Google Cloud project needed.

Flow:
  1. Call the Anthropic API (Claude, with the native web_search tool) to research
     and write this week's digest.
  2. Connect to Gmail via IMAP and append the message directly to your
     [Gmail]/Drafts folder. This does NOT send anything -- it only creates a draft.

Required environment variables (set as GitHub Actions secrets):
  ANTHROPIC_API_KEY
  GMAIL_ADDRESS          e.g. naveen@gmail.com
  GMAIL_APP_PASSWORD     16-character App Password (see README for how to generate)
  DIGEST_RECIPIENT       (optional) pre-fills the draft's "To" field
"""

import imaplib
import os
import sys
import time
from datetime import date
from email.mime.text import MIMEText

import anthropic

MODEL = "claude-sonnet-5"
MAX_TOKENS = 8000

DIGEST_PROMPT = """You are an India-first startup discovery and research agent.
Your job is to search broadly across the public web and produce a high-signal
weekly digest of startup stories, launches, pilots, partnerships, grants,
cohorts, and fundraising events in agriculture and adjacent innovation sectors.

## Mission
Find newly published or newly surfaced stories (this week) about startups and
emerging ventures in:
- agriculture, agtech, climate tech, carbon markets, carbon MRV
- bioenergy, biomass, waste-to-value
- biologicals, biofertilizers, biostimulants, soil health, regenerative agriculture
- dairy tech, poultry tech, piggery, livestock tech, aquaculture tech
- precision agriculture, irrigation and water tech, farm mechanization, farm robotics
- traceability, food systems innovation, rural commerce, farmer platform innovation
- FPO-enabling technology, adjacent sectors where innovation or technology is central

## Geography priority
1. India-based startups
2. Global startups relevant to India
3. Adjacent global innovations that may shape agriculture, climate, rural
   livelihoods, or food systems

## What qualifies as a strong story
Prefer: pilot launches, customer deployments, commercial traction, partnerships,
grant wins, accelerator/incubator selections, demo day appearances, founder
interviews with concrete business info, fundraising, R&D commercialization,
university spinouts, strategically meaningful hires.

## Exclude
- Generic policy news without a startup angle
- Broad industry commentary with no company relevance
- Large incumbents unless a startup partnership is central
- Duplicate syndicated articles, rumor sites, listicles with no original reporting
- Purely academic research unless there is clear commercialization or startup formation
- Any startup that has raised Series A or later funding (pre-seed, seed, angel,
  grants, and non-dilutive funding are all fine; Series A and beyond is not)

## Time window
Primary: last 7 days. If the pool is thin, you may note that explicitly and
include high-quality items up to 14 days old, clearly dated. Always prefer
freshness and say so explicitly if you had to expand the window.

## Deduplication
Deduplicate aggressively. Keep the most authoritative source; cite a secondary
only if it adds important detail.

## Required fields per story
Company name, country, sector tags, trigger (Fundraise/Launch/Pilot/Partnership/
Grant/Cohort/Product/Interview/Deployment), what happened, why it matters,
technology angle, business/customer angle, founder names, funding/stage details,
company website, public contact email (only from official public sources --
never guess or invent), founder or company LinkedIn (only if clearly public),
source link + publication date, confidence (High/Medium/Low).
If any field is unavailable: say "Not disclosed" or "Not publicly visible."
Never invent contact details, emails, or LinkedIn URLs.

## Output format
Write this as a complete, ready-to-send weekly email. Use this structure:

Subject line (as the very first line, prefixed with "SUBJECT: ")

Then the email body:
# Weekly Startup Digest -- India Agri & Adjacent Innovation

## Top Stories (as many strong ones as you found, ideally 5-10)
[full card format per story, per the required fields above]

## Early Signals
[cohort selections, challenge winners, university spinouts, pilots]

## Adjacent Sector Watchlist
[notable adjacent developments]

## One-Line Lead List
Company | geography | sector | trigger | website | contact | source

## Patterns Emerging This Week
[3-5 concise themes]

## Quality rules
- Concise and factual -- no hype language, no hallucinations
- No invented funding details, founders, or contact information
- If sources disagree, say so briefly
- Prefer primary or high-authority sources
- Useful for an investor, incubator, accelerator, donor, or ecosystem builder

Write the email now for the week ending {today}.
""".strip()


def generate_digest() -> tuple[str, str]:
    """Call the Anthropic API and return (subject, body)."""
    api_key = os.environ["ANTHROPIC_API_KEY"]
    client = anthropic.Anthropic(api_key=api_key)

    prompt = DIGEST_PROMPT.format(today=date.today().isoformat())

    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        tools=[
            {
                "type": "web_search_20250305",
                "name": "web_search",
                "max_uses": 25,
            }
        ],
        messages=[{"role": "user", "content": prompt}],
    )

    text_blocks = [block.text for block in response.content if block.type == "text"]
    full_text = "\n".join(text_blocks).strip()

    if not full_text:
        raise RuntimeError("Claude returned no text content -- check the API response.")

    subject = f"Weekly Startup Digest -- India Agri & Adjacent Innovation ({date.today().isoformat()})"
    body = full_text

    if full_text.upper().startswith("SUBJECT:"):
        first_line, _, rest = full_text.partition("\n")
        subject = first_line.split(":", 1)[1].strip()
        body = rest.strip()

    return subject, body


def create_gmail_draft_via_imap(subject: str, body: str) -> None:
    """Append a draft message directly to the Gmail Drafts folder over IMAP."""
    address = os.environ["GMAIL_ADDRESS"]
    app_password = os.environ["GMAIL_APP_PASSWORD"]
    recipient = os.environ.get("DIGEST_RECIPIENT", "")

    message = MIMEText(body)
    message["From"] = address
    message["Subject"] = subject
    if recipient:
        message["To"] = recipient

    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    imap.login(address, app_password)
    try:
        # \Draft flag marks it as a draft; the date is used for sort order.
        imap.append(
            '"[Gmail]/Drafts"',
            "(\\Draft)",
            imaplib.Time2Internaldate(time.time()),
            message.as_bytes(),
        )
    finally:
        imap.logout()


def main() -> None:
    print("Generating this week's digest via Claude API (this may take a minute)...")
    subject, body = generate_digest()

    print(f"Digest generated ({len(body)} chars). Creating Gmail draft via IMAP...")
    create_gmail_draft_via_imap(subject, body)

    print(f"Done. Gmail draft created: subject={subject!r}")


if __name__ == "__main__":
    try:
        main()
    except KeyError as e:
        print(f"Missing required environment variable: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Weekly digest run failed: {e}", file=sys.stderr)
        sys.exit(1)
