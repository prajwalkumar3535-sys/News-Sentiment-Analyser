from typing import List, Dict, Any
import numpy as np
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score, precision_score, recall_score


def evaluate_sentiment_model(
    y_true: List[str], 
    y_pred: List[str], 
    labels: List[str] = ["Positive", "Neutral", "Negative"]
) -> Dict[str, Any]:
    """
    Computes rigorous evaluation metrics for 3-class sentiment models.
    """
    accuracy = accuracy_score(y_true, y_pred)
    f1_macro = f1_score(y_true, y_pred, labels=labels, average="macro", zero_division=0)
    f1_weighted = f1_score(y_true, y_pred, labels=labels, average="weighted", zero_division=0)
    precision_macro = precision_score(y_true, y_pred, labels=labels, average="macro", zero_division=0)
    recall_macro = recall_score(y_true, y_pred, labels=labels, average="macro", zero_division=0)
    
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    report_dict = classification_report(y_true, y_pred, labels=labels, output_dict=True, zero_division=0)
    
    return {
        "accuracy": float(accuracy),
        "f1_macro": float(f1_macro),
        "f1_weighted": float(f1_weighted),
        "precision_macro": float(precision_macro),
        "recall_macro": float(recall_macro),
        "confusion_matrix": cm.tolist(),
        "labels": labels,
        "detailed_report": report_dict,
    }
