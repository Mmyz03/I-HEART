# Datasets & Clinical Benchmarks

This directory contains the benchmark datasets used to train and evaluate the machine learning models in the **I-HEART** platform.

---

## Directory Structure

```
datasets/
├── README.md                          # Datasets directory documentation
├── download_datasets.py               # Benchmark ingestion & verification script
├── diabetes/                          # Type 2 Diabetes Dataset
│   ├── raw/
│   │   └── diabetes_prediction_dataset.csv # 30,000 raw samples (84.5% non-diabetic, 15.5% diabetic)
│   └── processed/                     # Preprocessed 80/20 train and test CSV splits
└── cardiovascular/                    # Cardiovascular Disease Dataset
    ├── raw/
    │   └── cardiovascular_dataset.csv # 30,000 raw samples (60.7% no CVD, 39.3% CVD)
    └── processed/                     # Preprocessed 80/20 train and test CSV splits
```

---

## Dataset Summaries

### 1. Diabetes Prediction Dataset
- **Samples**: 30,000 total records (24,000 train / 6,000 test)
- **Target**: `diabetes` (Binary: `0` = No Diabetes, `1` = Diagnosed Diabetes)
- **Class Balance**: 84.5% Class 0 / 15.5% Class 1
- **Attributes**: `gender`, `age`, `hypertension`, `heart_disease`, `smoking_history`, `bmi`, `HbA1c_level`, `blood_glucose_level`
- **Documentation**: [docs/datasets/diabetes_dataset.md](file:///e:/projects/I-HEART/docs/datasets/diabetes_dataset.md)

### 2. Cardiovascular Disease (CVD) Dataset
- **Samples**: 30,000 total records (24,000 train / 6,000 test)
- **Target**: `cardio` (Binary: `0` = No CVD, `1` = Diagnosed CVD)
- **Class Balance**: 60.7% Class 0 / 39.3% Class 1
- **Attributes**: `age`, `gender`, `height`, `weight`, `ap_hi`, `ap_lo`, `cholesterol`, `gluc`, `smoke`, `alco`, `active`
- **Documentation**: [docs/datasets/cardiovascular_dataset.md](file:///e:/projects/I-HEART/docs/datasets/cardiovascular_dataset.md)

---

## Ingestion Script
To re-generate or verify benchmark splits:
```bash
python datasets/download_datasets.py
```
