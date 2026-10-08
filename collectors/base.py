from abc import ABC, abstractmethod
from typing import List, Tuple
from collectors.models import Comment, PlatformSummary
from config import PlatformType


class BaseCollector(ABC):
    """
    Abstract Base Class for all social media and news data collectors.
    Ensures a standardized interface and resilient error handling.
    """

    def __init__(self, platform_name: PlatformType):
        self.platform_name = platform_name

    @abstractmethod
    def is_configured(self) -> bool:
        """Returns True if the API keys or required credentials are provided."""
        pass

    @abstractmethod
    def fetch_comments(
        self, 
        query: str, 
        category: str = "All Categories", 
        limit: int = 50
    ) -> Tuple[List[Comment], PlatformSummary]:
        """
        Fetches public comments/reactions for the given query and category.
        Returns:
            Tuple of (list_of_comments, platform_summary)
        """
        pass
