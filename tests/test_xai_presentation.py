"""
Verification script for Explainable AI (XAI) Presentation Logic
Tests all patient risk cases:
1. Low risk profile (optimal indicators)
2. Moderate risk profile (pre-diabetic, Stage 1 BP, overweight)
3. High risk profile (elevated glucose, Stage 2 BP, obese, smoking)
4. Missing optional fields (null hba1c, null cholesterol)
5. Fallback isolation behavior
6. Results HTML and CSS DOM integrity
"""

import sys
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from schemas import (
    UnifiedPatientProfile,
    Demographics,
    PhysicalMeasurements,
    VitalSigns,
    LaboratoryData,
    LifestyleData,
    MedicalHistory,
)
from services.prediction_service import analyze_unified_patient

def make_profile(age=52, gender="Male", height=175.0, weight=82.0, bmi=26.8,
                 sbp=138, dbp=88, hr=74, glucose=115.0, hba1c=6.1, chol=210.0,
                 smoking="Current", activity="Moderate", alcohol="Moderate",
                 hyp=True, diab_hist=True, cvd_hist=True):
    return UnifiedPatientProfile(
        patient_id="VERIFY-PAT-01",
        demographics=Demographics(age=age, gender=gender),
        physical=PhysicalMeasurements(height_cm=height, weight_kg=weight, bmi=bmi),
        vitals=VitalSigns(systolic_bp=sbp, diastolic_bp=dbp, heart_rate=hr),
        laboratory=LaboratoryData(glucose=glucose, hba1c=hba1c, total_cholesterol=chol),
        lifestyle=LifestyleData(smoking=smoking, physical_activity=activity, alcohol=alcohol),
        medical_history=MedicalHistory(
            hypertension=hyp,
            family_history_diabetes=diab_hist,
            family_history_cvd=cvd_hist
        )
    )

def test_xai_profiles():
    print("==================================================")
    print("TESTING XAI LOGIC ACROSS SCENARIOS")
    print("==================================================")

    # 1. Low Risk Case
    low_p = make_profile(age=28, height=175.0, weight=68.0, bmi=22.2,
                         sbp=114, dbp=72, hr=65, glucose=85.0, hba1c=5.0, chol=170.0,
                         smoking="Never", activity="Active", alcohol="None",
                         hyp=False, diab_hist=False, cvd_hist=False)
    res_low = analyze_unified_patient(low_p)
    d_low_factors = res_low.predictions.diabetes.contributing_factors
    c_low_factors = res_low.predictions.cardiovascular.contributing_factors
    print(f"Low Risk - Diabetes Factors: {d_low_factors}")
    print(f"Low Risk - CVD Factors: {c_low_factors}")
    assert any("Optimal fasting glucose" in f for f in d_low_factors), "Low risk must have optimal glucose"
    assert any("Optimal resting blood pressure" in f for f in c_low_factors), "Low risk must have optimal BP"

    # 2. Moderate Risk Case
    mod_p = make_profile()
    res_mod = analyze_unified_patient(mod_p)
    d_mod_factors = res_mod.predictions.diabetes.contributing_factors
    c_mod_factors = res_mod.predictions.cardiovascular.contributing_factors
    print(f"Moderate Risk - Diabetes Factors: {d_mod_factors}")
    print(f"Moderate Risk - CVD Factors: {c_mod_factors}")
    assert any("Pre-diabetic fasting glucose" in f for f in d_mod_factors), "Mod risk must have pre-diabetic glucose"
    assert any("Stage 1 Hypertension" in f for f in c_mod_factors), "Mod risk must have Stage 1 BP"

    # 3. High Risk Case
    high_p = make_profile(age=64, height=170.0, weight=95.0, bmi=32.9,
                          sbp=162, dbp=102, hr=85, glucose=185.0, hba1c=7.8, chol=265.0,
                          smoking="Current", activity="Sedentary", alcohol="Frequent",
                          hyp=True, diab_hist=True, cvd_hist=True)
    res_high = analyze_unified_patient(high_p)
    d_high_factors = res_high.predictions.diabetes.contributing_factors
    c_high_factors = res_high.predictions.cardiovascular.contributing_factors
    print(f"High Risk - Diabetes Factors: {d_high_factors}")
    print(f"High Risk - CVD Factors: {c_high_factors}")
    assert any("Elevated fasting plasma glucose" in f for f in d_high_factors), "High risk must have elevated glucose"
    assert any("Stage 2 Hypertension" in f for f in c_high_factors), "High risk must have Stage 2 BP"

    # 4. Missing Optional Laboratory Values
    opt_p = make_profile(hba1c=None, chol=None)
    res_opt = analyze_unified_patient(opt_p)
    d_opt_factors = res_opt.predictions.diabetes.contributing_factors
    c_opt_factors = res_opt.predictions.cardiovascular.contributing_factors
    print(f"Missing Optional - Diabetes Factors: {d_opt_factors}")
    print(f"Missing Optional - CVD Factors: {c_opt_factors}")
    assert not any("HbA1c" in f for f in d_opt_factors), "Missing HbA1c must not generate HbA1c factor"
    assert not any("cholesterol" in f.lower() for f in c_opt_factors), "Missing chol must not generate chol factor"

    # 5. Verify results.html structure
    results_html = (PROJECT_ROOT / "frontend" / "results.html").read_text(encoding="utf-8")
    assert 'id="xai-section"' in results_html, "Missing xai-section in results.html"
    assert 'Why this risk was assessed' in results_html, "Missing heading in results.html"
    assert 'id="xai-fallback-alert"' in results_html, "Missing fallback alert in results.html"
    assert 'id="cards-diabetes-primary"' in results_html, "Missing cards-diabetes-primary in results.html"
    assert 'id="cards-cvd-primary"' in results_html, "Missing cards-cvd-primary in results.html"
    assert 'id="xai-synthesis-text"' in results_html, "Missing xai-synthesis-text in results.html"
    assert 'btn-xai-jump' in results_html, "Missing jump links in results.html"

    # 6. Verify results.js logic
    results_js = (PROJECT_ROOT / "frontend" / "js" / "results.js").read_text(encoding="utf-8")
    assert "parseDiseaseFactors" in results_js, "Missing parseDiseaseFactors in results.js"
    assert "generateClinicalSynthesis" in results_js, "Missing generateClinicalSynthesis in results.js"
    assert "triggerXaiFallback" in results_js, "Missing triggerXaiFallback in results.js"
    assert "Detailed factor attribution is currently unavailable" in results_js, "Missing fallback copy in results.js"
    assert "These explanations describe factors considered relevant to this assessment" in results_html, "Missing disclaimer in results.html"

    # 7. Verify CSS
    style_css = (PROJECT_ROOT / "frontend" / "css" / "style.css").read_text(encoding="utf-8")
    assert ".xai-explanation-section" in style_css, "Missing .xai-explanation-section in style.css"
    assert ".xai-factor-card" in style_css, "Missing .xai-factor-card in style.css"
    assert ".status-badge" in style_css, "Missing .status-badge in style.css"
    assert ".contribution-badge" in style_css, "Missing .contribution-badge in style.css"
    assert ".xai-synthesis-card" in style_css, "Missing .xai-synthesis-card in style.css"

    print("==================================================")
    print("ALL XAI VERIFICATION CHECKS PASSED SUCCESSFULLY!")
    print("==================================================")

if __name__ == "__main__":
    test_xai_profiles()
