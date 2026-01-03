# Prospecting Trigger Agent

Automated agent that monitors news for buying triggers and updates a Google Sheet with findings.

## What It Does

For each company in your Google Sheet, the agent:
1. Searches NewsAPI for recent articles (past 6 months)
2. Uses Claude AI to analyze articles for buying triggers
3. Updates the sheet with trigger summary, type, date, and article link

### Trigger Types Detected

- M&A activity (acquisitions, mergers, divestitures)
- Funding rounds (Series B+, IPO prep/completion)
- Private equity acquisitions
- Executive changes (CIO, CFO, CHRO, COO, VP IT/HR)
- Geographic expansion / new office openings
- Headcount growth (100+ hires announced)
- Digital transformation initiatives
- Legacy system migrations (SAP, Oracle, PeopleSoft)
- Cloud migration projects
- System outages or IT failures
- Restructuring or reorganization
- Compliance issues / new regulatory requirements
- Remote/hybrid work policy changes
- Operational challenges mentioned in earnings
- Industry awards (Inc 5000, Fast Company, Best Places to Work)

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Get API keys

**NewsAPI (free tier - 100 requests/day):**
1. Register at https://newsapi.org/register
2. Copy your API key

**Google Sheets:**
1. Go to https://console.cloud.google.com
2. Create or select a project
3. Enable the **Google Sheets API**
4. Go to **IAM & Admin → Service Accounts**
5. Create a service account
6. Click the account → **Keys → Add Key → JSON**
7. Save the file as `credentials.json` in this directory
8. Share your Google Sheet with the service account email (Editor access)

### 3. Configure environment

```bash
cp .env.example .env
```

Edit `.env`:
```
GOOGLE_SHEET_ID=your_sheet_id_here
NEWSAPI_KEY=your_newsapi_key
ANTHROPIC_API_KEY=your_anthropic_key
```

The Sheet ID is in your Google Sheet URL:
```
https://docs.google.com/spreadsheets/d/THIS_IS_YOUR_SHEET_ID/edit
```

### 4. Prepare your Google Sheet

Row 1 should have these headers:

| Company Name | Website | Latest Trigger | Trigger Date | Article Link | Trigger Type |
|--------------|---------|----------------|--------------|--------------|--------------|

Add company names in column A (website in column B is optional).

## Usage

```bash
python run_agent.py
```

The agent will process each company and print progress to the console. Triggers found are written directly to the sheet.

## Cost

- **NewsAPI**: Free tier allows 100 requests/day (1 per company)
- **Claude**: Uses Haiku model, ~$0.001 per company analyzed
