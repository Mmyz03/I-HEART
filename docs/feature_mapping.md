# Feature Mapping Documentation

## 1. Concept: Single Unified Patient Input to Independent Feature Vectors

The system collects a comprehensive 6-category patient health profile through one user-facing form. The backend mapping services extract only the specific features needed by each independent disease model.

```
                      UNIFIED PATIENT PROFILE
                                 |
         +-----------------------+-----------------------+
         |                                               |
         v                                               v
[Diabetes Feature Mapper]                       [CVD Feature Mapper]
  - age                                           - age
  - gender                                        - gender (1/2 code)
  - bmi                                           - height (cm)
  - blood_glucose_level                           - weight (kg)
  - HbA1c_level                                   - ap_hi (systolic BP)
  - hypertension (0/1)                            - ap_lo (diastolic BP)
  - heart_disease (0/1)                           - cholesterol (1/2/3 category)
  - smoking_history                               - gluc (1/2/3 category)
                                                  - smoke (0/1)
                                                  - alco (0/1)
                                                  - active (0/1)
```

## 2. Complete Feature Mapping Reference Table

| Unified Patient Field | JSON Path | Mapped to Diabetes Model? | Mapped to CVD Model? | Transformation / Derivation Rule |
| :--- | :--- | :--- | :--- | :--- |
| **Age** | `demographics.age` | `age` (Years) | `age` (Years) | Direct numeric pass-through |
| **Gender** | `demographics.gender` | `gender` (`Female`/`Male`/`Other`) | `gender` (`1`=Female, `2`=Male) | Standardized string / numeric encoding |
| **Height** | `physical.height_cm` | *(Derived via BMI)* | `height` (cm) | Direct numeric pass-through for CVD |
| **Weight** | `physical.weight_kg` | *(Derived via BMI)* | `weight` (kg) | Direct numeric pass-through for CVD |
| **BMI** | `physical.bmi` | `bmi` (kg/m²) | *(Implicit in H/W)* | Direct pass-through for Diabetes |
| **Systolic BP** | `vitals.systolic_bp` | *(No direct feature)* | `ap_hi` (mmHg) | Direct numeric pass-through for CVD |
| **Diastolic BP** | `vitals.diastolic_bp` | *(No direct feature)* | `ap_lo` (mmHg) | Direct numeric pass-through for CVD |
| **Heart Rate** | `vitals.heart_rate` | *(Clinical monitoring)* | *(Clinical monitoring)* | Stored in record; omitted from classical model vector |
| **Blood Glucose** | `laboratory.glucose` | `blood_glucose_level` (mg/dL) | `gluc` (1: <100, 2: 100-125, 3: >=126) | Direct value for Diabetes; categorized for CVD |
| **HbA1c** | `laboratory.hba1c` | `HbA1c_level` (%) | *(No direct feature)* | Direct value for Diabetes (median fallback if omitted) |
| **Total Cholesterol** | `laboratory.total_cholesterol` | *(No direct feature)* | `cholesterol` (1: <200, 2: 200-239, 3: >=240) | Categorized for CVD (default=1 if omitted) |
| **HDL / LDL / Triglycerides** | `laboratory.hdl`, `ldl`, `triglycerides`| *(Future Biomarker Submodels)* | *(Future Biomarker Submodels)* | Clinical record persistence |
| **Smoking** | `lifestyle.smoking` | `smoking_history` (`never`, `former`, `current`) | `smoke` (`0`=No, `1`=Yes) | Normalized string for Diabetes; binary for CVD |
| **Physical Activity** | `lifestyle.physical_activity` | *(No direct feature)* | `active` (`0`=No, `1`=Yes) | 1 if Moderate/Active, else 0 |
| **Alcohol** | `lifestyle.alcohol` | *(No direct feature)* | `alco` (`0`=No, `1`=Yes) | 1 if Moderate/Frequent, else 0 |
| **Hypertension History** | `medical_history.hypertension` | `hypertension` (`0`/`1`) | *(Correlated with BP)* | Binary flag for Diabetes |
| **Family History CVD** | `medical_history.family_history_cvd` | `heart_disease` (`0`/`1`) | *(Clinical context)* | Binary flag for Diabetes |
| **Family History Diabetes** | `medical_history.family_history_diabetes`| *(Clinical risk context)* | *(No direct feature)* | Stored in patient record |
