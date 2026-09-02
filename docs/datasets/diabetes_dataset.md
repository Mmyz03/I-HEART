# Diabetes Prediction Dataset Documentation

## 1. Overview & Provenance
- **Dataset Name:** Diabetes Prediction Dataset (Clinical Screening Benchmark)
- **Primary Source / Reference:** NIH / CDC / Kaggle Clinical Cohort Repository
- **Number of Records:** 30,000 samples
- **Target Variable:** `diabetes` (Binary: `0` = Non-Diabetic, `1` = Diabetic)
- **Target Class Distribution:**
  - Non-Diabetic (`0`): ~84.5%
  - Diabetic (`1`): ~15.5%

## 2. Feature Definitions

| Feature Name | Data Type | Clinical Range / Values | Description |
| :--- | :--- | :--- | :--- |
| `gender` | Categorical | `Female`, `Male`, `Other` | Biological sex of the patient |
| `age` | Numerical (Integer) | 1 – 80 years | Age in years |
| `hypertension` | Binary (Integer) | `0` (No), `1` (Yes) | History of diagnosed hypertension |
| `heart_disease` | Binary (Integer) | `0` (No), `1` (Yes) | History or family predisposition to cardiovascular disease |
| `smoking_history` | Categorical | `never`, `former`, `current`, `ever`, `not current`, `No Info` | Patient tobacco smoking status |
| `bmi` | Numerical (Float) | 10.0 – 65.0 kg/m² | Body Mass Index (weight in kg / height in m²) |
| `HbA1c_level` | Numerical (Float) | 3.5 – 9.0 % | Glycated hemoglobin level |
| `blood_glucose_level` | Numerical (Integer) | 80 – 300 mg/dL | Fasting plasma blood glucose |

## 3. Preprocessing Strategy & Leakage Prevention
- **Train/Test Splitting:** 80% Training (24,000 records) / 20% Test (6,000 records) with **Stratified sampling** to maintain target class ratio.
- **Leakage Safeguard:** All imputers, encoders, and scalers are fitted **strictly on the 80% training split**.
- **Numerical Pipeline:** `SimpleImputer(strategy='median')` followed by `StandardScaler()`.
- **Categorical Pipeline:** `SimpleImputer(strategy='most_frequent')` followed by `OneHotEncoder(handle_unknown='ignore')`.
- **Class Imbalance Strategy:** Handled via `class_weight='balanced'` in estimators rather than global oversampling to preserve natural empirical calibration.

## 4. Relationship to Unified Patient Input
The Unified Patient Health profile maps to these features directly:
- `demographics.gender` ➔ `gender`
- `demographics.age` ➔ `age`
- `medical_history.hypertension` ➔ `hypertension` (1 if true else 0)
- `medical_history.family_history_cvd` ➔ `heart_disease` (1 if true else 0)
- `lifestyle.smoking` ➔ `smoking_history`
- `physical.bmi` ➔ `bmi`
- `laboratory.hba1c` ➔ `HbA1c_level` (falls back to median imputation if optional field left blank)
- `laboratory.glucose` ➔ `blood_glucose_level`
