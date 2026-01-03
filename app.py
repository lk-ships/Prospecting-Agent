#!/usr/bin/env python3
"""
Web server for triggering the prospecting agent via URL.
Deploy to Render.com and trigger from anywhere.
"""

import base64
import json
import os
import tempfile
import time

from flask import Flask, jsonify, request

from news_client import NewsClient
from sheets_client import SheetsClient
from trigger_analyzer import TriggerAnalyzer

app = Flask(__name__)


def get_credentials_path():
    """Get path to credentials.json, creating from env var if needed."""
    # Check for local file first
    if os.path.exists("credentials.json"):
        return "credentials.json"

    # Otherwise, decode from environment variable
    creds_b64 = os.getenv("GOOGLE_CREDENTIALS_BASE64")
    if not creds_b64:
        raise ValueError("No credentials.json file or GOOGLE_CREDENTIALS_BASE64 env var found")

    # Decode and write to temp file
    creds_json = base64.b64decode(creds_b64).decode("utf-8")
    temp_path = "/tmp/credentials.json"
    with open(temp_path, "w") as f:
        f.write(creds_json)
    return temp_path


def run_agent():
    """Run the prospecting agent and return results."""
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
        return {"error": f"Missing environment variables: {', '.join(missing)}"}, 500

    # Get credentials
    try:
        creds_path = get_credentials_path()
    except ValueError as e:
        return {"error": str(e)}, 500

    # Initialize clients
    try:
        sheets = SheetsClient(sheet_id, credentials_path=creds_path)
        news = NewsClient(newsapi_key)
        analyzer = TriggerAnalyzer(anthropic_key)
    except Exception as e:
        return {"error": f"Failed to initialize: {str(e)}"}, 500

    # Read companies
    companies = sheets.read_companies()
    existing_triggers = sheets.get_existing_triggers()

    if not companies:
        return {"message": "No companies found in sheet", "triggers_added": 0}

    # Process each company
    triggers_found = 0
    new_triggers_added = 0
    skipped_duplicates = 0
    errors = 0
    results_log = []

    for company in companies:
        # Search for news
        articles = news.search_company_news(company.name)

        if not articles:
            continue

        # Analyze for triggers
        results = analyzer.analyze_articles(company.name, articles)

        if not results:
            continue

        triggers_found += len(results)

        # Add each trigger
        for result in results:
            key = (company.name.lower(), result.article_url)
            if key in existing_triggers:
                skipped_duplicates += 1
                continue

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
                existing_triggers.add(key)
                results_log.append({
                    "company": company.name,
                    "trigger": result.trigger_type,
                    "priority": result.priority,
                })
            except Exception as e:
                errors += 1

        # Rate limiting
        time.sleep(0.5)

    return {
        "message": "Agent completed successfully",
        "companies_processed": len(companies),
        "triggers_found": triggers_found,
        "new_rows_added": new_triggers_added,
        "duplicates_skipped": skipped_duplicates,
        "errors": errors,
        "triggers": results_log,
    }


@app.route("/")
def home():
    """Home page - just confirms the service is running."""
    return jsonify({"status": "ok", "message": "Prospecting Agent is running"})


@app.route("/run/<secret_token>")
def run_with_token(secret_token):
    """Run the agent if the secret token matches."""
    expected_token = os.getenv("SECRET_TOKEN")

    if not expected_token:
        return jsonify({"error": "SECRET_TOKEN not configured"}), 500

    if secret_token != expected_token:
        return jsonify({"error": "Invalid token"}), 403

    result = run_agent()
    if isinstance(result, tuple):
        return jsonify(result[0]), result[1]
    return jsonify(result)


@app.route("/health")
def health():
    """Health check endpoint for Render."""
    return jsonify({"status": "healthy"})


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
