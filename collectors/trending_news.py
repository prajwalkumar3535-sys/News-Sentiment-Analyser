import time
from datetime import datetime, timezone
from typing import List, Dict, Any
import feedparser

# Curated high-quality fallback news items matching categories for offline/instant-load resilience
FALLBACK_NEWS = [
    {
        "id": "pol_1",
        "category": "POLITICS",
        "title": "Ed Sheeran's tour in turmoil as opening acts drop out in solidarity with rapper Macklemore",
        "summary": "Several supporting acts have withdrawn from Ed Sheeran's tour after Macklemore's removal. These artists expressed solidarity with Macklemore and support for peace initiatives, citing their stance on human rights.",
        "source": "The Times of India",
        "time_ago": "6h ago",
        "query": "Ed Sheeran tour Macklemore controversy",
        "pos": 24, "neu": 38, "neg": 38
    },
    {
        "id": "pol_2",
        "category": "POLITICS",
        "title": "How the great gas crisis of 2030 will play out",
        "summary": "A speculative scenario explores a global natural gas crunch as shale output falters, extreme weather hits grids, and AI data centres surge domestic energy demand. Energy analysts debate policy shifts.",
        "source": "Reuters",
        "time_ago": "8h ago",
        "query": "global natural gas crisis energy policy",
        "pos": 18, "neu": 52, "neg": 30
    },
    {
        "id": "pol_3",
        "category": "POLITICS",
        "title": "US midterm elections 2026: Record diesel prices hit key battleground states",
        "summary": "Record fuel prices are putting pressure on farmers, logistics providers, and households weeks ahead of key electoral decisions. Energy supply chain constraints remain the central debate.",
        "source": "Associated Press",
        "time_ago": "4h ago",
        "query": "US midterm elections diesel energy prices",
        "pos": 15, "neu": 45, "neg": 40
    },
    {
        "id": "ent_1",
        "category": "ENTERTAINMENT",
        "title": "Christopher Nolan announces next IMAX historical epic set for 2027 global release",
        "summary": "Universal Pictures confirms Christopher Nolan's next major cinematic production will film entirely with next-generation IMAX film cameras, featuring an ensemble international cast.",
        "source": "Variety",
        "time_ago": "3h ago",
        "query": "Christopher Nolan new movie IMAX release",
        "pos": 65, "neu": 25, "neg": 10
    },
    {
        "id": "ent_2",
        "category": "ENTERTAINMENT",
        "title": "Global Box Office rebounds as original sci-fi and franchise releases top charts",
        "summary": "International theatre admissions surge across North America, Europe, and Asia with audiences embracing IMAX 70mm screenings and fresh original storytelling.",
        "source": "Deadline",
        "time_ago": "5h ago",
        "query": "Global Box Office theatrical admissions",
        "pos": 58, "neu": 30, "neg": 12
    },
    {
        "id": "spo_1",
        "category": "SPORTS",
        "title": "Champions League thriller: Dramatic 94th-minute winner secures semi-final spot",
        "summary": "A breathtaking European football clash saw underdog tactics triumph over favorites under torrential rain, sparking viral celebrations across international fan communities.",
        "source": "BBC Sport",
        "time_ago": "2h ago",
        "query": "Champions League football match reaction",
        "pos": 70, "neu": 15, "neg": 15
    },
    {
        "id": "spo_2",
        "category": "SPORTS",
        "title": "Cricket World Championship: India prepares bowling strategy ahead of marquee clash",
        "summary": "National team head coach unveils key reverse swing and spin tactics on abrasive subcontinental pitches before a sold-out stadium crowd.",
        "source": "ESPN Cricinfo",
        "time_ago": "5h ago",
        "query": "India cricket bowling tactics pitch conditions",
        "pos": 62, "neu": 28, "neg": 10
    },
    {
        "id": "bus_1",
        "category": "BUSINESS",
        "title": "GST Council to focus on systemic process reforms and digital tax compliance in October",
        "summary": "Union Finance Ministry outlines strategic simplification for small and medium enterprises, easing cross-border trade tariffs and dispute settlement timelines.",
        "source": "Moneycontrol",
        "time_ago": "4h ago",
        "query": "GST Council process reforms tax compliance",
        "pos": 48, "neu": 42, "neg": 10
    },
    {
        "id": "bus_2",
        "category": "BUSINESS",
        "title": "Global Semiconductor Alliance commits $80 Billion for next-generation 2nm fabs",
        "summary": "Major semiconductor fabrication conglomerates unite to accelerate resilient supply chains, automotive chip design, and advanced cleanroom technology.",
        "source": "Financial Times",
        "time_ago": "7h ago",
        "query": "Semiconductor fabrication investment fabs",
        "pos": 55, "neu": 35, "neg": 10
    },
    {
        "id": "tech_1",
        "category": "TECHNOLOGY",
        "title": "Meta introduces Muse Charm AI wearable ecosystem coming later this year",
        "summary": "New multimodal lightweight ambient glasses feature continuous real-time visual reasoning, local neural processing, and multi-lingual voice translation.",
        "source": "The Verge",
        "time_ago": "1h ago",
        "query": "Meta Muse Charm AI wearable smart glasses",
        "pos": 52, "neu": 33, "neg": 15
    },
    {
        "id": "tech_2",
        "category": "TECHNOLOGY",
        "title": "Open-Source AI models achieve parity with proprietary frontier systems in code generation",
        "summary": "Independent benchmark audits verify that modern open-weights architectures running locally on consumer hardware match commercial API performance.",
        "source": "TechCrunch",
        "time_ago": "3h ago",
        "query": "open source AI code generation benchmark",
        "pos": 74, "neu": 20, "neg": 6
    },
    {
        "id": "tech_3",
        "category": "TECHNOLOGY",
        "title": "Apple unveils spatial computing updates and next-gen silicon for pro creators",
        "summary": "New hardware architectures prioritize unified memory bandwidth, thermal efficiency, and developer SDKs for neural processing.",
        "source": "Ars Technica",
        "time_ago": "6h ago",
        "query": "Apple silicon spatial computing updates",
        "pos": 46, "neu": 40, "neg": 14
    }
]

