from typing import List, Dict, Any
from collections import Counter
import re
from collectors.models import Comment

STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "with",
    "by", "about", "against", "between", "into", "through", "during", "before",
    "after", "above", "below", "from", "up", "down", "of", "off", "over", "under",
    "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "do",
    "does", "did", "can", "could", "shall", "should", "will", "would", "may",
    "might", "must", "it", "its", "this", "that", "these", "those", "i", "you",
    "he", "she", "we", "they", "me", "him", "her", "us", "them", "my", "your",
    "his", "their", "what", "which", "who", "whom", "where", "when", "why", "how",
    "all", "any", "both", "each", "few", "more", "most", "other", "some", "such",
    "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very", "s",
    "t", "just", "don", "now", "here", "there", "also", "like", "get", "see", "one"
}


def extract_top_keywords(comments: List[Comment], top_k: int = 15) -> List[Dict[str, Any]]:
    """
    Extracts top meaningful keywords and bigrams from cleaned comment text.
    """
    if not comments:
        return []

    word_counts = Counter()
    for c in comments:
        text = c.cleaned_text.lower() if c.cleaned_text else c.raw_text.lower()
        tokens = re.findall(r"\b[a-zA-Z]{3,}\b", text)
        filtered = [w for w in tokens if w not in STOPWORDS]
        word_counts.update(filtered)

    top_pairs = word_counts.most_common(top_k)
    return [{"word": word, "count": count} for word, count in top_pairs]
