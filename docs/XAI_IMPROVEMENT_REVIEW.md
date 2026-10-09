# Explainable AI (XAI) Presentation & Human-Understandable Explanations Review

**System:** I-HEART (Intelligent Health Evaluation And Risk Tracking)  
**Document:** `docs/XAI_IMPROVEMENT_REVIEW.md`  
**Date:** October 2026  
**Status:** Complete & Verified  

---

## 1. Overview & Objectives

The goal of this enhancement was to transform the Explainable AI (XAI) section of the I-HEART clinical risk screening platform from high-level, generic attribution callouts into human-understandable, detailed, clinically grounded explanations for both **Type 2 Diabetes** and **Cardiovascular Disease (CVD)**.

### Problems Addressed:
1. **Factor Ambiguity:** Previous outputs displayed terse summary phrases without clear identification of the patient's individual biomarker and why it was flagged.
2. **Missing Reference Ranges:** Users could not see standard normative baselines or thresholds against which their values were evaluated.
3. **Absence of Clinical Directionality:** The clinical contribution direction (e.g., higher-risk contribution vs. lower-risk contribution) and categorical status (Normal vs. Elevated vs. Relevant) were not explicitly distinguished.
4. **No Synthesized Clinical Takeaway:** There was no cohesive summary contextualizing how the combination of factors influenced the dual assessment.
5. **Technical Jargon:** Machine learning terminology (feature vectors, coefficients, importance) was eliminated in favor of patient-centered clinical language.

---

## 2. Summary of Changes

