"""NewsAPI client for searching company news."""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List

from newsapi import NewsApiClient

from config import MAX_ARTICLES_PER_COMPANY, NEWS_LOOKBACK_DAYS


@dataclass
class Article:
    """Represents a news article."""
    title: str
    description: str
    url: str
    published_at: str
    source: str


class NewsClient:
    """Client for searching news via NewsAPI."""

    def __init__(self, api_key: str):
        """Initialize the NewsAPI client.

        Args:
            api_key: NewsAPI API key
        """
        self.client = NewsApiClient(api_key=api_key)

    def search_company_news(self, company_name: str) -> List[Article]:
        """Search for recent news about a company.

        Args:
            company_name: Name of the company to search for

        Returns:
            List of Article objects, sorted by relevance
        """
        # Calculate date range (past 6 months)
        to_date = datetime.now()
        from_date = to_date - timedelta(days=NEWS_LOOKBACK_DAYS)

        try:
            response = self.client.get_everything(
                q=f'"{company_name}"',  # Exact phrase match
                from_param=from_date.strftime("%Y-%m-%d"),
                to=to_date.strftime("%Y-%m-%d"),
                language="en",
                sort_by="relevancy",
                page_size=MAX_ARTICLES_PER_COMPANY,
            )
        except Exception as e:
            print(f"  Warning: NewsAPI error for {company_name}: {e}")
            return []

        articles = []
        for item in response.get("articles", []):
            # Skip articles with no real content
            if not item.get("title") or item.get("title") == "[Removed]":
                continue

            articles.append(Article(
                title=item.get("title", ""),
                description=item.get("description") or "",
                url=item.get("url", ""),
                published_at=item.get("publishedAt", "")[:10],  # Just the date
                source=item.get("source", {}).get("name", ""),
            ))

        return articles
