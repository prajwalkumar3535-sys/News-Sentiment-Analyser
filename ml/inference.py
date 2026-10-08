import os
import joblib
from pathlib import Path
from typing import List, Dict, Any, Optional

from config import SentimentLabel, config
from ml.preprocessor import clean_social_text
from ml.lang_detector import route_language

# Emotion mapping lexicons
EMOTION_PATTERNS = {
    "Joy & Excitement 🔥": ["fire", "win", "amazing", "great", "best", "mast", "love", "heart", "victory", "proud", "shandar", "zabardast", "🎉", "🔥", "❤️", "🏆"],
    "Optimism & Hope 🌟": ["hope", "relief", "progress", "initiative", "promising", "growth", "improvement", "forward", "clean", "solution", "✨", "🙏"],
    "Anger & Frustration 😡": ["worst", "pathetic", "scam", "corrupt", "disaster", "hate", "shame", "furious", "terrible", "bakwas", "ghatiya", "angry", "rage", "ruined", "waste", "😡", "😤", "🤬", "👎"],
    "Sadness & Empathy 💔": ["tragedy", "died", "loss", "heartbreaking", "victim", "rip", "unfortunate", "grief", "condolences", "devastating", "sad", "suffering", "homeless", "💔", "😢", "😭"],
    "Surprise & Shock ⚡": ["shocking", "unbelievable", "unexpected", "sudden", "insane", "bawaal", "wild", "khatarnak", "alert", "huge", "😲", "🚨", "⚡"],
    "Neutral & Informative 📰": ["report", "schedule", "update", "meeting", "announced", "statement", "timeline", "session", "official", "forecast", "measured", "opened", "📌", "📄"]
}


