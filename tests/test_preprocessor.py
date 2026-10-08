from ml.preprocessor import clean_social_text
from ml.lang_detector import route_language


def test_emoji_and_repeated_characters():
    raw = "India wonnn the matchhh 🔥🔥🔥❤️! #IndVsAus"
    cleaned = clean_social_text(raw)
    assert "fire" in cleaned or "heart" in cleaned
    assert "won" in cleaned
    assert "Ind Vs Aus" in cleaned


def test_hinglish_slang_expansion():
    raw = "bhai kya mast match tha, pura paisa vasool"
    cleaned = clean_social_text(raw)
    assert "brother" in cleaned
    assert "great" in cleaned
    assert "worth every penny" in cleaned


def test_url_and_mention_removal():
    raw = "Check this out @virat_kohli https://cricket.com/news #Victory"
    cleaned = clean_social_text(raw)
    assert "https://" not in cleaned
    assert "@virat_kohli" not in cleaned
    assert "Victory" in cleaned


def test_language_routing():
    # English
    lang, script = route_language("India won the cricket world cup")
    assert lang == "en"
    
    # Telugu Native Script
    lang_te, script_te = route_language("చాలా బాగుంది ఈ రోజు")
    assert lang_te == "te"
    assert script_te == "indic_native"
    
    # Hindi Native Script
    lang_hi, script_hi = route_language("भारत ने मैच जीत लिया")
    assert lang_hi == "hi"
    assert script_hi == "indic_native"
    
    # Hinglish
    lang_hinglish, script_hinglish = route_language("bhai kya mast match tha")
    assert lang_hinglish == "hi-en"
    assert script_hinglish == "hinglish"


if __name__ == "__main__":
    test_emoji_and_repeated_characters()
    test_hinglish_slang_expansion()
    test_url_and_mention_removal()
    test_language_routing()
    print("All preprocessing tests passed successfully!")
