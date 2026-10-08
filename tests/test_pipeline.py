import pytest
from config import NewsCategory, PlatformType, SentimentLabel
from collectors.models import Comment, PlatformSummary
from collectors.mock_collector import MockSocialCollector
from collectors import SocialMediaCollectorManager
from ml.inference import ml_engine
from analytics.aggregator import aggregate_sentiment_results, compute_time_series_sentiment
from analytics.keywords import extract_top_keywords
from database.db_manager import save_search_analysis, get_recent_search_runs


def test_mock_collector_generation():
    collector = MockSocialCollector()
    comments, summary = collector.fetch_comments("India cricket victory", limit=20)
    assert len(comments) == 20
    assert summary.total_comments == 20
    assert all(c.raw_text for c in comments)


def test_ml_inference_engine():
    # Test positive text
    pos_res = ml_engine.analyze_text("India won the cricket match! Incredible performance 🔥🏏")
    assert pos_res["sentiment"] in [SentimentLabel.POSITIVE, SentimentLabel.NEUTRAL]
    assert pos_res["compound_score"] >= -0.1

    # Test negative text
    neg_res = ml_engine.analyze_text("Worst decision ever made. Completely pathetic 😡👎")
    assert neg_res["sentiment"] == SentimentLabel.NEGATIVE
    assert neg_res["compound_score"] < 0.0


def test_aggregator_analytics():
    mock_comments = [
        Comment(
            id="1", platform=PlatformType.YOUTUBE, raw_text="Super match!", 
            sentiment=SentimentLabel.POSITIVE, compound_score=0.8, likes_count=50
        ),
        Comment(
            id="2", platform=PlatformType.REDDIT, raw_text="Bad umpiring", 
            sentiment=SentimentLabel.NEGATIVE, compound_score=-0.7, likes_count=10
        ),
        Comment(
            id="3", platform=PlatformType.YOUTUBE, raw_text="Match concluded at 5 PM", 
            sentiment=SentimentLabel.NEUTRAL, compound_score=0.0, likes_count=5
        ),
    ]
    
    summaries = {
        PlatformType.YOUTUBE.value: PlatformSummary(platform=PlatformType.YOUTUBE),
        PlatformType.REDDIT.value: PlatformSummary(platform=PlatformType.REDDIT),
    }

    result = aggregate_sentiment_results(
        query="Test Match",
        category=NewsCategory.SPORTS,
        comments=mock_comments,
        platform_summaries=summaries,
        data_sources_used=["YouTube", "Reddit"],
        execution_time=0.45
    )

    assert result.total_comments == 3
    assert result.positive_count == 1
    assert result.negative_count == 1
    assert result.neutral_count == 1
    assert pytest.approx(result.positive_pct, 0.1) == 33.33


def test_database_persistence():
    mock_comments = [
        Comment(
            id="persist_1", platform=PlatformType.YOUTUBE, raw_text="Super match!", 
            sentiment=SentimentLabel.POSITIVE, compound_score=0.8, likes_count=50
        )
    ]
    summaries = {PlatformType.YOUTUBE.value: PlatformSummary(platform=PlatformType.YOUTUBE)}
    result = aggregate_sentiment_results("Test Query", NewsCategory.ALL, mock_comments, summaries, ["YouTube"], 0.1)
    
    run_id = save_search_analysis(result)
    assert run_id > 0
    
    recent = get_recent_search_runs(limit=1)
    assert len(recent) > 0
    assert recent[0].query_text == "Test Query"
