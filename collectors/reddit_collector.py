import uuid
from datetime import datetime, timezone
from typing import List, Tuple
from collectors.base import BaseCollector
from collectors.models import Comment, PlatformSummary
from config import PlatformType, config, NewsCategory

# Subreddit mapping for news categories
CATEGORY_SUBREDDITS = {
    NewsCategory.POLITICS.value: "politics+worldnews+india+geopolitics",
    NewsCategory.SPORTS.value: "sports+cricket+soccer+nba+tennis",
    NewsCategory.TECHNOLOGY.value: "technology+gadgets+artificial+programming",
    NewsCategory.ENTERTAINMENT.value: "movies+entertainment+television+bollywood",
    NewsCategory.BUSINESS.value: "business+economics+stocks+finance",
    NewsCategory.SCIENCE.value: "science+space+technology+nature",
    NewsCategory.HEALTH.value: "health+medicine+coronavirus+wellness",
    NewsCategory.EDUCATION.value: "education+colleges+science+careers",
    NewsCategory.SOCIAL_ISSUES.value: "socialissues+india+worldnews+environment",
    NewsCategory.NATURAL_DISASTERS.value: "weather+environment+disasters+climate",
    NewsCategory.WORLD_EVENTS.value: "worldnews+geopolitics+news",
    NewsCategory.BREAKING_NEWS.value: "news+worldnews+breakingnews",
}


class RedditCollector(BaseCollector):
    """
    Ingests public comments and threads from Reddit.
    Supports two modes:
    1. Authenticated OAuth mode via PRAW (if credentials are provided in .env).
    2. Zero-Auth Public Reddit JSON mode (works out of the box without any developer keys!).
    """

    def __init__(self):
        super().__init__(PlatformType.REDDIT)
        self.client_id = config.reddit_client_id
        self.client_secret = config.reddit_client_secret
        self.user_agent = config.reddit_user_agent

    def is_configured(self) -> bool:
        # True because we now have public zero-auth fallback mode!
        return True

    def _fetch_via_public_json(
        self, query: str, category: str, limit: int
    ) -> Tuple[List[Comment], PlatformSummary]:
        summary = PlatformSummary(platform=PlatformType.REDDIT)
        comments: List[Comment] = []
        
        try:
            import requests
            import urllib.parse
            
            sub_target = CATEGORY_SUBREDDITS.get(category, "all")
            encoded_query = urllib.parse.quote_plus(query)
            url = f"https://www.reddit.com/r/{sub_target}/search.json?q={encoded_query}&sort=relevance&limit=10&restrict_sr=off"
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            
            resp = requests.get(url, headers=headers, timeout=8)
            if resp.status_code == 200:
                data = resp.json()
                posts = data.get("data", {}).get("children", [])
                
                for post_wrapper in posts:
                    p = post_wrapper.get("data", {})
                    title = p.get("title", "")
                    selftext = p.get("selftext", "")
                    score = p.get("score", 0)
                    permalink = p.get("permalink", "")
                    created_utc = p.get("created_utc", datetime.now(timezone.utc).timestamp())
                    post_url = f"https://reddit.com{permalink}"
                    
                    combined_body = f"{title}. {selftext}".strip()
                    if len(combined_body) > 5:
                        comments.append(
                            Comment(
                                id=f"red_pub_{uuid.uuid4().hex[:8]}",
                                platform=PlatformType.REDDIT,
                                raw_text=combined_body[:500],
                                likes_count=score,
                                timestamp=datetime.fromtimestamp(created_utc, tz=timezone.utc),
                                post_title=title,
                                post_url=post_url,
                            )
                        )
                        if len(comments) >= limit:
                            break

                summary.total_comments = len(comments)
                summary.total_engagement = sum(c.likes_count for c in comments)
                summary.is_available = True
                return comments, summary
            else:
                summary.error_message = f"Public Reddit returned HTTP {resp.status_code}"
                return [], summary
        except Exception as e:
            summary.error_message = f"Public Reddit fetch error: {str(e)}"
            return [], summary

    def fetch_comments(
        self, 
        query: str, 
        category: str = "All Categories", 
        limit: int = 50
    ) -> Tuple[List[Comment], PlatformSummary]:
        # If PRAW credentials exist, use official OAuth client
        if bool(self.client_id and self.client_secret and self.client_id.strip()):
            try:
                import praw

                reddit = praw.Reddit(
                    client_id=self.client_id,
                    client_secret=self.client_secret,
                    user_agent=self.user_agent,
                )

                sub_target = CATEGORY_SUBREDDITS.get(category, "all")
                subreddit = reddit.subreddit(sub_target)

                comments: List[Comment] = []
                search_results = subreddit.search(query, sort="relevance", time_filter="all", limit=5)

                for submission in search_results:
                    post_title = submission.title
                    post_url = f"https://reddit.com{submission.permalink}"

                    if submission.selftext and len(submission.selftext.strip()) > 10:
                        comments.append(
                            Comment(
                                id=f"red_post_{uuid.uuid4().hex[:8]}",
                                platform=PlatformType.REDDIT,
                                raw_text=submission.selftext[:500],
                                likes_count=submission.score,
                                timestamp=datetime.fromtimestamp(submission.created_utc, tz=timezone.utc),
                                post_title=post_title,
                                post_url=post_url,
                            )
                        )

                    submission.comments.replace_more(limit=0)
                    for c in submission.comments.list():
                        body = c.body
                        if body and body not in ["[deleted]", "[removed]"] and len(body.strip()) > 5:
                            comments.append(
                                Comment(
                                    id=f"red_{uuid.uuid4().hex[:8]}",
                                    platform=PlatformType.REDDIT,
                                    raw_text=body,
                                    likes_count=c.score,
                                    timestamp=datetime.fromtimestamp(c.created_utc, tz=timezone.utc),
                                    post_title=post_title,
                                    post_url=post_url,
                                )
                            )
                            if len(comments) >= limit:
                                break

                    if len(comments) >= limit:
                        break

                summary = PlatformSummary(platform=PlatformType.REDDIT)
                summary.total_comments = len(comments)
                summary.total_engagement = sum(c.likes_count for c in comments)
                return comments, summary
            except Exception as e:
                # If PRAW fails, gracefully fallback to public JSON mode
                return self._fetch_via_public_json(query, category, limit)

        # Otherwise, directly use zero-auth public JSON mode
        return self._fetch_via_public_json(query, category, limit)
