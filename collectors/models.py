from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from config import PlatformType, SentimentLabel, NewsCategory


class Comment(BaseModel):
    id: str
    platform: PlatformType
    raw_text: str
    cleaned_text: str = ""
    language: str = "en"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    likes_count: int = 0
    post_title: str = ""
    post_url: str = ""
    
    # ML Prediction fields
    sentiment: Optional[SentimentLabel] = None
    confidence: float = 0.0
    probabilities: Dict[str, float] = Field(default_factory=lambda: {"Positive": 0.0, "Neutral": 0.0, "Negative": 0.0})
    compound_score: float = 0.0  # Range: -1.0 (extremely negative) to +1.0 (extremely positive)
    dominant_emotion: str = "Neutral"
    
    # Relevance score
    relevance_score: float = 1.0


class PlatformSummary(BaseModel):
    platform: PlatformType
    total_comments: int = 0
    positive_count: int = 0
    neutral_count: int = 0
    negative_count: int = 0
    positive_pct: float = 0.0
    neutral_pct: float = 0.0
    negative_pct: float = 0.0
    avg_compound_score: float = 0.0
    total_engagement: int = 0  # Sum of likes/upvotes
    is_available: bool = True
    error_message: Optional[str] = None


class SearchAnalysisResult(BaseModel):
    query: str
    category: NewsCategory = NewsCategory.ALL
    analyzed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    total_comments: int = 0
    
    # Overall Sentiment Distribution
    positive_count: int = 0
    neutral_count: int = 0
    negative_count: int = 0
    positive_pct: float = 0.0
    neutral_pct: float = 0.0
    negative_pct: float = 0.0
    avg_compound_score: float = 0.0
    weighted_compound_score: float = 0.0  # Engagement-weighted
    
    dominant_sentiment: SentimentLabel = SentimentLabel.NEUTRAL
    dominant_emotion: str = "Neutral"
    
    # Top keywords & n-grams
    top_keywords: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Platform Breakdown
    platform_summaries: Dict[str, PlatformSummary] = Field(default_factory=dict)
    
    # All processed comments
    comments: List[Comment] = Field(default_factory=list)
    
    # Execution metadata
    execution_time_seconds: float = 0.0
    data_sources_used: List[str] = Field(default_factory=list)