class SentimentInferenceEngine:
    """
    Production-grade sentiment analysis engine supporting:
    1. Pre-trained Social Transformers (RoBERTa)
    2. Serialized Scikit-Learn Baseline (TF-IDF + LinearSVC)
    3. Multilingual & Hinglish Social Text Handling
    4. Compound Intensity & Emotion Detection
    """

    def __init__(self):
        self.transformer_pipeline = None
        self.baseline_pipeline = None
        self._load_models()

    def _load_models(self):
        # 1. Load Baseline Model if present
        if config.baseline_model_path.exists():
            try:
                self.baseline_pipeline = joblib.load(config.baseline_model_path)
            except Exception as e:
                print(f"[ML Engine] Warning: Could not load baseline model: {e}")
        
        # 2. Lazy load / initialize Transformer
        try:
            from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
            model_name = config.transformer_model_name
            # Uses fast local cache if downloaded, otherwise will fetch once
            self.transformer_pipeline = pipeline(
                "sentiment-analysis",
                model=model_name,
                tokenizer=model_name,
                return_all_scores=True,
                device=-1  # CPU safe by default
            )
            print(f"[ML Engine] HuggingFace Transformer model '{model_name}' loaded successfully.")
        except Exception as e:
            print(f"[ML Engine] Note: Transformer pipeline not initialized ({e}). Using optimized baseline engine.")

    def _infer_transformer(self, text: str) -> Dict[str, Any]:
        """
        Runs CardiffNLP Twitter-RoBERTa / HuggingFace model inference.
        """
        # Truncate to 512 tokens safe limit
        truncated_text = text[:512]
        scores_list = self.transformer_pipeline(truncated_text)[0]
        
        # CardiffNLP outputs labels: 'negative' (or label_0), 'neutral' (or label_1), 'positive' (or label_2)
        prob_map = {"Positive": 0.0, "Neutral": 0.0, "Negative": 0.0}
        for item in scores_list:
            lbl = item["label"].lower()
            val = float(item["score"])
            if "pos" in lbl or lbl == "label_2":
                prob_map["Positive"] = val
            elif "neu" in lbl or lbl == "label_1":
                prob_map["Neutral"] = val
            elif "neg" in lbl or lbl == "label_0":
                prob_map["Negative"] = val

        return prob_map

    def _infer_baseline(self, text: str) -> Dict[str, Any]:
        """
        Runs TF-IDF + Calibrated LinearSVC baseline inference.
        """
        if self.baseline_pipeline is None:
            # Fallback heuristic if baseline is not trained yet
            return {"Positive": 0.33, "Neutral": 0.34, "Negative": 0.33}

        probs = self.baseline_pipeline.predict_proba([text])[0]
        classes = self.baseline_pipeline.classes_
        prob_map = {"Positive": 0.0, "Neutral": 0.0, "Negative": 0.0}
        for cls, p in zip(classes, probs):
            prob_map[cls] = float(p)
        return prob_map

    def _detect_dominant_emotion(self, text: str, sentiment: SentimentLabel) -> str:
        """
        Infers emotion nuance from text tokens & sentiment direction.
        """
        lower = text.lower()
        matched_scores = {}
        for emotion, keywords in EMOTION_PATTERNS.items():
            score = sum(1 for kw in keywords if kw in lower)
            if score > 0:
                matched_scores[emotion] = score

        if matched_scores:
            return max(matched_scores, key=matched_scores.get)

        # Fallback based on sentiment
        if sentiment == SentimentLabel.POSITIVE:
            return "Joy & Excitement 🔥"
        elif sentiment == SentimentLabel.NEGATIVE:
            return "Anger & Frustration 😡"
        else:
            return "Neutral & Informative 📰"

    def analyze_text(self, raw_text: str) -> Dict[str, Any]:
        """
        Main entry point: cleans, detects language, and performs sentiment inference.
        """
        if not raw_text or not raw_text.strip():
            return {
                "cleaned_text": "",
                "language": "en",
                "sentiment": SentimentLabel.NEUTRAL,
                "confidence": 1.0,
                "probabilities": {"Positive": 0.0, "Neutral": 1.0, "Negative": 0.0},
                "compound_score": 0.0,
                "dominant_emotion": "Neutral & Informative 📰",
            }

        # 1. Clean and normalize text
        cleaned_text = clean_social_text(raw_text)
        
        # 2. Detect language / script
        lang_code, script_type = route_language(raw_text)

        # 3. Model Inference (Transformer if available, else Baseline)
        if self.transformer_pipeline is not None:
            try:
                prob_map = self._infer_transformer(cleaned_text)
            except Exception:
                prob_map = self._infer_baseline(cleaned_text)
        else:
            prob_map = self._infer_baseline(cleaned_text)

        # 4. Determine Winner Label
        max_label_str = max(prob_map, key=prob_map.get)
        if max_label_str == "Positive":
            winner_sentiment = SentimentLabel.POSITIVE
        elif max_label_str == "Negative":
            winner_sentiment = SentimentLabel.NEGATIVE
        else:
            winner_sentiment = SentimentLabel.NEUTRAL

        confidence = prob_map[max_label_str]

        # 5. Calculate Compound Sentiment Score in [-1.0, +1.0]
        compound_score = round(prob_map["Positive"] - prob_map["Negative"], 4)

        # 6. Extract Nuanced Emotion
        dominant_emotion = self._detect_dominant_emotion(cleaned_text + " " + raw_text, winner_sentiment)

        return {
            "cleaned_text": cleaned_text,
            "language": lang_code,
            "sentiment": winner_sentiment,
            "confidence": round(confidence, 4),
            "probabilities": {k: round(v, 4) for k, v in prob_map.items()},
            "compound_score": compound_score,
            "dominant_emotion": dominant_emotion,
        }

    def batch_analyze(self, comments: List[Any]) -> List[Any]:
        """
        Enriches a list of Comment objects in-place with sentiment predictions.
        """
        for c in comments:
            res = self.analyze_text(c.raw_text)
            c.cleaned_text = res["cleaned_text"]
            c.language = res["language"]
            c.sentiment = res["sentiment"]
            c.confidence = res["confidence"]
            c.probabilities = res["probabilities"]
            c.compound_score = res["compound_score"]
            c.dominant_emotion = res["dominant_emotion"]
        return comments


# Singleton instance for efficient reuse across the app
ml_engine = SentimentInferenceEngine()
