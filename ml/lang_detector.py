import re
from langdetect import detect, DetectorFactory
from typing import Tuple

# Seed language detector for deterministic results
DetectorFactory.seed = 42

# Unicode ranges for major Indian scripts
INDIAN_SCRIPT_RANGES = {
    "hi_devanagari": (0x0900, 0x097F),
    "te_telugu": (0x0C00, 0x0C7F),
    "ta_tamil": (0x0B80, 0x0BFF),
    "kn_kannada": (0x0C80, 0x0CFF),
    "ml_malayalam": (0x0D00, 0x0D7F),
    "bn_bengali": (0x0980, 0x09FF),
}

# Common Hinglish marker words
HINGLISH_KEYWORDS = {
    "bhai", "kya", "hai", "nahi", "tha", "hoga", "match", "yaar", "mast", 
    "bakwas", "dekho", "aaj", "accha", "acha", "sahi", "galat", "kaise", 
    "karte", "bolo", "desh", "waale", "bawaal", "paisa", "vasool"
}


def detect_script_language(text: str) -> str:
    """
    Checks if characters belong to Indian script unicode blocks.
    """
    script_counts = {k: 0 for k in INDIAN_SCRIPT_RANGES}
    total_chars = 0

    for char in text:
        cp = ord(char)
        total_chars += 1
        for script, (start, end) in INDIAN_SCRIPT_RANGES.items():
            if start <= cp <= end:
                script_counts[script] += 1

    for script, count in script_counts.items():
        if total_chars > 0 and (count / total_chars) > 0.20:
            return script.split("_")[0]  # Return 'hi', 'te', 'ta', etc.

    return "unknown"


def is_hinglish(text: str) -> bool:
    """
    Checks if Latin script text contains transliterated Hindi/Hinglish patterns.
    """
    tokens = set(re.findall(r"\b\w+\b", text.lower()))
    matches = tokens.intersection(HINGLISH_KEYWORDS)
    return len(matches) >= 2 or (len(tokens) <= 4 and len(matches) >= 1)


def route_language(text: str) -> Tuple[str, str]:
    """
    Returns (detected_language_code, script_category)
    Examples:
      - "India won the match" -> ("en", "latin")
      - "చాలా బాగుంది" -> ("te", "indic_native")
      - "bhai kya mast match tha" -> ("hi-en", "hinglish")
    """
    if not text or not text.strip():
        return ("en", "latin")

    # 1. First check Indian native scripts via unicode
    script_lang = detect_script_language(text)
    if script_lang != "unknown":
        return (script_lang, "indic_native")

    # 2. Check for Hinglish code-mixed latin text
    if is_hinglish(text):
        return ("hi-en", "hinglish")

    # 3. Fallback to statistical language detector
    try:
        lang = detect(text)
        return (lang, "latin" if lang in ["en", "es", "fr", "de"] else "other")
    except Exception:
        return ("en", "latin")
