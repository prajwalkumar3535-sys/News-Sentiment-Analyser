import os
from enum import Enum
from pathlib import Path
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


class NewsCategory(str, Enum):
    ALL = "All Categories"
    POLITICS = "Politics"
    SPORTS = "Sports"
    TECHNOLOGY = "Technology"
    ENTERTAINMENT = "Entertainment & Movies"
    BUSINESS = "Business & Economy"
    SCIENCE = "Science & Space"
    HEALTH = "Health & Medicine"
    EDUCATION = "Education & Careers"
    SOCIAL_ISSUES = "Social Issues & Culture"
    NATURAL_DISASTERS = "Natural Disasters & Climate"
    WORLD_EVENTS = "World Events & Geopolitics"
    BREAKING_NEWS = "Breaking News"

    @classmethod
    def list_categories(cls) -> list[str]:
        return [c.value for c in cls]


class PlatformType(str, Enum):
    YOUTUBE = "YouTube"
    REDDIT = "Reddit"
    NEWS_RSS = "News Articles & RSS"
    MOCK = "Simulated Social Feed"


class SentimentLabel(str, Enum):
    POSITIVE = "Positive"
    NEUTRAL = "Neutral"
    NEGATIVE = "Negative"


class AppConfig(BaseModel):
    # App Settings
    app_env: str = Field(default=os.getenv("APP_ENV", "development"))
    database_url: str = Field(default=os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/sentiment_analyzer.db"))
    default_comment_limit: int = Field(default=int(os.getenv("DEFAULT_COMMENT_LIMIT", "100")))
    
    # API Credentials
    youtube_api_key: str = Field(default=os.getenv("YOUTUBE_API_KEY", ""))
    reddit_client_id: str = Field(default=os.getenv("REDDIT_CLIENT_ID", ""))
    reddit_client_secret: str = Field(default=os.getenv("REDDIT_CLIENT_SECRET", ""))
    reddit_user_agent: str = Field(default=os.getenv("REDDIT_USER_AGENT", "NewsSentimentAnalyzer/1.0"))
    
    # ML Models
    transformer_model_name: str = Field(
        default=os.getenv("TRANSFORMER_MODEL_NAME", "cardiffnlp/twitter-roberta-base-sentiment-latest")
    )
    baseline_model_path: Path = Field(default=BASE_DIR / "models" / "saved" / "baseline_tfidf_linearsvc.joblib")
    
    # NLP Thresholds
    semantic_similarity_threshold: float = Field(default=float(os.getenv("SEMANTIC_SIMILARITY_THRESHOLD", "0.20")))

    @property
    def is_youtube_configured(self) -> bool:
        return bool(self.youtube_api_key and self.youtube_api_key.strip())

    @property
    def is_reddit_configured(self) -> bool:
        return bool(self.reddit_client_id and self.reddit_client_secret and self.reddit_client_id.strip())


config = AppConfig()
