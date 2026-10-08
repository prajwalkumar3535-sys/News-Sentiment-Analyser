from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class SearchRunRecord(Base):
    __tablename__ = "search_runs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    query_text = Column(String(255), nullable=False, index=True)
    category = Column(String(100), default="All Categories")
    total_comments = Column(Integer, default=0)
    positive_pct = Column(Float, default=0.0)
    neutral_pct = Column(Float, default=0.0)
    negative_pct = Column(Float, default=0.0)
    avg_compound_score = Column(Float, default=0.0)
    weighted_compound_score = Column(Float, default=0.0)
    dominant_sentiment = Column(String(50), default="Neutral")
    dominant_emotion = Column(String(100), default="Neutral")
    analyzed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    comments = relationship("CommentRecord", back_populates="search_run", cascade="all, delete-orphan")


class CommentRecord(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    search_run_id = Column(Integer, ForeignKey("search_runs.id"), nullable=False)
    platform = Column(String(50), nullable=False)
    raw_text = Column(Text, nullable=False)
    cleaned_text = Column(Text, nullable=True)
    language = Column(String(20), default="en")
    sentiment = Column(String(20), default="Neutral")
    confidence = Column(Float, default=0.0)
    compound_score = Column(Float, default=0.0)
    dominant_emotion = Column(String(100), default="Neutral")
    likes_count = Column(Integer, default=0)
    post_title = Column(String(500), nullable=True)
    post_url = Column(String(500), nullable=True)
    comment_timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    search_run = relationship("SearchRunRecord", back_populates="comments")
