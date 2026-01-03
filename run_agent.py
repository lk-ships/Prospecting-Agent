#!/usr/bin/env python3
"""
Prospecting Trigger Agent

Searches for buying triggers in news articles for companies in a Google Sheet.
Appends NEW ROWS for each trigger found (multiple triggers per company possible).

Usage:
    python run_agent.py
"""

import os
import sys
import time

from dotenv import load_dotenv

from news_client import NewsClient
from sheets_client import SheetsClient
from trigger_analyzer import TriggerAnalyzer


def main():
    # Load environment variables
    load_dotenv()

    sheet_id = os.getenv("GOOGLE_SHEET_ID")
    newsapi_key = os.getenv("NEWSAPI_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")

    # Validate configuration
    missing = []
    if not sheet_id:
        missing.append("GOOGLE_SHEET_ID")
    if not newsapi_key:
        missing.append("NEWSAPI_KEY")
    if not anthropic_key:
        missing.append("ANTHROPIC_API_KEY")

    if missing:
        print("Error: Missing required environment variables:")
        for var in missing:
            print(f"  - {var}")
        print("\nCopy .env.example to .env and fill in your values.")
        sys.exit(1)

    # Check for credentials file
    if not os.path.exists("credentials.json"):
        print("Error: credentials.json not found.")
        print("Download your Google Cloud service account key and save it as credentials.json")
        sys.exit(1)

    print("=" * 60)
    print("PROSPECTING TRIGGER AGENT")
    print("=" * 60)

    # Initialize clients
    print("\nInitializing...")
    try:
        sheets = SheetsClient(sheet_id)
        news = NewsClient(newsapi_key)
        analyzer = TriggerAnalyzer(anthropic_key)
    except Exception as e:
        print(f"Error initializing clients: {e}")
        sys.exit(1)

    # Read companies from sheet
    print("Reading companies from Google Sheet...")
    companies = sheets.read_companies()
    print(f"Found {len(companies)} unique companies")

    # Get existing triggers to avoid duplicates
    print("Checking for existing triggers...")
    existing_triggers = sheets.get_existing_triggers()
    print(f"Found {len(existing_triggers)} existing trigger entries\n")

    if not companies:
        print("No companies found in the sheet. Add some companies and try again.")
        sys.exit(0)

    # Process each company
    triggers_found = 0
    new_triggers_added = 0
    skipped_duplicates = 0
    errors = 0

    for i, company in enumerate(companies, 1):
        print(f"[{i}/{len(companies)}] {company.name}")

        # Search for news
        print("  Searching news...")
        articles = news.search_company_news(company.name)

        if not articles:
            print("  No articles found")
            continue

        print(f"  Found {len(articles)} articles, analyzing...")

        # Analyze for ALL triggers
        results = analyzer.analyze_articles(company.name, articles)

        if not results:
            print("  No relevant triggers found")
            continue

        print(f"  Found {len(results)} trigger(s)!")
        triggers_found += len(results)

        # Add each trigger as a new row
        for result in results:
            # Check if this trigger already exists (by company + article URL)
            key = (company.name.lower(), result.article_url)
            if key in existing_triggers:
                print(f"    - {result.trigger_type} (already exists, skipping)")
                skipped_duplicates += 1
                continue

            print(f"    + [{result.priority}] {result.trigger_type}")

            try:
                sheets.append_trigger(
                    company_name=company.name,
                    website=company.website,
                    trigger_summary=result.summary,
                    trigger_type=result.trigger_type,
                    trigger_date=result.article_date,
                    article_link=result.article_url,
                    priority=result.priority,
                )
                new_triggers_added += 1
                # Add to existing set to avoid duplicates within this run
                existing_triggers.add(key)
            except Exception as e:
                print(f"    Error adding trigger: {e}")
                errors += 1

        # Small delay to be nice to APIs
        time.sleep(0.5)

    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Companies processed: {len(companies)}")
    print(f"Total triggers found: {triggers_found}")
    print(f"New rows added: {new_triggers_added}")
    if skipped_duplicates:
        print(f"Duplicates skipped: {skipped_duplicates}")
    if errors:
        print(f"Errors: {errors}")
    print("\nDone!")


if __name__ == "__main__":
    main()
