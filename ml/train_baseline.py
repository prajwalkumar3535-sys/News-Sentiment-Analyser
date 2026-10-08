import os
import joblib
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.pipeline import Pipeline

from ml.preprocessor import clean_social_text
from ml.evaluate import evaluate_sentiment_model

# Ensure models directory exists
MODEL_DIR = Path(__file__).resolve().parent.parent / "models" / "saved"
MODEL_DIR.mkdir(parents=True, exist_ok=True)
MODEL_SAVE_PATH = MODEL_DIR / "baseline_tfidf_linearsvc.joblib"


def build_training_corpus() -> pd.DataFrame:
    """
    Constructs a comprehensive dataset reflecting real-world news reactions,
    sports, politics, technology, entertainment, disasters, Hinglish, emojis,
    and social media nuances.
    """
    data = [
        # POSITIVE EXAMPLES (Sports, Tech, Politics, General, Hinglish, Emojis)
        ("India won the cricket match against Australia! Incredible performance 🔥🏏", "Positive"),
        ("What a magnificent victory, proud of team India! 🇮🇳❤️", "Positive"),
        ("The new AI update is lightning fast and genuinely helpful", "Positive"),
        ("Rescue teams have saved over 500 people from the flood area. Heroic effort! 🙏", "Positive"),
        ("bhai kya mast match tha, maza aa gaya ekdum paisa vasool! 😂🔥", "Positive"),
        ("చాలా అద్భుతమైన విజయం! చాలా బాగుంది", "Positive"),
        ("Huge W for renewable energy projects launched today! 🚀", "Positive"),
        ("The new movie is a masterpiece, brilliant direction and acting! 👏🎬", "Positive"),
        ("Stock market reaches all-time high as economy strengthens", "Positive"),
        ("Spacecraft successfully lands on the moon! Historic achievement! 🌕✨", "Positive"),
        ("Medical breakthrough in cancer treatment announced by scientists! Great news", "Positive"),
        ("Student scholarship scheme extended to 100,000 more candidates. Wonderful initiative", "Positive"),
        ("New expressway cuts travel time in half. Excellent infrastructure work!", "Positive"),
        ("This is the best tech launch of 2026 so far, highly recommended 🔥", "Positive"),
        ("shandar performance by both teams, true sportsmanship!", "Positive"),
        ("Government subsidy on solar panels increased, good policy for environment", "Positive"),
        ("Traffic police rescued an injured puppy on the highway ❤️ kudos to them", "Positive"),
        ("The concert in Hyderabad was pure magic! Best night ever ✨🎉", "Positive"),
        ("zabardast innings by the captain, legend for a reason! 👑", "Positive"),
        ("Inflation rate dropped significantly this quarter, great relief for families", "Positive"),
        ("The new operating system feels buttery smooth and battery life is great", "Positive"),
        ("Beautiful gesture by the athletes at the finish line! Pure inspiration", "Positive"),
        ("Clean energy investments up 40%, fantastic step for climate action", "Positive"),
        ("Super happy with the election outcome, true democracy in action!", "Positive"),

        # NEUTRAL EXAMPLES (Informational, News Reporting, Queries, Statements)
        ("The press conference is scheduled for 3 PM tomorrow.", "Neutral"),
        ("Match between India and England starts at 1:30 PM IST.", "Neutral"),
        ("Government released the preliminary report on the new budget allocation.", "Neutral"),
        ("The flight was delayed by 45 minutes due to fog.", "Neutral"),
        ("Hyderabad weather forecast predicts cloudy skies with mild breeze.", "Neutral"),
        ("Here is the full timeline of events that occurred during the summit.", "Neutral"),
        ("The company announced its quarterly earnings report this morning.", "Neutral"),
        ("Parliament session will resume on Monday to discuss the bill.", "Neutral"),
        ("Smartphone comes with 6.7 inch AMOLED display and 5000mAh battery.", "Neutral"),
        ("Metro trains will operate on regular timetable today.", "Neutral"),
        ("Police have registered a case and initiated an inquiry into the matter.", "Neutral"),
        ("School examinations will commence from next month as per notification.", "Neutral"),
        ("Reserve Bank kept repo rates unchanged in the latest monetary policy.", "Neutral"),
        ("Voting took place across 50 constituencies in the second phase.", "Neutral"),
        ("The official document can be downloaded from the state portal.", "Neutral"),
        ("Bus services on this route have been temporarily diverted.", "Neutral"),
        ("Match ended in a tie after 20 overs.", "Neutral"),
        ("Official statement released by the Ministry of External Affairs.", "Neutral"),
        ("Submissions for the science exhibition close on Friday.", "Neutral"),
        ("New bridge has been opened for light vehicles only.", "Neutral"),
        ("Rainfall measured at 45mm over the last 24 hours in the coastal belt.", "Neutral"),
        ("Ticket booking opens tomorrow at 10 AM on the official website.", "Neutral"),

        # NEGATIVE EXAMPLES (Complaints, Anger, Disasters, Criticisms, Hinglish, Disgust)
        ("Worst decision ever made by the management. Absolutely pathetic! 😡", "Negative"),
        ("Severe waterlogging and traffic chaos across the city after heavy rains 🌧️🤦‍♂️", "Negative"),
        ("The referee ruined the entire match with biased decisions! Terrible refereeing", "Negative"),
        ("Product stopped working within 2 days. Total waste of money! Do not buy 👎", "Negative"),
        ("bhai ekdum ghatiya aur bakwas decision tha, mood kharab kar diya 🤮", "Negative"),
        ("చాలా చెత్త నిర్ణయం, అసలు నచ్చలేదు", "Negative"),
        ("Devastating earthquake leaves hundreds homeless. Heartbreaking tragedy 💔", "Negative"),
        ("Prices of essential commodities skyrocket again. Unbearable burden on common man", "Negative"),
        ("Hospital negligence led to severe complications. Strict action must be taken! 🚨", "Negative"),
        ("Major train delay of 6 hours without any announcement or water. Horrible service 😤", "Negative"),
        ("The movie was completely boring and predictable. Total waste of 3 hours", "Negative"),
        ("Cyber attack leaks personal data of thousands of users. Huge security failure!", "Negative"),
        ("Roads are full of dangerous potholes, municipality does nothing! 🤦", "Negative"),
        ("Big L for the company after laying off 2000 loyal employees with zero notice", "Negative"),
        ("App keeps crashing on startup after the latest buggy update. Fix it ASAP!", "Negative"),
        ("Smog and air quality reached hazardous levels today. Breathing is difficult 😷", "Negative"),
        ("Terrible customer support, nobody answers the helpline or replies to emails", "Negative"),
        ("Corruption scandal exposed in the municipal department. Shameful! 😡", "Negative"),
        ("Flight cancelled at the last moment with zero refund or accommodation!", "Negative"),
        ("Scam alert! Several people lost money in fake investment app.", "Negative"),
        ("Power outage for 8 hours in extreme heat. Unacceptable failure!", "Negative"),
        ("The team played carelessly with zero strategy. Complete disaster", "Negative"),
    ]
    
    # Expand with variations to ensure robust vocabulary coverage
    expanded_data = []
    for text, label in data:
        expanded_data.append({"text": text, "label": label})
        # Add a lowercased or slightly noisy variant
        expanded_data.append({"text": text.lower(), "label": label})

    return pd.DataFrame(expanded_data)


