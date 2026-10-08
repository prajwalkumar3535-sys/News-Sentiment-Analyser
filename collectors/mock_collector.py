import uuid
import random
from datetime import datetime, timedelta, timezone
from typing import List, Tuple
from collectors.base import BaseCollector
from collectors.models import Comment, PlatformSummary
from config import PlatformType, NewsCategory

# Templates for synthetic realistic social media reactions
TEMPLATES_BY_SENTIMENT = {
    "Positive": [
        "What a magnificent performance on {topic}! Truly inspiring 🔥🇮🇳",
        "bhai kya mast update hai {topic} ke baare me, dil khush ho gaya! 😂❤️",
        "Huge W for everyone involved in {topic}. Well deserved success! 🚀👏",
        "Outstanding work! {topic} is going to change everything for the better.",
        "చాలా బాగుంది {topic} గురించి వినడం! Super happy today ✨",
        "The progress on {topic} has been phenomenal this month.",
        "paisa vasool moment! Honestly the best news I heard today on {topic} 🏆",
        "Love how quickly {topic} is developing. Big respect to the entire team! 🙏",
        "This is genuinely good news. Hope this trend continues forward.",
        "Incredible achievement regarding {topic}! Made my day 🔥",
    ],
    "Neutral": [
        "Here is the latest breakdown of events regarding {topic} as reported today.",
        "According to official sources, {topic} discussions will continue tomorrow.",
        "The timeline for {topic} has been updated in the latest press release.",
        "Can someone explain the context behind this new update on {topic}?",
        "Details regarding {topic} have been submitted to the committee.",
        "Weather and scheduling update for {topic} expected by 5 PM.",
        "Meeting regarding {topic} concluded after 2 hours of deliberations.",
        "Official notification on {topic} was published on the portal.",
        "Just waiting to see how {topic} unfolds over the weekend.",
        "Data metrics regarding {topic} show steady numbers across all sectors.",
    ],
    "Negative": [
        "Worst management ever regarding {topic}. Completely ruined it! 😡👎",
        "bhai ekdum ghatiya aur bakwas decision on {topic}, total waste of time 🤮",
        "Big L for the leadership handling {topic}. Absolutely zero accountability 🤦‍♂️",
        "చాలా చెత్త పరిస్థితి, {topic} వల్ల చాలా ఇబ్బందులు పడుతున్నారు",
        "Devastating impact of {topic} on regular citizens. Heartbreaking situation 💔",
        "Terrible execution and zero planning on {topic}. Highly disappointed 😤",
        "Prices and conditions around {topic} are getting out of hand. Unacceptable!",
        "They promised changes for {topic} but nothing happened. Pure scam alert 🚨",
        "The quality has drastically gone down. Not satisfied with {topic} at all.",
        "Disastrous outcome for {topic}. Everyone is frustrated with this 😡",
    ]
}

SIMULATED_PLATFORMS = [PlatformType.YOUTUBE, PlatformType.REDDIT]


class MockSocialCollector(BaseCollector):
    """
    Generates realistic, contextual synthetic comments across multiple platforms
    for offline testing, demonstration, and fallback when API keys are missing.
    """

    def __init__(self):
        super().__init__(PlatformType.MOCK)

    def is_configured(self) -> bool:
        return True

    def fetch_comments(
        self, 
        query: str, 
        category: str = "All Categories", 
        limit: int = 60
    ) -> Tuple[List[Comment], PlatformSummary]:
        summary = PlatformSummary(platform=PlatformType.MOCK)
        comments: List[Comment] = []
        
        now = datetime.now(timezone.utc)
        sentiments = ["Positive"] * 5 + ["Neutral"] * 3 + ["Negative"] * 2  # Realistic skew

        for i in range(limit):
            chosen_sent = random.choice(sentiments)
            tmpl = random.choice(TEMPLATES_BY_SENTIMENT[chosen_sent])
            text = tmpl.format(topic=query)
            
            # Generate random timestamp within the last 48 hours
            mins_ago = random.randint(5, 48 * 60)
            comment_time = now - timedelta(minutes=mins_ago)
            
            # Assigned simulated platform
            platform = random.choice(SIMULATED_PLATFORMS)
            likes = random.randint(0, 1500) if chosen_sent != "Neutral" else random.randint(0, 200)

            comments.append(
                Comment(
                    id=f"sim_{uuid.uuid4().hex[:8]}",
                    platform=platform,
                    raw_text=text,
                    likes_count=likes,
                    timestamp=comment_time,
                    post_title=f"Public discussion on {query}",
                    post_url="https://socialmedia.com/post/demo"
                )
            )

        summary.total_comments = len(comments)
        summary.total_engagement = sum(c.likes_count for c in comments)
        return comments, summary
