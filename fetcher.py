"""
News Fetcher Service — Pulls articles from NewsAPI and RSS feeds.
"""

import feedparser
import httpx
import logging
from datetime import datetime
from backend.config import settings

logger = logging.getLogger(__name__)

RSS_FEEDS = {
    "technology": [
        "https://feeds.feedburner.com/TechCrunch",
        "https://www.theverge.com/rss/index.xml",
        "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml",
    ],
    "business": [
        "https://feeds.bloomberg.com/markets/news.rss",
        "https://www.economist.com/finance-and-economics/rss.xml",
    ],
    "science": [
        "https://rss.nytimes.com/services/xml/rss/nyt/Science.xml",
        "https://www.newscientist.com/feed/home/",
    ],
    "world": [
        "https://feeds.bbci.co.uk/news/world/rss.xml",
        "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    ],
}


def fetch_from_rss(category: str = "technology") -> list[dict]:
    """Fetch articles from RSS feeds for a given category."""
    feeds = RSS_FEEDS.get(category, RSS_FEEDS["technology"])
    articles = []

    for url in feeds:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[: settings.MAX_ARTICLES_PER_SOURCE]:
                articles.append({
                    "title": entry.get("title", ""),
                    "content": entry.get("summary", entry.get("description", "")),
                    "url": entry.get("link", ""),
                    "source": feed.feed.get("title", url),
                    "category": category,
                    "published_at": entry.get("published", datetime.utcnow().isoformat()),
                })
        except Exception as e:
            logger.warning(f"Failed to fetch RSS feed {url}: {e}")

    logger.info(f"Fetched {len(articles)} articles from RSS ({category})")
    return articles


async def fetch_from_newsapi(query: str = "AI technology", category: str = "technology") -> list[dict]:
    """Fetch articles from NewsAPI."""
    if not settings.NEWSAPI_KEY:
        logger.warning("NEWSAPI_KEY not set, skipping NewsAPI fetch.")
        return []

    url = "https://newsapi.org/v2/top-headlines"
    params = {
        "category": category,
        "language": "en",
        "pageSize": settings.MAX_ARTICLES_PER_SOURCE,
        "apiKey": settings.NEWSAPI_KEY,
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=10.0)
            response.raise_for_status()
            data = response.json()

        articles = [
            {
                "title": a.get("title", ""),
                "content": a.get("content") or a.get("description", ""),
                "url": a.get("url", ""),
                "source": a.get("source", {}).get("name", "NewsAPI"),
                "category": category,
                "published_at": a.get("publishedAt", datetime.utcnow().isoformat()),
            }
            for a in data.get("articles", [])
            if a.get("title") and "[Removed]" not in a.get("title", "")
        ]
        logger.info(f"Fetched {len(articles)} articles from NewsAPI")
        return articles

    except Exception as e:
        logger.error(f"NewsAPI fetch failed: {e}")
        return []


async def fetch_all_news(categories: list[str] = None) -> list[dict]:
    """Fetch news from all sources and categories."""
    if categories is None:
        categories = list(RSS_FEEDS.keys())

    all_articles = []
    for category in categories:
        rss_articles = fetch_from_rss(category)
        api_articles = await fetch_from_newsapi(category=category)
        all_articles.extend(rss_articles + api_articles)

    # Deduplicate by URL
    seen_urls = set()
    unique_articles = []
    for article in all_articles:
        if article["url"] not in seen_urls and article["url"]:
            seen_urls.add(article["url"])
            unique_articles.append(article)

    logger.info(f"Total unique articles fetched: {len(unique_articles)}")
    return unique_articles
