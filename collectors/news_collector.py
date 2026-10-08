import uuid
import urllib.parse
from datetime import datetime, timezone
from typing import List, Tuple
from collectors.base import BaseCollector
from collectors.models import Comment, PlatformSummary
from config import PlatformType


class NewsRSSCollector(BaseCollector):
    """
    Ingests public news articles, editorial opinions, and public reaction snippets
    via public RSS news feeds (zero API key needed).
    """

    def __init__(self):
        super().__init__(PlatformType.NEWS_RSS)

    def is_configured(self) -> bool:
        return True  # Public RSS feeds are always active

    def fetch_comments(
        self, 
        query: str, 
        category: str = "All Categories", 
        limit: int = 30
    ) -> Tuple[List[Comment], PlatformSummary]:
        summary = PlatformSummary(platform=PlatformType.NEWS_RSS)
        
        try:
            import feedparser

            encoded_query = urllib.parse.quote_plus(query)
            rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-IN&gl=IN&ceid=IN:en"
            
            feed = feedparser.parse(rss_url)
            comments: List[Comment] = []

            for entry in feed.entries[:limit]:
                title = entry.get("title", "")
                summary_text = entry.get("summary", "")
                link = entry.get("link", "")
                
                # Parse publication time
                try:
                    ts = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                except Exception:
                    ts = datetime.now(timezone.utc)

                # Text is title + summary
                combined_text = f"{title}. {summary_text}"
                
                if title:
                    comments.append(
                        Comment(
                            id=f"news_{uuid.uuid4().hex[:8]}",
                            platform=PlatformType.NEWS_RSS,
                            raw_text=combined_text,
                            likes_count=10,  # Baseline weight for news articles
                            timestamp=ts,
                            post_title=title,
                            post_url=link
                        )
                    )

            summary.total_comments = len(comments)
            summary.total_engagement = sum(c.likes_count for c in comments)
            return comments, summary

        except Exception as e:
            summary.is_available = False
            summary.error_message = f"News RSS Error: {str(e)}"
            return [], summary
