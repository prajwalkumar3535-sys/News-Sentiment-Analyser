import time
from typing import List, Tuple, Dict
from collectors.models import Comment, PlatformSummary
from collectors.youtube_collector import YouTubeCollector
from collectors.reddit_collector import RedditCollector
from collectors.news_collector import NewsRSSCollector
from collectors.mock_collector import MockSocialCollector
from config import PlatformType


class SocialMediaCollectorManager:
    """
    Coordinates multi-platform collection across YouTube, Reddit, News RSS, and Mock Fallback.
    Ensures that if one platform fails, the rest continue without interruption.
    """

    def __init__(self):
        self.youtube_collector = YouTubeCollector()
        self.reddit_collector = RedditCollector()
        self.news_collector = NewsRSSCollector()
        self.mock_collector = MockSocialCollector()

    def collect_all(
        self, 
        query: str, 
        category: str = "All Categories", 
        limit_per_platform: int = 50,
        enable_mock_fallback: bool = True
    ) -> Tuple[List[Comment], Dict[str, PlatformSummary], List[str]]:
        """
        Gathers comments from all configured platforms.
        Returns:
            Tuple of (all_comments, platform_summaries_dict, active_sources_list)
        """
        all_comments: List[Comment] = []
        platform_summaries: Dict[str, PlatformSummary] = {}
        active_sources: List[str] = []

        # 1. YouTube
        yt_comments, yt_summary = self.youtube_collector.fetch_comments(query, category, limit_per_platform)
        platform_summaries[PlatformType.YOUTUBE.value] = yt_summary
        if yt_comments:
            all_comments.extend(yt_comments)
            active_sources.append(PlatformType.YOUTUBE.value)

        # 2. Reddit
        red_comments, red_summary = self.reddit_collector.fetch_comments(query, category, limit_per_platform)
        platform_summaries[PlatformType.REDDIT.value] = red_summary
        if red_comments:
            all_comments.extend(red_comments)
            active_sources.append(PlatformType.REDDIT.value)

        # 3. Google News RSS
        news_comments, news_summary = self.news_collector.fetch_comments(query, category, limit_per_platform // 2)
        platform_summaries[PlatformType.NEWS_RSS.value] = news_summary
        if news_comments:
            all_comments.extend(news_comments)
            active_sources.append(PlatformType.NEWS_RSS.value)

        # 4. Fallback to Mock Collector if no live API credentials are configured
        if not all_comments and enable_mock_fallback:
            mock_comments, mock_summary = self.mock_collector.fetch_comments(query, category, limit_per_platform * 2)
            platform_summaries[PlatformType.MOCK.value] = mock_summary
            all_comments.extend(mock_comments)
            active_sources.append("Simulated Multi-Platform Stream")

        # Deduplicate comments by cleaned text
        seen_texts = set()
        deduped_comments: List[Comment] = []
        for c in all_comments:
            normalized = c.raw_text.strip().lower()
            if normalized not in seen_texts and len(normalized) > 5:
                seen_texts.add(normalized)
                deduped_comments.append(c)

        return deduped_comments, platform_summaries, active_sources
