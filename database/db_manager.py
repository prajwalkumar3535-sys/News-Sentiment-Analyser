from datetime import datetime
from typing import List, Optional
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker, scoped_session

from config import config
from database.models import Base, SearchRunRecord, CommentRecord
from collectors.models import SearchAnalysisResult, Comment
from config import PlatformType, SentimentLabel

engine = create_engine(config.database_url, connect_args={"check_same_thread": False} if "sqlite" in config.database_url else {})
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

# Ensure tables are created
Base.metadata.create_all(bind=engine)


def save_search_analysis(result: SearchAnalysisResult) -> int:
    """
    Persists a complete search run and all analyzed comments.
    """
    session = SessionLocal()
    try:
        run_record = SearchRunRecord(
            query_text=result.query,
            category=result.category.value if hasattr(result.category, "value") else str(result.category),
            total_comments=result.total_comments,
            positive_pct=result.positive_pct,
            neutral_pct=result.neutral_pct,
            negative_pct=result.negative_pct,
            avg_compound_score=result.avg_compound_score,
            weighted_compound_score=result.weighted_compound_score,
            dominant_sentiment=result.dominant_sentiment.value if hasattr(result.dominant_sentiment, "value") else str(result.dominant_sentiment),
            dominant_emotion=result.dominant_emotion,
            analyzed_at=result.analyzed_at,
        )
        session.add(run_record)
        session.flush()

        # Add comments
        for c in result.comments:
            comm_rec = CommentRecord(
                search_run_id=run_record.id,
                platform=c.platform.value if hasattr(c.platform, "value") else str(c.platform),
                raw_text=c.raw_text,
                cleaned_text=c.cleaned_text,
                language=c.language,
                sentiment=c.sentiment.value if c.sentiment else "Neutral",
                confidence=c.confidence,
                compound_score=c.compound_score,
                dominant_emotion=c.dominant_emotion,
                likes_count=c.likes_count,
                post_title=c.post_title,
                post_url=c.post_url,
                comment_timestamp=c.timestamp,
            )
            session.add(comm_rec)

        session.commit()
        return run_record.id
    except Exception as e:
        session.rollback()
        print(f"[DB Error] Failed to save search analysis: {e}")
        return -1
    finally:
        session.close()


def get_recent_search_runs(limit: int = 10) -> List[SearchRunRecord]:
    """
    Retrieves recent search queries for history and quick-load.
    """
    session = SessionLocal()
    try:
        runs = session.query(SearchRunRecord).order_by(desc(SearchRunRecord.analyzed_at)).limit(limit).all()
        return runs
    finally:
        session.close()
