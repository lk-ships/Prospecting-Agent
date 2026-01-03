#!/usr/bin/env python3
"""
Prospecting Trigger Agent

Searches for buying triggers in news articles for companies in a Google Sheet.
Updates the sheet with trigger summaries, types, dates, and article links.

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
    print(f"Found {len(companies)} companies\n")

    if not companies:
        print("No companies found in the sheet. Add some companies and try again.")
        sys.exit(0)

    # Process each company
    triggers_found = 0
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

        # Analyze for triggers
        result = analyzer.analyze_articles(company.name, articles)

        if result and result.has_trigger:
            print(f"  TRIGGER FOUND: {result.trigger_type}")
            print(f"  Summary: {result.summary[:80]}...")

            # Update the sheet
            try:
                sheets.update_trigger(
                    row_number=company.row_number,
                    trigger_summary=result.summary,
                    trigger_type=result.trigger_type,
                    trigger_date=result.article_date,
                    article_link=result.article_url,
                )
                triggers_found += 1
                print("  Sheet updated!")
            except Exception as e:
                print(f"  Error updating sheet: {e}")
                errors += 1
        else:
            print("  No relevant triggers found")

        # Small delay to be nice to APIs
        time.sleep(0.5)

    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Companies processed: {len(companies)}")
    print(f"Triggers found: {triggers_found}")
    if errors:
        print(f"Errors: {errors}")
    print("\nDone!")


if __name__ == "__main__":
    main()
