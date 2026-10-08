import uuid
from datetime import datetime, timezone
from typing import List, Tuple
from collectors.base import BaseCollector
from collectors.models import Comment, PlatformSummary
from config import PlatformType, config


class YouTubeCollector(BaseCollector):
    """
    Ingests public video comments using the official Google YouTube Data API v3.
    """

    def __init__(self):
        super().__init__(PlatformType.YOUTUBE)
        self.api_key = config.youtube_api_key

    def is_configured(self) -> bool:
        return bool(self.api_key and self.api_key.strip())

    def fetch_comments(
        self, 
        query: str, 
        category: str = "All Categories", 
        limit: int = 50
    ) -> Tuple[List[Comment], PlatformSummary]:
        summary = PlatformSummary(platform=PlatformType.YOUTUBE)

        if not self.is_configured():
            summary.is_available = False
            summary.error_message = "YouTube API key not configured in .env (YOUTUBE_API_KEY)"
            return [], summary

        try:
            from googleapiclient.discovery import build
            from googleapiclient.errors import HttpError

            youtube = build("youtube", "v3", developerKey=self.api_key)

            # 1. Search for top relevant videos for the query
            search_query = f"{query} news" if category != "All Categories" else query
            search_response = youtube.search().list(
                q=search_query,
                part="id,snippet",
                maxResults=min(5, max(1, limit // 10)),
                type="video",
                order="relevance"
            ).execute()

            comments: List[Comment] = []
            video_items = search_response.get("items", [])

            if not video_items:
                summary.error_message = "No matching videos found for this topic."
                return [], summary

            for v in video_items:
                video_id = v["id"]["videoId"]
                video_title = v["snippet"]["title"]
                video_url = f"https://www.youtube.com/watch?v={video_id}"

                try:
                    # 2. Fetch comments for this video
                    comments_response = youtube.commentThreads().list(
                        part="snippet",
                        videoId=video_id,
                        maxResults=min(50, limit - len(comments)),
                        textFormat="plainText",
                        order="relevance"
                    ).execute()

                    for item in comments_response.get("items", []):
                        top_comment = item["snippet"]["topLevelComment"]["snippet"]
                        text = top_comment.get("textDisplay", "")
                        like_count = top_comment.get("likeCount", 0)
                        published_str = top_comment.get("publishedAt", "")
                        
                        try:
                            ts = datetime.fromisoformat(published_str.replace("Z", "+00:00"))
                        except Exception:
                            ts = datetime.now(timezone.utc)

                        if text and len(text.strip()) > 3:
                            comments.append(
                                Comment(
                                    id=f"yt_{uuid.uuid4().hex[:8]}",
                                    platform=PlatformType.YOUTUBE,
                                    raw_text=text,
                                    likes_count=like_count,
                                    timestamp=ts,
                                    post_title=video_title,
                                    post_url=video_url
                                )
                            )
                            if len(comments) >= limit:
                                break

                except HttpError as e:
                    # Some videos have comments disabled or restricted
                    if "commentsDisabled" in str(e):
                        continue
                    else:
                        print(f"[YouTubeCollector] Error fetching comments for video {video_id}: {e}")

                if len(comments) >= limit:
                    break

            summary.total_comments = len(comments)
            summary.total_engagement = sum(c.likes_count for c in comments)
            return comments, summary

        except Exception as e:
            summary.is_available = False
            summary.error_message = f"YouTube API error: {str(e)}"
            return [], summary
