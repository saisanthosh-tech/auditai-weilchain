"""
AuditAI - News Feed Tool

Tool for fetching recent crypto/DeFi/blockchain news articles.
Can be connected to any news API (NewsAPI, CryptoPanic, etc.).
"""

from __future__ import annotations
from typing import Any
import httpx
from src.tools.base import BaseTool

class NewsFeedTool(BaseTool):
    """Fetches recent cryptocurrency and blockchain news."""

    name = "news_feed"
    description = (
        "Fetches recent news articles about a cryptocurrency or blockchain topic. "
        "Input: {'topic': 'bitcoin'} or {'topic': 'defi'}. "
        "Returns a list of recent news articles with titles, sources, and summaries."
    )

    def __init__(
        self,
        api_url: str = "https://newsapi.org/v2",
        api_key: str | None = None,
    ) -> None:
        self.api_url = api_url
        self.api_key = api_key

    def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Fetch news articles for a given topic.

        Args:
            input_data: Must contain 'topic' key.
                        e.g., {'topic': 'bitcoin', 'max_results': 5}

        Returns:
            List of news articles with title, source, description, and URL.
        """
        topic = input_data.get("topic", "").strip()
        if not topic:
            raise ValueError("Missing 'topic' in input_data")

        max_results = input_data.get("max_results", 5)

        if not self.api_key:
            # Return placeholder data when API key is not configured
            return {
                "topic": topic,
                "articles": [],
                "total_results": 0,
                "note": "News API key not configured. Set NEWS_FEED_API_KEY in .env",
            }

        try:
            response = httpx.get(
                f"{self.api_url}/everything",
                params={
                    "q": f"{topic} crypto OR blockchain",
                    "sortBy": "publishedAt",
                    "pageSize": max_results,
                    "language": "en",
                    "apiKey": self.api_key,
                },
                timeout=10.0,
            )
            response.raise_for_status()
            data = response.json()

            articles = [
                {
                    "title": a.get("title"),
                    "source": a.get("source", {}).get("name"),
                    "description": a.get("description"),
                    "url": a.get("url"),
                    "published_at": a.get("publishedAt"),
                }
                for a in data.get("articles", [])[:max_results]
            ]

            return {
                "topic": topic,
                "articles": articles,
                "total_results": len(articles),
            }

        except httpx.HTTPError as e:
            raise RuntimeError(f"Failed to fetch news: {e}") from e
