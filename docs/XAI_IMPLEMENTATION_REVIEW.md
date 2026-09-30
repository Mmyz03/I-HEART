# EXPLAINABLE AI (XAI) & FACTOR ATTRIBUTION REVIEW

> **Authoritative Context**: Root `AGENTS.md`  
> **Status**: Completed  
> **Milestone**: Explainable AI & Clinical Attribution Architecture

---

## 1. Overview & Objective

In clinical risk screening, providing black-box probabilities without interpretability impairs clinical trust and decision support. The I-HEART system pairs every numeric risk prediction with **Explainable AI (XAI) Clinical Factor Attribution**.

The objectives of the XAI layer are:
1. Identify and explain the specific biomarkers, vitals, or demographic factors driving elevated or optimal risk.
2. Present evidence-based findings in clear, human-understandable clinical terminology (avoiding raw feature tokens or internal mathematical variables).
3. Ensure **failure-isolated resilience**: if an attribution or text-generation routine encounters an unhandled exception, it must gracefully return a clinical fallback note without interrupting or failing the core machine-learning prediction pipeline.

---

## 2. Architecture & Pipeline Isolation

XAI attribution routines operate inside the specialized predictor modules:
- Diabetes Pipeline: `explain_diabetes_factors()` in [backend/services/diabetes_predictor.py](file:///e:/projects/I-HEART/backend/services/diabetes_predictor.py)
- Cardiovascular Pipeline: `explain_cvd_factors()` in [backend/services/cvd_predictor.py](file:///e:/projects/I-HEART/backend/services/cvd_predictor.py)

```
                            Patient Health Record
                                      │
              ┌───────────────────────┴───────────────────────┐
              ▼                                               ▼
    [predict_diabetes]                                  [predict_cvd]
              │                                               │
   [predict_proba → Risk %]                       [predict_proba → Risk %]
              │                                               │
              ▼                                               ▼
  [explain_diabetes_factors]                        [explain_cvd_factors]
    - Glucose thresholds                             - Blood pressure stages
    - HbA1c prediabetic/diabetic                     - Cholesterol categories
    - BMI classifications                            - Tobacco & lifestyle
    - Age & medical history                          - Age & clinical history
              │                                               │
              └───────────────────────┬───────────────────────┘
                                      ▼
                       Aggregated AnalysisResponse
                   [Risk %, Level Badge, Factors List,
                         Clinical Summary Note]
```

---

## 3. Clinical Factor Derivation Rules

### 3.1 Diabetes XAI Factor Rules
| Clinical Parameter | Threshold / Clinical Condition | Generated Factor Phrasing |
| :--- | :--- | :--- |
| **Fasting Blood Glucose** | $\ge 126.0\text{ mg/dL}$ | Elevated fasting plasma glucose ($X\text{ mg/dL}$) in diabetic range |
| | $100.0 \le \text{Glucose} < 126.0$ | Pre-diabetic fasting glucose range ($X\text{ mg/dL}$) |
| | $\text{Glucose} < 100.0\text{ mg/dL}$ | Optimal fasting glucose ($X\text{ mg/dL}$) |
| **HbA1c** | $\ge 6.5\%$ | Elevated HbA1c ($X\%$) in diabetic range |
| | $5.7\% \le \text{HbA1c} < 6.5\%$ | Borderline HbA1c ($X\%$) in pre-diabetic range |
| | $\text{HbA1c} < 5.7\%$ | Normal glycated hemoglobin ($X\%$) |
| **Body Mass Index (BMI)** | $\ge 30.0\text{ kg/m}^2$ | High Body Mass Index (BMI: $X\text{ kg/m}^2$ - Obese) |
| | $25.0 \le \text{BMI} < 30.0$ | Elevated Body Mass Index (BMI: $X\text{ kg/m}^2$ - Overweight) |
| **Demographics & History** | $\text{Age} \ge 45$ | Age demographic risk factor ($X\text{ years}$) |
| | Hypertension diagnosed | Prior clinical diagnosis of hypertension |
| | Family history diabetes | First-degree family history of Type 2 diabetes |

### 3.2 Cardiovascular Disease (CVD) XAI Factor Rules
| Clinical Parameter | Threshold / Clinical Condition | Generated Factor Phrasing |
| :--- | :--- | :--- |
| **Blood Pressure** | $\text{SBP} \ge 140\text{ or }\text{DBP} \ge 90$ | Stage 2 Hypertension ($SBP/DBP\text{ mmHg}$) |
| | $130 \le \text{SBP} < 140\text{ or }80 \le \text{DBP} < 90$ | Stage 1 Hypertension ($SBP/DBP\text{ mmHg}$) |
| | $120 \le \text{SBP} < 130\text{ and }\text{DBP} < 80$ | Elevated blood pressure ($SBP/DBP\text{ mmHg}$) |
| | $\text{SBP} < 120\text{ and }\text{DBP} < 80$ | Optimal resting blood pressure ($SBP/DBP\text{ mmHg}$) |
| **Cholesterol** | $\text{Total} \ge 240\text{ mg/dL}$ | High total cholesterol ($X\text{ mg/dL}$) |
| | $200 \le \text{Total} < 240\text{ mg/dL}$ | Borderline total cholesterol ($X\text{ mg/dL}$) |
| **Smoking Behavior** | Current smoker | Active tobacco smoking behavior |
| | Former smoker | History of prior tobacco smoking |
| **Demographics & History** | $\text{Age} \ge 50$ | Age demographic risk ($X\text{ years}$) |
| | Hypertension diagnosed | Documented clinical history of hypertension |
| | Family history CVD | Documented hereditary/family history of cardiovascular disease |

---

## 4. Failure Resilience & Isolation Safeguards

To prevent external or internal explanation failures from degrading clinical prediction availability:
1. **Try-Except Enclosure**: Both `explain_diabetes_factors()` and `explain_cvd_factors()` are wrapped in comprehensive `try-except` blocks.
2. **Predictor-Level Fallback**: If factor extraction raises any exception, the predictor logs an error and returns a sanitized fallback note: `"Clinical risk estimation computed successfully. Detailed factor attribution temporarily unavailable."`
3. **Orchestrator-Level Fallback**: If an entire disease module fails during attribution, the master orchestrator (`analyze_unified_patient`) preserves the companion disease prediction and returns valid response payloads.

---

## 5. Automated Verification Results

Suite 4 of the automated test runner rigorously exercises the XAI layer:

| Test Case | Description | Result |
| :--- | :--- | :--- |
| `test_diabetes_xai_optimal_indicators` | Confirms normal ranges generate optimal clinical indicator descriptions | **PASS** |
| `test_diabetes_xai_elevated_indicators` | Confirms diabetic thresholds produce diabetic range explanations | **PASS** |
| `test_diabetes_xai_prediabetic_indicators` | Verifies pre-diabetic glucose/HbA1c classifications | **PASS** |
| `test_cvd_xai_optimal_indicators` | Confirms optimal resting blood pressure factor phrasing | **PASS** |
| `test_cvd_xai_stage1_hypertension_and_smoking` | Confirms Stage 1 hypertension and smoking factor capture | **PASS** |
| `test_cvd_xai_stage2_hypertension_and_high_cholesterol` | Confirms Stage 2 hypertension and hypercholesterolemia attribution | **PASS** |
| `test_xai_feature_names_are_human_understandable` | Ensures zero internal column names (e.g. `ap_hi`, `hdl_mg_dl`) leak into user messages | **PASS** |
| `test_xai_summary_note_integrity` | Verifies clinical summary notes provide contextual narrative guidance | **PASS** |
| `test_xai_dynamically_reflects_patient_changes` | Verifies changes in patient vitals dynamically alter generated attributions | **PASS** |
| `test_diabetes_prediction_resilience_on_xai_failure` | Proves Diabetes prediction succeeds even if XAI throws `RuntimeError` | **PASS** |
| `test_cvd_prediction_resilience_on_xai_failure` | Proves CVD prediction succeeds even if XAI throws `RuntimeError` | **PASS** |
| `test_orchestrator_resilience_on_dual_xai_failure` | Proves Dual prediction orchestrator succeeds even under total XAI crash | **PASS** |

*Result: 12 of 12 XAI tests passing.*
