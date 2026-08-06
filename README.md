# Weekly India Agri Startup Digest — Automation

Every Monday, this repo's GitHub Action calls the Claude API (with live web
search) to research the week's India agri/climate/agtech startup news, then
creates a **draft** (never auto-sent) in your Gmail account so you can review
and send it.

## What runs where

- **GitHub Actions** (`.github/workflows/weekly-digest.yml`) — the weekly
  clock. It just checks out the repo, installs dependencies, and runs the
  script below.
- **`weekly_digest.py`** — does the actual work:
  1. Calls the Anthropic API with the `web_search` tool to research and write
     the digest (the full brief is inline in `DIGEST_PROMPT`).
  2. Calls the Gmail API to create a draft with that content.
- **`get_gmail_refresh_token.py`** — a one-time helper you run locally, once,
  to authorize this automation against your Gmail account.

## One-time setup (about 15 minutes)

### 1. Get an Anthropic API key
Go to https://console.anthropic.com/ → Settings → API Keys → Create Key.
Keep it somewhere safe — you'll paste it into GitHub secrets in step 4.

### 2. Set up Gmail API access
1. Go to https://console.cloud.google.com/ and create a new project (or reuse one).
2. **APIs & Services → Library** → search "Gmail API" → Enable.
3. **APIs & Services → OAuth consent screen**:
   - User type: External (unless you have Workspace)
   - Add your own Gmail address under **Test users**
   - You do not need to submit for verification — test mode works fine for personal use
4. **APIs & Services → Credentials → Create Credentials → OAuth client ID**:
   - Application type: **Desktop app**
   - Download the JSON — rename it to `credentials.json` and put it in this
     folder on your own computer (not in the GitHub repo — don't commit it).

### 3. Generate your refresh token (run locally, once)
```bash
pip install google-auth-oauthlib google-auth google-api-python-client
python get_gmail_refresh_token.py
```
This opens a browser window — log in with the Gmail account you want drafts
created in, and approve the "compose" permission. The script prints three
values:
```
GMAIL_CLIENT_ID=...
GMAIL_CLIENT_SECRET=...
GMAIL_REFRESH_TOKEN=...
```
Copy these — you'll need them in the next step. (Note: the permission
requested is `gmail.compose` only — this automation can create/edit drafts
but cannot read your inbox or send mail on its own.)

### 4. Add GitHub repo secrets
In your GitHub repo: **Settings → Secrets and variables → Actions → New
repository secret**. Add:

| Secret name | Value |
|---|---|
| `ANTHROPIC_API_KEY` | from step 1 |
| `GMAIL_CLIENT_ID` | from step 3 |
| `GMAIL_CLIENT_SECRET` | from step 3 |
| `GMAIL_REFRESH_TOKEN` | from step 3 |
| `DIGEST_RECIPIENT` | *(optional)* the email address you want pre-filled in the draft's "To" field |

### 5. Push this repo to GitHub
```bash
git init
git add .
git commit -m "Weekly India agri startup digest automation"
git branch -M main
git remote add origin <your-repo-url>
git push -u origin main
```
Make sure `credentials.json` is **not** committed (it's not needed in the
repo — only the three secret values derived from it are).

### 6. Test it
Go to your repo's **Actions** tab → "Weekly India Agri Startup Digest" →
**Run workflow** (this uses the `workflow_dispatch` trigger, so you don't
have to wait until Monday). Check the run logs, then check Gmail → Drafts.

## Changing the schedule
Edit the `cron` line in `.github/workflows/weekly-digest.yml`. It's in UTC.
Current setting (`30 3 * * 1`) = Monday 09:00 IST. Use https://crontab.guru
if you want a different day/time.

## Changing what gets researched
Edit `DIGEST_PROMPT` in `weekly_digest.py` — sectors, exclusions, funding-stage
filter (currently excludes Series A and later), time window, and output
format all live there.

## Safety notes
- This automation only ever **creates a Gmail draft**. It cannot send email,
  read your inbox, or delete anything — the OAuth scope is limited to
  `gmail.compose`.
- GitHub Actions minutes on public repos are free; on private repos this uses
  a small amount of your monthly included minutes (a single run takes a
  couple of minutes).
- Each run costs a small amount of Anthropic API usage (dependent on how many
  searches Claude makes — bounded by `max_uses: 25` in `weekly_digest.py`).
# India-Startup-Discovery_Weekly
