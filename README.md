# Weekly India Agri Startup Digest — Automation

Every Monday, this repo's GitHub Action calls the Claude API (with live web
search) to research the week's India agri/climate/agtech startup news, then
creates a **draft** (never auto-sent) directly in your Gmail Drafts folder so
you can review and send it.

No Google Cloud project needed — this uses a Gmail **App Password** over
IMAP instead of the full Gmail API OAuth flow.

## What runs where

- **GitHub Actions** (`.github/workflows/weekly-digest.yml`) — the weekly
  clock. Checks out the repo, installs dependencies, runs the script below.
- **`weekly_digest.py`** — does the actual work:
  1. Calls the Anthropic API with the `web_search` tool to research and write
     the digest (the full brief is inline in `DIGEST_PROMPT`).
  2. Logs into Gmail over IMAP with your App Password and appends the message
     straight into your Drafts folder.

## One-time setup (about 5 minutes)

### 1. Get an Anthropic API key
Go to https://console.anthropic.com/ → Settings → API Keys → Create Key.
Keep it somewhere safe.

### 2. Turn on 2-Step Verification (if not already on)
App Passwords require it. Go to https://myaccount.google.com/security and
enable **2-Step Verification** if you haven't already.

### 3. Generate a Gmail App Password
1. Go to https://myaccount.google.com/apppasswords
   (if that link doesn't work directly, go to Google Account → Security →
   search "App passwords")
2. Enter a name like "weekly-digest" and click **Create**
3. Google shows you a 16-character password (e.g. `abcd efgh ijkl mnop`) —
   copy it. You won't be able to see it again (but you can always generate a
   new one).

### 4. Add GitHub repo secrets
In your repo: **Settings → Secrets and variables → Actions → New repository
secret**. Add:

| Secret name | Value |
|---|---|
| `ANTHROPIC_API_KEY` | from step 1 |
| `GMAIL_ADDRESS` | your full Gmail address, e.g. `naveen@gmail.com` |
| `GMAIL_APP_PASSWORD` | the 16-character password from step 3 (no spaces) |
| `DIGEST_RECIPIENT` | *(optional)* email address you want pre-filled in the draft's "To" field |

### 5. Push this repo to GitHub
```bash
git init
git add .
git commit -m "Weekly India agri startup digest automation"
git branch -M main
git remote add origin https://github.com/naveen15489/India-Startup-Discovery_Weekly.git
git push -u origin main
```

### 6. Test it
Go to your repo's **Actions** tab → "Weekly India Agri Startup Digest" →
**Run workflow** button. This runs it immediately instead of waiting for
Monday. Check the run logs, then check Gmail → Drafts.

## Changing the schedule
Edit the `cron` line in `.github/workflows/weekly-digest.yml`. It's in UTC.
Current setting (`30 3 * * 1`) = Monday 09:00 IST. Use https://crontab.guru
if you want a different day/time.

## Changing what gets researched
Edit `DIGEST_PROMPT` in `weekly_digest.py` — sectors, exclusions, funding-stage
filter (currently excludes Series A and later), time window, and output
format all live there.

## Safety notes
- This automation only ever **creates a Gmail draft**. It never sends email
  on its own.
- An App Password grants broader account access than the OAuth "compose-only"
  scope would have — but it's fully revocable any time from
  https://myaccount.google.com/apppasswords with one click, and it can't be
  used to change your actual Google account password.
- GitHub Actions minutes on public repos are free; on private repos this uses
  a small amount of your monthly included minutes (a single run takes a
  couple of minutes).
- Each run costs a small amount of Anthropic API usage (dependent on how many
  searches Claude makes — bounded by `max_uses: 25` in `weekly_digest.py`).
