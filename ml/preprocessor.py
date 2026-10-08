import re
import html
import emoji

# Comprehensive slang dictionary (Internet & Indian Social Code-Mixed)
SLANG_MAP = {
    # English Social Slang
    "idk": "i do not know",
    "tbh": "to be honest",
    "ngl": "not going to lie",
    "smh": "shaking my head",
    "lmao": "laughing",
    "lmfao": "laughing loudly",
    "lol": "laughing out loud",
    "rofl": "laughing rolling on floor",
    "goat": "greatest of all time",
    "w": "win",
    "huge w": "huge win",
    "l": "loss",
    "big l": "big loss",
    "fr": "for real",
    "rn": "right now",
    "imo": "in my opinion",
    "imho": "in my humble opinion",
    "omg": "oh my god",
    "wth": "what the heck",
    "wtf": "what the heck",
    "gg": "good game",
    "rip": "rest in peace",
    "fyi": "for your information",
    "brb": "be right back",
    "afaik": "as far as i know",
    "pls": "please",
    "plz": "please",
    "thx": "thanks",
    "ty": "thank you",
    "bc": "because",
    "coz": "because",
    "cuz": "because",
    "fav": "favorite",
    "ur": "your",
    "u": "you",
    "r": "are",
    
    # Common Transliterated Hinglish / Indian Social Cues
    "mast": "great",
    "shandar": "magnificent",
    "zabardast": "fantastic",
    "badhiya": "very good",
    "khatarnak": "dangerous intense",
    "bakwas": "nonsense garbage",
    "ghatiya": "very bad low quality",
    "bekaar": "useless bad",
    "chutiya": "foolish",
    "bhai": "brother",
    "yaar": "friend",
    "bawaal": "amazing chaotic",
    "dhamaal": "super fun",
    "sahi": "correct right",
    "galat": "wrong bad",
    "chindi": "cheap",
    "paisa vasool": "worth every penny",
    "fadu": "awesome",
    "faadu": "awesome",
}

# Regex Patterns
URL_PATTERN = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)
MENTION_PATTERN = re.compile(r"@[\w_]+", re.IGNORECASE)
HTML_TAG_PATTERN = re.compile(r"<.*?>")
MULTIPLE_SPACES_PATTERN = re.compile(r"\s+")
REPEATED_CHARS_PATTERN = re.compile(r"(.)\1{2,}")  # 3 or more repeated characters


def segment_hashtag(hashtag_str: str) -> str:
    """
    Converts CamelCase hashtags into space-separated words.
    Example: #IndVsAus -> Ind Vs Aus
             #NewiPhoneLaunch -> New iPhone Launch
    """
    tag = hashtag_str.lstrip("#")
    # Split camel case: lowerToUpper or UpperUpperLower
    spaced = re.sub(r"([a-z])([A-Z])", r"\1 \2", tag)
    spaced = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1 \2", spaced)
    return spaced


def normalize_repeated_chars(text: str) -> str:
    """
    Collapses 3+ repeated characters down to 2 characters to preserve emphasis
    while normalizing words.
    Example: 'woooow' -> 'woow', 'gooooal' -> 'goal'
    """
    return REPEATED_CHARS_PATTERN.sub(r"\1\1", text)


def expand_slang(text: str) -> str:
    """
    Replaces common internet and Hinglish slang terms (both multi-word and single-word)
    with expanded equivalents.
    """
    lower_text = text
    # 1. Multi-word phrases first
    for k, v in SLANG_MAP.items():
        if " " in k:
            pattern = re.compile(re.escape(k), re.IGNORECASE)
            lower_text = pattern.sub(v, lower_text)

    # 2. Single token replacements
    tokens = lower_text.split()
    expanded = []
    for token in tokens:
        clean_tok = token.lower().strip(".,!?;:\"'")
        if clean_tok in SLANG_MAP and " " not in clean_tok:
            expanded.append(SLANG_MAP[clean_tok])
        else:
            expanded.append(token)
    return " ".join(expanded)


def process_emojis(text: str, mode: str = "demojize") -> str:
    """
    Processes emojis in the text.
    - 'demojize': converts 🔥 to ':fire:' so NLP models retain sentiment context.
    - 'preserve': leaves emojis untouched.
    """
    if mode == "demojize":
        # Convert emoji to delimited text :fire: -> ' fire '
        demojized = emoji.demojize(text, delimiters=(" ", " "))
        # Replace underscores in emoji names with spaces (e.g. 'red_heart' -> 'red heart')
        return demojized.replace("_", " ")
    return text


def clean_social_text(
    text: str,
    preserve_emojis: bool = True,
    expand_slangs: bool = True,
    normalize_hashtags: bool = True,
    remove_urls: bool = True,
    remove_mentions: bool = True,
) -> str:
    """
    Complete social media text cleaning and sentiment-preserving normalization.
    """
    if not text or not isinstance(text, str):
        return ""

    # 1. Decode HTML entities (&amp;, &lt;, etc.)
    text = html.unescape(text)

    # 2. Strip HTML tags
    text = HTML_TAG_PATTERN.sub(" ", text)

    # 3. Handle URLs
    if remove_urls:
        text = URL_PATTERN.sub(" ", text)

    # 4. Handle Mentions (@user)
    if remove_mentions:
        text = MENTION_PATTERN.sub(" ", text)

    # 5. Segment and clean hashtags
    if normalize_hashtags:
        text = re.sub(r"#\w+", lambda m: " " + segment_hashtag(m.group(0)) + " ", text)

    # 6. Normalize repeated characters ('loooove' -> 'love')
    text = normalize_repeated_chars(text)

    # 7. Expand Internet & Indian Social Slang
    if expand_slangs:
        text = expand_slang(text)

    # 8. Process emojis
    if preserve_emojis:
        text = process_emojis(text, mode="demojize")

    # 9. Normalize whitespace
    text = MULTIPLE_SPACES_PATTERN.sub(" ", text).strip()

    return text
