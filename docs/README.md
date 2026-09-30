# AI-Based Health Risk Prediction

An AI-powered healthcare system designed to predict the risk of **Diabetes and Cardiovascular Diseases** using patient health data. The project applies Machine Learning and Explainable AI techniques to support **early disease detection and clinical decision-making**.

## Features

* Diabetes risk prediction
* Cardiovascular disease risk prediction
* Machine Learning-based health analysis
* Explainable AI (XAI) for understanding predictions
* Patient health data processing
* Early risk detection
* Risk assessment and decision support
* User-friendly healthcare interface
* Scalable framework for future disease prediction

## Technologies Used

**Frontend:** HTML, CSS, JavaScript
**Backend:** Python, FastAPI
**Machine Learning:** Scikit-learn, Pandas, NumPy
**Deep Learning:** TensorFlow / Keras
**Models:** Random Forest, SVM, Logistic Regression, Deep Learning
**Explainable AI:** SHAP / LIME
**Database:** SQLite
**Development Tools:** Jupyter Notebook, VS Code, Git & GitHub

## Project Objective

The main objective is to develop a **reliable, explainable, and scalable AI-based healthcare system** that can identify disease risks at an early stage and provide useful insights to support healthcare professionals.

## Future Scope

The system can be extended with **real-time health monitoring, larger clinical datasets, additional diseases, and continuous model improvement**.

---

# I-HEART Technical Documentation Directory

This directory contains the complete technical reports, architectural specifications, data dictionaries, and testing audits for the **I-HEART** (Intelligent Health Evaluation And Risk Tracking) platform.

---

## Documentation Index

### 1. System Architecture & Engineering
- [ml_architecture.md](file:///e:/projects/I-HEART/docs/ml_architecture.md): Overview of the dual-disease pipeline architecture, data isolation, and inference aggregation.
- [feature_mapping.md](file:///e:/projects/I-HEART/docs/feature_mapping.md): Comprehensive reference mapping the canonical `UnifiedPatientProfile` to model-specific feature vectors.
- [LOCAL_HOST_MERGE_REVIEW.md](file:///e:/projects/I-HEART/docs/LOCAL_HOST_MERGE_REVIEW.md): Audit report on single-port localhost consolidation (`http://127.0.0.1:8001`).

### 2. Machine Learning & Pipelines
- [training_pipeline.md](file:///e:/projects/I-HEART/docs/training_pipeline.md): Step-by-step reproducible training pipeline, data splitting, and data leakage safeguards.
- [model_evaluation.md](file:///e:/projects/I-HEART/docs/model_evaluation.md): 5-Fold cross-validation benchmark results across 4 candidate algorithms and untouched test set performance.
- [datasets/diabetes_dataset.md](file:///e:/projects/I-HEART/docs/datasets/diabetes_dataset.md): Provenance, demographics, and clinical attributes of the Diabetes benchmark dataset.
- [datasets/cardiovascular_dataset.md](file:///e:/projects/I-HEART/docs/datasets/cardiovascular_dataset.md): Provenance, hemodynamics, and clinical attributes of the Cardiovascular Disease benchmark dataset.

### 3. Integration, UI & Verification Audits
- [CLINICAL_UI_REDESIGN_REVIEW.md](file:///e:/projects/I-HEART/docs/CLINICAL_UI_REDESIGN_REVIEW.md): Clinical UI redesign review and aesthetic transformation audit.
- [XAI_IMPLEMENTATION_REVIEW.md](file:///e:/projects/I-HEART/docs/XAI_IMPLEMENTATION_REVIEW.md): Explainable AI clinical factor attribution architecture, derivation rules, and failure resilience.
- [EMR_INTEGRATION_REVIEW.md](file:///e:/projects/I-HEART/docs/EMR_INTEGRATION_REVIEW.md): Implementation and verification audit for the Hospital / EMR Integration Foundation (`MockEMRPayload`, `EMRAdapter`).
- [TESTING_VALIDATION_REVIEW.md](file:///e:/projects/I-HEART/docs/TESTING_VALIDATION_REVIEW.md): Step 4 software testing audit covering 84 automated tests across 8 suites (100% pass rate).
- [DESKTOP_UI_POLISH_REVIEW.md](file:///e:/projects/I-HEART/docs/DESKTOP_UI_POLISH_REVIEW.md): Step 6 desktop visual refinement, clinical dark theme tokens, and accessibility review.
- [MOBILE_RESPONSIVE_REVIEW.md](file:///e:/projects/I-HEART/docs/MOBILE_RESPONSIVE_REVIEW.md): Step 7 mobile and tablet responsive UI audit across 6 viewport tiers (320px to 1024px).
- [FINAL_VERIFICATION_REVIEW.md](file:///e:/projects/I-HEART/docs/FINAL_VERIFICATION_REVIEW.md): Step 8 comprehensive pre-deployment verification and system hardening audit.
- [DOCUMENTATION_REVIEW.md](file:///e:/projects/I-HEART/docs/DOCUMENTATION_REVIEW.md): Step 5 documentation consistency and verification audit report.
- [AGENTS_SETUP_REVIEW.md](file:///e:/projects/I-HEART/docs/AGENTS_SETUP_REVIEW.md): Initial repository context creation and verification audit.

---

## Documentation Standards
All technical documentation in this repository follows strict factual accuracy rules:
- All metrics are based directly on reproducible evaluation scripts and untouched test sets.
- No fictional hospital connections, regulatory approvals, or medical efficacy claims are permitted.
- Future roadmap items are explicitly demarcated from currently implemented functionality.
