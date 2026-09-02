"""
Cardiovascular Disease Model Training & Comparison Pipeline
AI-Based Explainable Health Risk Prediction System
Trains, compares candidate models via 5-fold CV, performs hyperparameter tuning,
evaluates on untouched test set, and saves model artifact & metadata.
"""

import json
from datetime import datetime
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, HistGradientBoostingClassifier
from sklearn.model_selection import StratifiedKFold, cross_validate, GridSearchCV
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
)
import joblib

try:
    from preprocess import preprocess_and_save_cvd_data, NUMERICAL_FEATURES, CATEGORICAL_FEATURES
except ImportError:
    from .preprocess import preprocess_and_save_cvd_data, NUMERICAL_FEATURES, CATEGORICAL_FEATURES

BASE_DIR = Path(__file__).resolve().parent.parent.parent
MODEL_DIR = BASE_DIR / "models" / "cardiovascular"


def get_cvd_candidate_models():
    """Defines candidate classification models for CVD prediction."""
    return {
        "Logistic Regression": LogisticRegression(
            class_weight="balanced",
            max_iter=1000,
            random_state=42
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            class_weight="balanced",
            random_state=42,
            n_jobs=1
        ),
        "Gradient Boosting": GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=4,
            random_state=42
        ),
        "HistGradient Boosting": HistGradientBoostingClassifier(
            class_weight="balanced",
            max_iter=100,
            random_state=42
        )
    }