def train_and_evaluate_baseline():
    print("Building training corpus...")
    df = build_training_corpus()
    
    print(f"Dataset Size: {len(df)} samples")
    print("Class distribution:\n", df["label"].value_counts())
    
    # Preprocess text
    print("Preprocessing texts...")
    df["cleaned_text"] = df["text"].apply(clean_social_text)
    
    # Train / Test split
    X_train, X_test, y_train, y_test = train_test_split(
        df["cleaned_text"], df["label"], test_size=0.25, random_state=42, stratify=df["label"]
    )
    
    print(f"Training on {len(X_train)} samples, testing on {len(X_test)} samples...")
    
    # Build ML Pipeline: TF-IDF + Calibrated LinearSVC (to get calibrated probabilities)
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=5000,
            sublinear_tf=True,
            strip_accents="unicode"
        )),
        ("classifier", CalibratedClassifierCV(LinearSVC(C=1.0, random_state=42)))
    ])
    
    pipeline.fit(X_train, y_train)
    
    # Evaluate
    y_pred = pipeline.predict(X_test)
    metrics = evaluate_sentiment_model(y_test.tolist(), y_pred.tolist())
    
    print("\n" + "="*50)
    print("  MODEL EVALUATION RESULTS")
    print("="*50)
    print(f"Accuracy:        {metrics['accuracy']:.4f}")
    print(f"Macro F1-Score:  {metrics['f1_macro']:.4f}")
    print(f"Weighted F1:     {metrics['f1_weighted']:.4f}")
    print(f"Macro Precision: {metrics['precision_macro']:.4f}")
    print(f"Macro Recall:    {metrics['recall_macro']:.4f}")
    print("\nConfusion Matrix (Rows=True, Cols=Pred [Pos, Neu, Neg]):")
    for row in metrics["confusion_matrix"]:
        print(f"  {row}")
    print("="*50)
    
    # Save trained model
    joblib.dump(pipeline, MODEL_SAVE_PATH)
    print(f"\nTrained baseline model successfully saved to: {MODEL_SAVE_PATH}")
    return pipeline, metrics


if __name__ == "__main__":
    train_and_evaluate_baseline()
