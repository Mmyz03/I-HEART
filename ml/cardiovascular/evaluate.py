"""
Cardiovascular Disease Model Evaluation Module
AI-Based Explainable Health Risk Prediction System
Loads saved CVD model & preprocessor, evaluates on test data, generates detailed metrics & confusion matrix.
"""

from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.metrics import (
    classification_report, confusion_matrix, roc_auc_score,
    accuracy_score, precision_score, recall_score, f1_score,
    average_precision_score
)
import joblib

try:
    from preprocess import load_raw_cvd_data, split_cvd_data
except ImportError:
    from .preprocess import load_raw_cvd_data, split_cvd_data

BASE_DIR = Path(__file__).resolve().parent.parent.parent
MODEL_DIR = BASE_DIR / "models" / "cardiovascular"


def evaluate_saved_cvd_model(operating_threshold: float = 0.48):
    print("=" * 65)
    print("CARDIOVASCULAR DISEASE SAVED MODEL INDEPENDENT EVALUATION")
    print("=" * 65)

    model_path = MODEL_DIR / "cvd_model.joblib"
    preprocessor_path = MODEL_DIR / "cvd_preprocessor.joblib"

    if not model_path.exists() or not preprocessor_path.exists():
        raise FileNotFoundError(f"Model artifacts not found in {MODEL_DIR}. Please run ml/cardiovascular/train.py first.")

    model = joblib.load(model_path)
    preprocessor = joblib.load(preprocessor_path)

    # Load test split
    df = load_raw_cvd_data()
    _, X_test, _, y_test = split_cvd_data(df, test_size=0.2, random_state=42)

    X_test_transformed = preprocessor.transform(X_test)
    y_proba = model.predict_proba(X_test_transformed)[:, 1]

    # Metrics at baseline threshold (0.50)
    y_pred_base = (y_proba >= 0.50).astype(int)
    cm_base = confusion_matrix(y_test, y_pred_base)
    acc_base = accuracy_score(y_test, y_pred_base)
    prec_base = precision_score(y_test, y_pred_base)
    rec_base = recall_score(y_test, y_pred_base)
    f1_base = f1_score(y_test, y_pred_base)

    # Metrics at optimized clinical operating threshold
    y_pred_opt = (y_proba >= operating_threshold).astype(int)
    cm_opt = confusion_matrix(y_test, y_pred_opt)
    acc_opt = accuracy_score(y_test, y_pred_opt)
    prec_opt = precision_score(y_test, y_pred_opt)
    rec_opt = recall_score(y_test, y_pred_opt)
    f1_opt = f1_score(y_test, y_pred_opt)
    spec_opt = cm_opt[0, 0] / (cm_opt[0, 0] + cm_opt[0, 1])

    roc_auc = roc_auc_score(y_test, y_proba)
    pr_auc = average_precision_score(y_test, y_proba)

    print(f"Loaded Model:              {type(model).__name__}")
    print(f"ROC-AUC Score:             {roc_auc:.4f}")
    print(f"PR-AUC (Avg Precision):    {pr_auc:.4f}")
    print("\n--- BASELINE OPERATING POINT (Threshold: 0.50) ---")
    print(f"Accuracy:    {acc_base:.4f} | Precision: {prec_base:.4f} | Recall: {rec_base:.4f} | F1: {f1_base:.4f}")
    print(f"Confusion:   TN={cm_base[0, 0]}, FP={cm_base[0, 1]}, FN={cm_base[1, 0]}, TP={cm_base[1, 1]}")
    print(f"\n--- SENSITIVITY-OPTIMIZED OPERATING POINT (Threshold: {operating_threshold:.2f}) ---")
    print(f"Accuracy:    {acc_opt:.4f} | Precision: {prec_opt:.4f} | Recall: {rec_opt:.4f} | F1: {f1_opt:.4f} | Specificity: {spec_opt:.4f}")
    print(f"Confusion:   TN={cm_opt[0, 0]}, FP={cm_opt[0, 1]}, FN={cm_opt[1, 0]}, TP={cm_opt[1, 1]}")
    print(f"\nDetailed Classification Report at Threshold {operating_threshold:.2f}:")
    print(classification_report(y_test, y_pred_opt, target_names=["No CVD (0)", "CVD Present (1)"]))
    print("=" * 65)

    return {
        "roc_auc": roc_auc,
        "pr_auc": pr_auc,
        "operating_threshold": operating_threshold,
        "accuracy": acc_opt,
        "precision": prec_opt,
        "recall": rec_opt,
        "f1_score": f1_opt,
        "specificity": spec_opt,
        "confusion_matrix": cm_opt
    }


if __name__ == "__main__":
    evaluate_saved_cvd_model()