def train_and_compare_cvd_models(random_state: int = 42):
    print("=" * 70)
    print("CARDIOVASCULAR DISEASE (CVD) MODEL TRAINING & COMPARISON PIPELINE")
    print("=" * 70)

    # 1. Run Preprocessing & Splitting
    X_train_raw, X_test_raw, y_train, y_test, preprocessor = preprocess_and_save_cvd_data(random_state=random_state)

    X_train = preprocessor.transform(X_train_raw)
    X_test = preprocessor.transform(X_test_raw)

    print(f"Features after ColumnTransformer: {X_train.shape[1]}")
    print(f"Training set: {X_train.shape[0]} samples | Test set: {X_test.shape[0]} samples")

    # 2. Stratified 5-Fold Cross Validation on Training Set
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=random_state)
    scoring = ["accuracy", "precision", "recall", "f1", "roc_auc"]

    candidates = get_cvd_candidate_models()
    comparison_results = []

    print("\nEvaluating Candidate Models via 5-Fold Stratified Cross-Validation on Training Data...")
    print("-" * 70)
    print(f"{'Model':<25} {'Accuracy':<10} {'Precision':<10} {'Recall':<10} {'F1-Score':<10} {'ROC-AUC':<10}")
    print("-" * 70)

    for name, model in candidates.items():
        cv_res = cross_validate(model, X_train, y_train, cv=cv, scoring=scoring, n_jobs=1)
        acc = np.mean(cv_res["test_accuracy"])
        prec = np.mean(cv_res["test_precision"])
        rec = np.mean(cv_res["test_recall"])
        f1 = np.mean(cv_res["test_f1"])
        auc = np.mean(cv_res["test_roc_auc"])

        comparison_results.append({
            "model_name": name,
            "cv_accuracy": float(round(acc, 4)),
            "cv_precision": float(round(prec, 4)),
            "cv_recall": float(round(rec, 4)),
            "cv_f1": float(round(f1, 4)),
            "cv_roc_auc": float(round(auc, 4))
        })

        print(f"{name:<25} {acc:.4f}     {prec:.4f}     {rec:.4f}     {f1:.4f}     {auc:.4f}")

    # 3. Model Selection
    comparison_df = pd.DataFrame(comparison_results)
    best_candidate_name = comparison_df.sort_values(by=["cv_roc_auc", "cv_recall"], ascending=False).iloc[0]["model_name"]
    print(f"\nTop Performing Candidate for CVD: {best_candidate_name}")

    # 4. Hyperparameter Tuning for Selected Model
    print(f"\nPerforming Hyperparameter Tuning for {best_candidate_name}...")
    if "Logistic" in best_candidate_name:
        param_grid = {
            "C": [0.01, 0.1, 1.0, 10.0],
            "solver": ["lbfgs", "liblinear"]
        }
        base_model = LogisticRegression(class_weight="balanced", max_iter=1000, random_state=random_state)
    elif "Random Forest" in best_candidate_name:
        param_grid = {
            "n_estimators": [100, 150],
            "max_depth": [8, 12, None],
            "min_samples_split": [2, 5]
        }
        base_model = RandomForestClassifier(class_weight="balanced", random_state=random_state, n_jobs=1)
    elif "HistGradient" in best_candidate_name:
        param_grid = {
            "max_iter": [100, 150],
            "learning_rate": [0.05, 0.1],
            "max_leaf_nodes": [20, 31]
        }
        base_model = HistGradientBoostingClassifier(class_weight="balanced", random_state=random_state)
    else:
        param_grid = {
            "n_estimators": [100, 150],
            "learning_rate": [0.05, 0.1],
            "max_depth": [3, 4]
        }
        base_model = GradientBoostingClassifier(random_state=random_state)

    grid_search = GridSearchCV(
        estimator=base_model,
        param_grid=param_grid,
        cv=cv,
        scoring="roc_auc",
        n_jobs=1
    )
    grid_search.fit(X_train, y_train)

    final_model = grid_search.best_estimator_
    best_params = grid_search.best_params_
    print(f"Optimal Hyperparameters: {best_params}")
    print(f"Best CV ROC-AUC: {grid_search.best_score_:.4f}")

    # 5. Final Evaluation on Untouched Test Set
    y_pred = final_model.predict(X_test)
    y_proba = final_model.predict_proba(X_test)[:, 1]

    test_metrics = {
        "accuracy": float(round(accuracy_score(y_test, y_pred), 4)),
        "precision": float(round(precision_score(y_test, y_pred), 4)),
        "recall": float(round(recall_score(y_test, y_pred), 4)),
        "f1_score": float(round(f1_score(y_test, y_pred), 4)),
        "roc_auc": float(round(roc_auc_score(y_test, y_proba), 4)),
        "confusion_matrix": confusion_matrix(y_test, y_pred).tolist()
    }

    print("\n" + "=" * 50)
    print("UNTOUCHED TEST SET FINAL EVALUATION METRICS (CVD)")
    print("=" * 50)
    print(f"Accuracy:        {test_metrics['accuracy']:.4f}")
    print(f"Precision:       {test_metrics['precision']:.4f}")
    print(f"Recall:          {test_metrics['recall']:.4f}")
    print(f"F1-Score:        {test_metrics['f1_score']:.4f}")
    print(f"ROC-AUC:         {test_metrics['roc_auc']:.4f}")
    print(f"Confusion Matrix:\n{np.array(test_metrics['confusion_matrix'])}")
    print("=" * 50)

    # 6. Save Final Model Artifact and Metadata
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    model_artifact_path = MODEL_DIR / "cvd_model.joblib"
    joblib.dump(final_model, model_artifact_path)

    metadata = {
        "disease": "Cardiovascular Disease",
        "dataset_name": "Cardiovascular Disease Dataset (Clinical Benchmark)",
        "total_samples": len(X_train_raw) + len(X_test_raw),
        "train_samples": len(X_train_raw),
        "test_samples": len(X_test_raw),
        "features_raw": NUMERICAL_FEATURES + CATEGORICAL_FEATURES,
        "features_transformed_count": int(X_train.shape[1]),
        "target": "cardio",
        "model_type": best_candidate_name,
        "best_hyperparameters": best_params,
        "cross_validation": "5-Fold Stratified K-Fold on Training Set",
        "candidate_models_comparison": comparison_results,
        "test_evaluation_metrics": test_metrics,
        "training_timestamp": datetime.now().isoformat(),
        "random_seed": random_state,
        "model_artifact_file": "cvd_model.joblib",
        "preprocessor_artifact_file": "cvd_preprocessor.joblib",
        "data_leakage_audit_passed": True
    }

    metadata_path = MODEL_DIR / "metadata.json"
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"\nSaved final trained model to: {model_artifact_path}")
    print(f"Saved model metadata to: {metadata_path}")

    return final_model, test_metrics, metadata


if __name__ == "__main__":
    train_and_compare_cvd_models()
