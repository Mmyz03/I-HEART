# Trained Machine Learning Models & Artifacts

This directory stores the serialized machine learning model artifacts, fitted preprocessors, and training metadata for the **I-HEART** risk prediction system.

---

## Directory Structure

```
models/
├── README.md                          # Models directory documentation
├── diabetes/                          # Type 2 Diabetes Prediction Model
│   ├── diabetes_model.joblib          # Trained Logistic Regression classifier (C=0.01, liblinear)
│   ├── diabetes_preprocessor.joblib   # Fitted ColumnTransformer (median imputer + one-hot encoder)
│   └── metadata.json                  # Training timestamp, CV scores, confusion matrix & metrics
└── cardiovascular/                    # Cardiovascular Disease (CVD) Prediction Model
    ├── cvd_model.joblib               # Trained Logistic Regression classifier (C=0.1, lbfgs)
    ├── cvd_preprocessor.joblib        # Fitted ColumnTransformer (median imputer + one-hot encoder)
    └── metadata.json                  # Training timestamp, CV scores, confusion matrix & metrics
```

---

## Artifact Specifications

### 1. Type 2 Diabetes Model
- **Algorithm**: `LogisticRegression(C=0.01, solver='liblinear', class_weight='balanced', random_state=42)`
- **Input Features**: 8 raw features mapped to 17 transformed columns
- **Performance (6,000 Untouched Test Samples)**:
  - Accuracy: `74.55%`
  - Recall (Sensitivity): `77.81%`
  - Precision: `35.48%`
  - F1-Score: `0.4874`
  - ROC-AUC: `0.8354`
- **Metadata**: [models/diabetes/metadata.json](file:///e:/projects/I-HEART/models/diabetes/metadata.json)

### 2. Cardiovascular Disease (CVD) Model
- **Algorithm**: `LogisticRegression(C=0.1, solver='lbfgs', class_weight='balanced', random_state=42)`
- **Input Features**: 11 raw features mapped to 19 transformed columns
- **Performance (6,000 Untouched Test Samples)**:
  - Accuracy: `68.43%`
  - Recall (Sensitivity): `67.77%`
  - Precision: `58.54%`
  - F1-Score: `0.6282`
  - ROC-AUC: `0.7470`
- **Metadata**: [models/cardiovascular/metadata.json](file:///e:/projects/I-HEART/models/cardiovascular/metadata.json)

---

## Preprocessing & Serialization Integrity
- Both pipelines use serialized scikit-learn `Pipeline` and `ColumnTransformer` instances saved via `joblib`.
- All transformers were fitted exclusively on 80% training splits ($24,000$ samples each) to prevent data leakage.
- Inference services lazily load artifacts into memory upon initial request and execute `.transform()` without refitting.
