# Cardiovascular Disease Dataset Documentation

## 1. Overview & Provenance
- **Dataset Name:** Cardiovascular Disease (CVD) Clinical Dataset
- **Primary Source / Reference:** European Society of Cardiology / Kaggle Cardiology Benchmark
- **Number of Records:** 30,000 samples
- **Target Variable:** `cardio` (Binary: `0` = Absence of CVD, `1` = Presence of CVD)
- **Target Class Distribution:**
  - Absence of CVD (`0`): ~60.7%
  - Presence of CVD (`1`): ~39.3%

## 2. Feature Definitions

| Feature Name | Data Type | Clinical Range / Values | Description |
| :--- | :--- | :--- | :--- |
| `age` | Numerical (Integer) | Days (converted to years: 30–65 yrs) | Age of patient |
| `gender` | Categorical | `1` (Female), `2` (Male) | Biological sex code |
| `height` | Numerical (Integer) | 140 – 205 cm | Patient height in centimeters |
| `weight` | Numerical (Float) | 40.0 – 160.0 kg | Patient weight in kilograms |
| `ap_hi` | Numerical (Integer) | 90 – 200 mmHg | Systolic blood pressure |
| `ap_lo` | Numerical (Integer) | 60 – 130 mmHg | Diastolic blood pressure |
| `cholesterol` | Categorical / Ordinal | `1`: Normal (<200 mg/dL), `2`: Above Normal (200-239), `3`: High (>=240) | Total serum cholesterol category |
| `gluc` | Categorical / Ordinal | `1`: Normal (<100 mg/dL), `2`: Above Normal (100-125), `3`: High (>=126) | Glucose category |
| `smoke` | Binary | `0` (No), `1` (Yes) | Tobacco smoking status |
| `alco` | Binary | `0` (No), `1` (Yes) | Alcohol consumption status |
| `active` | Binary | `0` (No), `1` (Yes) | Physical activity status |

## 3. Preprocessing Strategy & Leakage Prevention
- **Train/Test Splitting:** 80% Training (24,000 records) / 20% Test (6,000 records) with **Stratified sampling** to maintain target class ratio.
- **Leakage Safeguard:** All imputers, encoders, and scalers are fitted **strictly on the 80% training split**.
- **Numerical Pipeline:** `SimpleImputer(strategy='median')` followed by `StandardScaler()` applied to `age`, `height`, `weight`, `ap_hi`, `ap_lo`.
- **Categorical Pipeline:** `OneHotEncoder(handle_unknown='ignore')` applied to `gender`, `cholesterol`, `gluc`, `smoke`, `alco`, `active`.
- **Class Imbalance Strategy:** Evaluated using `class_weight='balanced'` in estimators.

## 4. Relationship to Unified Patient Input
The Unified Patient Health profile maps to these features directly:
- `demographics.age` ➔ `age` (converted to years or days)
- `demographics.gender` ➔ `gender` (1 for Female, 2 for Male)
- `physical.height_cm` ➔ `height`
- `physical.weight_kg` ➔ `weight`
- `vitals.systolic_bp` ➔ `ap_hi`
- `vitals.diastolic_bp` ➔ `ap_lo`
- `laboratory.total_cholesterol` ➔ `cholesterol` (1 if <200, 2 if 200-239, 3 if >=240; defaults to 1 if not provided)
- `laboratory.glucose` ➔ `gluc` (1 if <100, 2 if 100-125, 3 if >=126)
- `lifestyle.smoking` ➔ `smoke` (1 if Current/Former else 0)
- `lifestyle.alcohol` ➔ `alco` (1 if Moderate/Frequent else 0)
- `lifestyle.physical_activity` ➔ `active` (1 if Moderate/Active else 0)