CATEGORY_RSS_TOPICS = {
    "politics": "https://news.google.com/rss/search?q=politics+news&hl=en-IN&gl=IN&ceid=IN:en",
    "entertainment": "https://news.google.com/rss/headlines/section/topic/ENTERTAINMENT?hl=en-IN&gl=IN&ceid=IN:en",
    "sports": "https://news.google.com/rss/headlines/section/topic/SPORTS?hl=en-IN&gl=IN&ceid=IN:en",
    "business": "https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=en-IN&gl=IN&ceid=IN:en",
    "technology": "https://news.google.com/rss/headlines/section/topic/TECHNOLOGY?hl=en-IN&gl=IN&ceid=IN:en",
    "all": "https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en",
}


def get_trending_news(category: str = "all", limit: int = 9) -> List[Dict[str, Any]]:
    """
    Fetches real-time live categorized news headlines from Google News RSS.
    Gracefully falls back to curated items if offline or rate-limited.
    """
    cat_lower = category.lower().strip()
    feed_url = CATEGORY_RSS_TOPICS.get(cat_lower, CATEGORY_RSS_TOPICS["all"])
    
    items: List[Dict[str, Any]] = []
    try:
        feed = feedparser.parse(feed_url)
        for idx, entry in enumerate(feed.entries[:limit]):
            title = entry.get("title", "")
            if not title:
                continue
            
            # Clean title and separate source if appended by Google News " - SourceName"
            source_name = "Google News"
            if " - " in title:
                parts = title.rsplit(" - ", 1)
                clean_title = parts[0].strip()
                source_name = parts[1].strip()
            else:
                clean_title = title
            
            # Clean summary
            summary = entry.get("summary", "")
            if "<" in summary:
                # Basic strip HTML tags
                import re
                summary = re.sub(r"<[^>]+>", "", summary).strip()
            if not summary or len(summary) < 20:
                summary = f"Latest live public reporting and social reaction stream regarding {clean_title}."
            
            # Infer category tag
            card_cat = cat_lower.upper() if cat_lower != "all" else "GENERAL"
            if "POLITICS" in clean_title.upper() or "ELECTION" in clean_title.upper() or "MINISTER" in clean_title.upper() or "GOVERNMENT" in clean_title.upper():
                card_cat = "POLITICS"
            elif "CRICKET" in clean_title.upper() or "MATCH" in clean_title.upper() or "CHAMPIONS" in clean_title.upper() or "CUP" in clean_title.upper():
                card_cat = "SPORTS"
            elif "AI" in clean_title.upper() or "TECH" in clean_title.upper() or "APPLE" in clean_title.upper() or "GOOGLE" in clean_title.upper():
                card_cat = "TECHNOLOGY"
            elif "MARKET" in clean_title.upper() or "STOCK" in clean_title.upper() or "GST" in clean_title.upper() or "ECONOMY" in clean_title.upper():
                card_cat = "BUSINESS"
            elif "MOVIE" in clean_title.upper() or "TOUR" in clean_title.upper() or "FILM" in clean_title.upper() or "ACTOR" in clean_title.upper():
                card_cat = "ENTERTAINMENT"

            items.append({
                "id": f"live_{idx}",
                "category": card_cat,
                "title": clean_title,
                "summary": (summary[:220] + "...") if len(summary) > 220 else summary,
                "source": source_name,
                "time_ago": f"{idx * 2 + 1}h ago",
                "query": clean_title,
                "pos": 45, "neu": 35, "neg": 20
            })
    except Exception as e:
        print(f"[NewsFeed] RSS fetch warning: {e}")

    # If live items were retrieved, return them; otherwise filter fallback
    if items and len(items) >= 3:
        return items[:limit]

    # Return filtered fallback
    if cat_lower == "all":
        return FALLBACK_NEWS[:limit]
    
    filtered = [n for n in FALLBACK_NEWS if n["category"].lower() == cat_lower]
    return filtered if filtered else FALLBACK_NEWS[:limit]
