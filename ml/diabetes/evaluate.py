"""
Diabetes Model Evaluation Module
AI-Based Explainable Health Risk Prediction System
Loads saved model & preprocessor, evaluates on test data, generates detailed metrics & confusion matrix.
"""

from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, accuracy_score
import joblib

try:
    from preprocess import load_raw_data, split_data
except ImportError:
    from .preprocess import load_raw_data, split_data

BASE_DIR = Path(__file__).resolve().parent.parent.parent
MODEL_DIR = BASE_DIR / "models" / "diabetes"


def evaluate_saved_diabetes_model():
    print("=" * 60)
    print("DIABETES SAVED MODEL INDEPENDENT EVALUATION")
    print("=" * 60)

    model_path = MODEL_DIR / "diabetes_model.joblib"
    preprocessor_path = MODEL_DIR / "diabetes_preprocessor.joblib"

    if not model_path.exists() or not preprocessor_path.exists():
        raise FileNotFoundError(f"Model artifacts not found in {MODEL_DIR}. Please run ml/diabetes/train.py first.")

    model = joblib.load(model_path)
    preprocessor = joblib.load(preprocessor_path)

    # Load test split
    df = load_raw_data()
    _, X_test, _, y_test = split_data(df, test_size=0.2, random_state=42)

    X_test_transformed = preprocessor.transform(X_test)
    y_pred = model.predict(X_test_transformed)
    y_proba = model.predict_proba(X_test_transformed)[:, 1]

    acc = accuracy_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_proba)
    cm = confusion_matrix(y_test, y_pred)
    cr = classification_report(y_test, y_pred, target_names=["Non-Diabetic (0)", "Diabetic (1)"])

    print(f"Loaded Model:        {type(model).__name__}")
    print(f"Overall Accuracy:    {acc:.4f}")
    print(f"ROC-AUC Score:       {auc:.4f}")
    print("\nConfusion Matrix:")
    print(f"                 Predicted 0    Predicted 1")
    print(f"Actual 0 (No)    {cm[0, 0]:<14} {cm[0, 1]}")
    print(f"Actual 1 (Yes)   {cm[1, 0]:<14} {cm[1, 1]}")
    print("\nDetailed Classification Report:")
    print(cr)
    print("=" * 60)

    return {"accuracy": acc, "roc_auc": auc, "confusion_matrix": cm, "report": cr}


if __name__ == "__main__":
    evaluate_saved_diabetes_model()