### 2.1 Files Modified
1. [frontend/results.html](file:///e:/projects/I-HEART/frontend/results.html):
   - Replaced generic static `.xai-callout-card` with the comprehensive `<section class="xai-explanation-section" id="xai-section">`.
   - Added section heading `"Why this risk was assessed"` with plain-language introduction without causal claims.
   - Added disease-specific panels for **Type 2 Diabetes Factors** and **Cardiovascular Disease Factors**.
   - Added priority grouping containers: `"Most Relevant Factors"` and `"Other Relevant Factors"`.
   - Added dynamic `"What this means"` clinical synthesis card (`#xai-synthesis-container`).
   - Added subtle medical AI disclaimer notice at the base of the XAI section.
   - Added jump links (`.btn-xai-jump`) in the top disease risk cards for fast navigation to detailed explanations.
   - Integrated graceful fallback alert box (`#xai-fallback-alert`).

2. [frontend/js/results.js](file:///e:/projects/I-HEART/frontend/js/results.js):
   - Implemented `renderExplainableAI(analysis)` with robust factor parsing, disease-specific categorization, and priority sorting.
   - Implemented `parseSingleDiabetesFactor()` and `parseSingleCvdFactor()` mapping each identified biomarker to actual patient values, units, reference ranges, status badges, contribution direction, and plain-language "Why this matters" narratives.
   - Implemented `generateClinicalSynthesis()` dynamically compiling key findings across both disease profiles into a cohesive summary.
   - Implemented `triggerXaiFallback()` displaying `"Detailed factor attribution is currently unavailable, but your risk prediction was completed successfully."` if attribution data is interrupted.
   - Maintained strict XSS protection using HTML escaping on all injected values.

3. [frontend/css/style.css](file:///e:/projects/I-HEART/frontend/css/style.css):
   - Added clinical design tokens and component styling for `.xai-explanation-section`, `.xai-disease-panel`, `.xai-factor-card`, `.status-badge`, `.contribution-badge`, `.xai-synthesis-card`, and `.btn-xai-jump`.
   - Maintained dark clinical theme adhering to I-HEART visual standards (glassmorphism cards, emerald/teal accents, JetBrains Mono numbers, and Inter typography).
   - Added responsive rules across breakpoints (1024px, 768px, 580px, 480px, 360px).

---

## 3. Human-Understandable Factor Card Structure

Each identified clinical factor is rendered as an individual card with the following structure:

```
┌────────────────────────────────────────────────────────────────────────┐
│ 1. Fasting Blood Glucose                     [STATUS: ELEVATED]        │
│ 168 mg/dL                         [HIGHER-RISK CONTRIBUTION]           │
├────────────────────────────────────────────────────────────────────────┤
│ Reference Range: 70–99 mg/dL                                           │
├────────────────────────────────────────────────────────────────────────┤
│ WHY THIS MATTERS:                                                      │
│ Your fasting blood glucose is 168 mg/dL, which is above the reference   │
│ range used by this assessment (70–99 mg/dL). Elevated glucose levels    │
│ are associated with increased diabetes risk, making this an important   │
│ factor in your current assessment.                                     │
└────────────────────────────────────────────────────────────────────────┘
```

### Factor Card Fields:
- **Factor Name:** Clearly labeled clinical parameter (e.g., Fasting Blood Glucose, Glycated Hemoglobin (HbA1c), Body Mass Index, Resting Blood Pressure, Tobacco Smoking, Total Cholesterol, Age Demographic).
- **Patient's Actual Value:** Large typography displaying the patient's measured number (e.g., `168`, `6.1`, `26.8`, `138/88`, `210`).
- **Clinical Unit:** Subdued unit indicator (`mg/dL`, `%`, `kg/m²`, `mmHg`, `years`).
- **Reference Range:** Standard clinical normative threshold (e.g., `70–99 mg/dL`, `< 5.7%`, `18.5–24.9 kg/m²`, `< 120/80 mmHg`, `< 200 mg/dL`).
- **Status Badge:** Categorical rating (`Normal`, `Elevated`, or `Relevant`).
- **Contribution Direction:** Qualitative assessment contribution (`Higher-risk contribution`, `Lower-risk contribution`, or `Relevant factor`).
- **Why It Matters Narrative:** Clear, non-technical explanation describing how the biomarker relates to evaluated risk without making unsupported causal claims.

---

## 4. Prioritization & Dynamic Clinical Synthesis

### Factor Prioritization:
Factors identified by the backend attribution logic are categorized into two tiers:
1. **Most Relevant Factors (Primary):** Direct physiological biomarkers and active lifestyle behaviors (Blood Glucose, HbA1c, BMI, Blood Pressure, Smoking, Total Cholesterol).
2. **Other Relevant Factors (Secondary):** Demographic and clinical history context (Age Demographic, Diagnosed Hypertension history, Family History).

### Dynamic "What This Means" Synthesis:
Below the factor panels, a synthesized narrative is dynamically generated reflecting the exact combination of findings:
> *"The assessment identified elevated fasting blood glucose, glycated hemoglobin (hba1c), and body mass index (bmi) as important factors associated with your current diabetes risk. For cardiovascular health, resting blood pressure, tobacco smoking status, and total serum cholesterol were identified as relevant factors influencing your assessed risk. Demographic and clinical history factors (age demographic) were also taken into account. These explanations provide transparency into the specific parameters considered during your assessment, helping facilitate productive conversations with your physician."*

### Subtle Medical Disclaimer:
> *"These explanations describe factors considered relevant to this assessment. They are not a medical diagnosis and should not be used as a substitute for professional medical advice."*

---

## 5. Fallback & Failure Isolation

If backend factor attribution is temporarily unavailable or encounters an isolated error:
- The results page remains fully functional; risk gauge percentages and categorical bands are never disrupted.
- The XAI section displays a non-blocking clinical notice:
  > **Attribution Notice:** Detailed factor attribution is currently unavailable, but your risk prediction was completed successfully.
- No placeholder or fabricated data is ever rendered.

---

## 6. Confirmation of System Integrity

- **ML Models & Artifacts:** Untouched ([diabetes_model.joblib](file:///e:/projects/I-HEART/models/diabetes/diabetes_model.joblib), [cvd_model.joblib](file:///e:/projects/I-HEART/models/cardiovascular/cvd_model.joblib)).
- **Preprocessing Pipelines:** Untouched ([diabetes_preprocessor.joblib](file:///e:/projects/I-HEART/models/diabetes/diabetes_preprocessor.joblib), [cvd_preprocessor.joblib](file:///e:/projects/I-HEART/models/cardiovascular/cvd_preprocessor.joblib)).
- **Prediction Logic & Risk Thresholds:** Completely unchanged (`<35% Low`, `35–69% Moderate`, `>=70% High`).
- **API Contracts:** `POST /api/analyze` and `POST /api/emr/analyze` contracts and schemas remain identical.
- **Hospital / EMR Integration:** Untouched.

---

## 7. Verification & Test Results

### 7.1 Full Test Suite Execution (`py tests/run_all_tests.py`)
```
###########################################################################
FINAL TEST EXECUTION SUMMARY TABLE
###########################################################################
Test Group / Suite                                 | Pass  | Fail  | Skip  | Duration
---------------------------------------------------------------------------
1. ML Pipelines (Diabetes & CVD)                   | 11    | 0     | 0     | 1.84s
2. Input Validation & Clinical Boundaries          | 22    | 0     | 0     | 0.01s
3. API Endpoints & Server Stability                | 16    | 0     | 0     | 0.16s
4. Explainable AI (XAI) & Attribution Resilience   | 12    | 0     | 0     | 0.05s
5. Hospital / EMR Integration Foundation           | 10    | 0     | 0     | 0.04s
6. End-to-End Scenarios (A - F)                    | 6     | 0     | 0     | 0.07s
7. Security, Privacy & Reliability Safeguards      | 6     | 0     | 0     | 0.10s
8. Scenario Verification (verify_scenarios)        | 1     | 0     | 0     | 0.06s
---------------------------------------------------------------------------
OVERALL TOTALS                                     | 84    | 0     | 0     | 2.33s
###########################################################################

OVERALL STATUS: ALL TEST SUITES PASSED (PASS)
Total Tests Executed: 84
```

### 7.2 Scenario-Specific XAI Verification (`tests/test_xai_presentation.py`)
- **Low Risk Profile (PAT-LOW-01):** Optimal fasting glucose (85 mg/dL) and optimal resting BP (114/72 mmHg) correctly identified with `Normal` status and `Lower-risk contribution`.
- **Moderate Risk Profile (PAT-MOD-02):** Pre-diabetic glucose, borderline HbA1c, overweight BMI, and Stage 1 BP correctly parsed with `Elevated` status and `Higher-risk contribution`.
- **High Risk Profile (PAT-HIGH-03):** Diabetic glucose (185 mg/dL), diabetic HbA1c (7.8%), obese BMI (32.9 kg/m²), Stage 2 BP (162/102 mmHg), and high cholesterol correctly prioritized.
- **Missing Optional Values:** Null HbA1c and cholesterol profiles handled cleanly without generating phantom cards or failing.
- **Fallback Simulation:** Handled without UI interruption; fallback message presented cleanly.

### 7.3 Responsive Layout Verification
Responsive rules and layout behavior verified across all required resolutions:
- **320x568 & 360x640 (Compact mobile):** Factor cards stack vertically, values scaled to 1.15rem, badges wrap neatly without overflow.
- **375x667, 390x844, 414x896 (Standard mobile):** 1-column layout, full touch targets, readable explanation blocks.
- **768x1024 (Tablets):** 1-column disease panel grid with spacious card layouts and clear typography.
- **1366x768, 1440x900, 1920x1080 (Laptops & Desktops):** Balanced 2-column grid comparing metabolic vs. cardiovascular factors side by side.
