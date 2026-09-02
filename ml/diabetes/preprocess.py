"""
Diabetes Preprocessing Pipeline
AI-Based Explainable Health Risk Prediction System
Builds and fits preprocessor on training data strictly to avoid data leakage.
"""

from pathlib import Path
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
import joblib

BASE_DIR = Path(__file__).resolve().parent.parent.parent
RAW_DATA_PATH = BASE_DIR / "datasets" / "diabetes" / "raw" / "diabetes_prediction_dataset.csv"
PROCESSED_DIR = BASE_DIR / "datasets" / "diabetes" / "processed"
MODEL_DIR = BASE_DIR / "models" / "diabetes"

NUMERICAL_FEATURES = ["age", "bmi", "HbA1c_level", "blood_glucose_level"]
CATEGORICAL_FEATURES = ["gender", "hypertension", "heart_disease", "smoking_history"]
TARGET_COL = "diabetes"


def load_raw_data(file_path: Path = RAW_DATA_PATH) -> pd.DataFrame:
    """Loads raw diabetes dataset from CSV."""
    if not file_path.exists():
        raise FileNotFoundError(f"Raw diabetes dataset not found at {file_path}. Run datasets/download_datasets.py first.")
    df = pd.read_csv(file_path)
    return df


def split_data(df: pd.DataFrame, test_size: float = 0.2, random_state: int = 42):
    """
    Splits dataset into train and test sets using stratified sampling on target.
    Leakage prevention: Split happens BEFORE any scaling or imputation.
    """
    X = df[NUMERICAL_FEATURES + CATEGORICAL_FEATURES]
    y = df[TARGET_COL]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=test_size,
        random_state=random_state,
        stratify=y
    )

    return X_train, X_test, y_train, y_test


def build_preprocessor() -> ColumnTransformer:
    """
    Builds scikit-learn ColumnTransformer for numerical and categorical features.
    """
    numeric_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ])

    categorical_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, NUMERICAL_FEATURES),
            ("cat", categorical_transformer, CATEGORICAL_FEATURES)
        ]
    )

    return preprocessor


def preprocess_and_save_data(random_state: int = 42):
    """
    Main preprocessing driver:
    1. Loads data
    2. Splits into train/test
    3. Fits preprocessor ONLY on training data
    4. Transforms train and test sets
    5. Saves processed sets and preprocessor artifact
    """
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    df = load_raw_data()
    X_train, X_test, y_train, y_test = split_data(df, test_size=0.2, random_state=random_state)

    preprocessor = build_preprocessor()

    # Fit preprocessor strictly on X_train
    X_train_transformed = preprocessor.fit_transform(X_train)
    X_test_transformed = preprocessor.transform(X_test)

    # Save preprocessor artifact
    preprocessor_path = MODEL_DIR / "diabetes_preprocessor.joblib"
    joblib.dump(preprocessor, preprocessor_path)

    # Save processed splits for reproducibility
    pd.DataFrame(X_train_transformed).to_csv(PROCESSED_DIR / "X_train.csv", index=False)
    pd.DataFrame(X_test_transformed).to_csv(PROCESSED_DIR / "X_test.csv", index=False)
    y_train.to_csv(PROCESSED_DIR / "y_train.csv", index=False)
    y_test.to_csv(PROCESSED_DIR / "y_test.csv", index=False)

    print(f"Diabetes Preprocessing complete. Train samples: {len(X_train)}, Test samples: {len(X_test)}")
    print(f"Saved preprocessor to: {preprocessor_path}")

    return X_train, X_test, y_train, y_test, preprocessor


if __name__ == "__main__":
    preprocess_and_save_data()
