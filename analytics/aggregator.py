import math
from typing import List, Dict, Any
import pandas as pd
from datetime import datetime, timezone

from collectors.models import Comment, SearchAnalysisResult, PlatformSummary
from config import SentimentLabel, NewsCategory, PlatformType


def aggregate_sentiment_results(
    query: str,
    category: NewsCategory,
    comments: List[Comment],
    platform_summaries: Dict[str, PlatformSummary],
    data_sources_used: List[str],
    execution_time: float = 0.0,
) -> SearchAnalysisResult:
    """
    Computes statistical and engagement-weighted analytics over analyzed comments.
    """
    total_count = len(comments)
    if total_count == 0:
        return SearchAnalysisResult(
            query=query,
            category=category,
            total_comments=0,
            execution_time_seconds=execution_time,
            data_sources_used=data_sources_used,
        )

    pos_count = sum(1 for c in comments if c.sentiment == SentimentLabel.POSITIVE)
    neu_count = sum(1 for c in comments if c.sentiment == SentimentLabel.NEUTRAL)
    neg_count = sum(1 for c in comments if c.sentiment == SentimentLabel.NEGATIVE)

    pos_pct = round((pos_count / total_count) * 100, 2)
    neu_pct = round((neu_count / total_count) * 100, 2)
    neg_pct = round((neg_count / total_count) * 100, 2)

    # Arithmetic average compound score
    avg_compound = round(sum(c.compound_score for c in comments) / total_count, 4)

    # Engagement-weighted compound score: weight = log(1 + likes)
    weighted_compound_sum = 0.0
    total_weights = 0.0
    for c in comments:
        w = math.log1p(max(0, c.likes_count)) + 1.0  # Base weight 1.0
        weighted_compound_sum += c.compound_score * w
        total_weights += w
    
    weighted_compound = round(weighted_compound_sum / total_weights, 4) if total_weights > 0 else avg_compound

    # Determine dominant sentiment & dominant emotion
    if pos_pct >= neu_pct and pos_pct >= neg_pct:
        dominant_sentiment = SentimentLabel.POSITIVE
    elif neg_pct >= pos_pct and neg_pct >= neu_pct:
        dominant_sentiment = SentimentLabel.NEGATIVE
    else:
        dominant_sentiment = SentimentLabel.NEUTRAL

    # Find dominant emotion across all comments
    emotions = [c.dominant_emotion for c in comments if c.dominant_emotion]
    dominant_emotion = max(set(emotions), key=emotions.count) if emotions else "Neutral & Informative 📰"

    # Update platform summaries with classified numbers
    for plat_name, summary in platform_summaries.items():
        plat_comments = [c for c in comments if c.platform.value == plat_name]
        if plat_comments:
            p_tot = len(plat_comments)
            p_pos = sum(1 for c in plat_comments if c.sentiment == SentimentLabel.POSITIVE)
            p_neu = sum(1 for c in plat_comments if c.sentiment == SentimentLabel.NEUTRAL)
            p_neg = sum(1 for c in plat_comments if c.sentiment == SentimentLabel.NEGATIVE)
            summary.total_comments = p_tot
            summary.positive_count = p_pos
            summary.neutral_count = p_neu
            summary.negative_count = p_neg
            summary.positive_pct = round((p_pos / p_tot) * 100, 2)
            summary.neutral_pct = round((p_neu / p_tot) * 100, 2)
            summary.negative_pct = round((p_neg / p_tot) * 100, 2)
            summary.avg_compound_score = round(sum(c.compound_score for c in plat_comments) / p_tot, 4)
            summary.total_engagement = sum(c.likes_count for c in plat_comments)

    return SearchAnalysisResult(
        query=query,
        category=category,
        analyzed_at=datetime.now(timezone.utc),
        total_comments=total_count,
        positive_count=pos_count,
        neutral_count=neu_count,
        negative_count=neg_count,
        positive_pct=pos_pct,
        neutral_pct=neu_pct,
        negative_pct=neg_pct,
        avg_compound_score=avg_compound,
        weighted_compound_score=weighted_compound,
        dominant_sentiment=dominant_sentiment,
        dominant_emotion=dominant_emotion,
        platform_summaries=platform_summaries,
        comments=comments,
        execution_time_seconds=round(execution_time, 2),
        data_sources_used=data_sources_used,
    )


def compute_time_series_sentiment(comments: List[Comment], bins: int = 10) -> pd.DataFrame:
    """
    Aggregates comments over temporal intervals to plot sentiment progression over time.
    """
    if not comments:
        return pd.DataFrame(columns=["timestamp", "positive", "neutral", "negative", "compound_avg", "volume"])

    data = []
    for c in comments:
        data.append({
            "timestamp": c.timestamp,
            "sentiment": c.sentiment.value if c.sentiment else "Neutral",
            "compound": c.compound_score,
            "likes": c.likes_count
        })

    df = pd.DataFrame(data)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df = df.sort_values("timestamp")

    # Resample or group into time buckets
    df["time_bucket"] = pd.qcut(df["timestamp"], q=min(bins, len(df)), duplicates="drop")
    
    agg = df.groupby("time_bucket", observed=False).agg(
        timestamp=("timestamp", "mean"),
        compound_avg=("compound", "mean"),
        volume=("sentiment", "count"),
        positive=("sentiment", lambda s: (s == "Positive").sum()),
        neutral=("sentiment", lambda s: (s == "Neutral").sum()),
        negative=("sentiment", lambda s: (s == "Negative").sum()),
    ).reset_index()

    agg["compound_avg"] = agg["compound_avg"].round(3)
    return agg.sort_values("timestamp")
