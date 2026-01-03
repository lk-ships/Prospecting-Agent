"""Claude-powered trigger analysis for news articles."""

import json
from dataclasses import dataclass

import anthropic

from config import CLAUDE_MODEL, TRIGGER_TYPES
from news_client import Article


@dataclass
class TriggerResult:
    """Result of trigger analysis."""
    has_trigger: bool
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
        self, company_name: str, articles: list[Article]
    ) -> TriggerResult | None:
        """Analyze articles to find buying triggers.

        Args:
            company_name: Name of the company
            articles: List of articles to analyze

        Returns:
            TriggerResult if a trigger is found, None otherwise
        """
        if not articles:
            return None

        # Format articles for the prompt
        articles_text = "\n\n".join(
            f"[{i+1}] {a.title}\n"
            f"Source: {a.source} | Date: {a.published_at}\n"
            f"Summary: {a.description}\n"
            f"URL: {a.url}"
            for i, a in enumerate(articles)
        )

        trigger_types_text = "\n".join(f"- {t}" for t in TRIGGER_TYPES)

        prompt = f"""Analyze these news articles about {company_name} to identify buying triggers for enterprise software.

ARTICLES:
{articles_text}

TRIGGER TYPES TO LOOK FOR:
{trigger_types_text}

TASK:
1. Read each article carefully
2. Identify if any article indicates a HIGH-IMPACT buying trigger
3. Focus on events that suggest the company may need new enterprise software (HR systems, ERP, cloud infrastructure, etc.)

Respond with a JSON object:
{{
    "has_trigger": true/false,
    "trigger_type": "The specific trigger type from the list above (or empty string if none)",
    "summary": "2-3 sentence summary of the trigger event and why it indicates software buying potential (or empty string if none)",
    "article_index": 1-based index of the most relevant article (or 0 if none)
}}

Only return the JSON, no other text."""

        try:
            response = self.client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=500,
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

            if not result.get("has_trigger"):
                return None

            # Get the referenced article
            article_idx = result.get("article_index", 1) - 1
            if 0 <= article_idx < len(articles):
                article = articles[article_idx]
            else:
                article = articles[0]  # Fallback to first article

            return TriggerResult(
                has_trigger=True,
                trigger_type=result.get("trigger_type", ""),
                summary=result.get("summary", ""),
                article_url=article.url,
                article_date=article.published_at,
            )

        except Exception as e:
            print(f"  Warning: Analysis error for {company_name}: {e}")
            return None
