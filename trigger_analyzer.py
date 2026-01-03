"""Claude-powered trigger analysis for news articles."""

import json
from dataclasses import dataclass
from typing import List

import anthropic

from config import CLAUDE_MODEL, TRIGGER_TYPES
from news_client import Article


@dataclass
class TriggerResult:
    """Result of trigger analysis."""
    trigger_type: str
    summary: str
    article_url: str
    article_date: str


class TriggerAnalyzer:
    """Analyzes news articles for buying triggers using Claude."""

    def __init__(self, api_key: str):
        """Initialize the analyzer.

        Args:
            api_key: Anthropic API key
        """
        self.client = anthropic.Anthropic(api_key=api_key)

    def analyze_articles(
        self, company_name: str, articles: List[Article]
    ) -> List[TriggerResult]:
        """Analyze articles to find ALL buying triggers.

        Args:
            company_name: Name of the company
            articles: List of articles to analyze

        Returns:
            List of TriggerResult objects for each trigger found
        """
        if not articles:
            return []

        # Format articles for the prompt
        articles_text = "\n\n".join(
            f"[{i+1}] {a.title}\n"
            f"Source: {a.source} | Date: {a.published_at}\n"
            f"Summary: {a.description}\n"
            f"URL: {a.url}"
            for i, a in enumerate(articles)
        )

        trigger_types_text = "\n".join(f"- {t}" for t in TRIGGER_TYPES)

        prompt = f"""Analyze these news articles about {company_name} to identify ALL buying triggers for enterprise software.

ARTICLES:
{articles_text}

TRIGGER TYPES TO LOOK FOR:
{trigger_types_text}

TASK:
1. Read each article carefully
2. Identify ALL articles that indicate HIGH-IMPACT buying triggers
3. Focus on events that suggest the company may need new enterprise software (HR systems, ERP, cloud infrastructure, etc.)
4. A single article can have multiple triggers (e.g., M&A + Executive Change)
5. Different articles can have different triggers

Respond with a JSON object:
{{
    "triggers": [
        {{
            "trigger_type": "The specific trigger type from the list above",
            "summary": "2-3 sentence summary of the trigger event and why it indicates software buying potential",
            "article_index": 1-based index of the relevant article
        }}
    ]
}}

Return an empty array if no triggers found: {{"triggers": []}}
Only return the JSON, no other text."""

        try:
            response = self.client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}],
            )

            # Parse the response
            response_text = response.content[0].text.strip()

            # Handle potential markdown code blocks
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
                response_text = response_text.strip()

            result = json.loads(response_text)
            triggers = result.get("triggers", [])

            if not triggers:
                return []

            results = []
            for trigger in triggers:
                # Get the referenced article
                article_idx = trigger.get("article_index", 1) - 1
                if 0 <= article_idx < len(articles):
                    article = articles[article_idx]
                else:
                    article = articles[0]  # Fallback to first article

                results.append(TriggerResult(
                    trigger_type=trigger.get("trigger_type", ""),
                    summary=trigger.get("summary", ""),
                    article_url=article.url,
                    article_date=article.published_at,
                ))

            return results

        except Exception as e:
            print(f"  Warning: Analysis error for {company_name}: {e}")
            return []
