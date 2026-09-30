"""
Automated Test Suite for End-to-End Scenarios (A through F)
AI-Based Explainable Health Risk Prediction System (I-HEART)
Tests complete flow against the active FastAPI service:
  Scenario A — Low-risk profile
  Scenario B — Moderate-risk profile
  Scenario C — High-risk profile
  Scenario D — Invalid patient data (safe 422 rejection)
  Scenario E — Incomplete patient data (optional fields omitted)
  Scenario F — EMR patient (mock hospital integration workflow)
"""

import sys
import json
import urllib.request
import urllib.error
from pathlib import Path

API_ANALYZE_URL = "http://127.0.0.1:8001/api/analyze"
API_EMR_URL = "http://127.0.0.1:8001/api/emr/analyze"


def post_json(url, payload):
    data_bytes = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data_bytes,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode("utf-8")
            return resp.status, json.loads(body)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        try:
            parsed = json.loads(body)
        except Exception:
            parsed = {"raw": body}
        return e.code, parsed


# =============================================================================
# Scenario A: Low-Risk Profile
# =============================================================================

def test_scenario_a_low_risk_profile():
    payload = {
        "patient_id": "SCENARIO-A-LOW",
        "demographics": {"age": 26, "gender": "Female"},
        "physical": {"height_cm": 168.0, "weight_kg": 58.0, "bmi": 20.5},
        "vitals": {"systolic_bp": 110, "diastolic_bp": 72, "heart_rate": 66},
        "laboratory": {
            "glucose": 82.0,
            "hba1c": 4.9,
            "total_cholesterol": 160.0,
            "hdl": 60.0,
            "ldl": 85.0,
            "triglycerides": 80.0
        },
        "lifestyle": {
            "smoking": "Never",
            "physical_activity": "Active",
            "alcohol": "None"
        },
        "medical_history": {
            "hypertension": False,
            "existing_diabetes": False,
            "family_history_diabetes": False,
            "family_history_cvd": False
        }
    }
    status_code, resp = post_json(API_ANALYZE_URL, payload)
    assert status_code == 200, f"Expected 200, got {status_code}"
    assert resp["status"] == "success"
    assert resp["prediction_source"] == "trained_ml_models"

    diab = resp["predictions"]["diabetes"]
    cvd = resp["predictions"]["cardiovascular"]

    assert diab["risk_level"] == "Low"
    assert cvd["risk_level"] == "Low"
    assert diab["risk_percentage"] < 35
    assert cvd["risk_percentage"] < 35
    assert len(diab["contributing_factors"]) > 0
    assert len(cvd["contributing_factors"]) > 0


# =============================================================================
# Scenario B: Moderate-Risk Profile
# =============================================================================

def test_scenario_b_moderate_risk_profile():
    payload = {
        "patient_id": "SCENARIO-B-MOD",
        "demographics": {"age": 52, "gender": "Male"},
        "physical": {"height_cm": 175.0, "weight_kg": 82.0, "bmi": 26.8},
        "vitals": {"systolic_bp": 136, "diastolic_bp": 86, "heart_rate": 76},
        "laboratory": {
            "glucose": 116.0,
            "hba1c": 6.0,
            "total_cholesterol": 210.0,
            "hdl": 45.0,
            "ldl": 135.0,
            "triglycerides": 155.0
        },
        "lifestyle": {
            "smoking": "Former",
            "physical_activity": "Moderate",
            "alcohol": "Moderate"
        },
        "medical_history": {
            "hypertension": True,
            "existing_diabetes": False,
            "family_history_diabetes": True,
            "family_history_cvd": False
        }
    }
    status_code, resp = post_json(API_ANALYZE_URL, payload)
    assert status_code == 200, f"Expected 200, got {status_code}"
    assert resp["status"] == "success"

    diab = resp["predictions"]["diabetes"]
    cvd = resp["predictions"]["cardiovascular"]

    assert diab["risk_level"] in ["Moderate", "High"]
    assert cvd["risk_level"] in ["Moderate", "High"]
    assert 0 <= diab["risk_percentage"] <= 100
    assert 0 <= cvd["risk_percentage"] <= 100
    assert len(diab["contributing_factors"]) > 0
    assert len(cvd["contributing_factors"]) > 0


# =============================================================================
# Scenario C: High-Risk Profile
# =============================================================================

def test_scenario_c_high_risk_profile():
    payload = {
        "patient_id": "SCENARIO-C-HIGH",
        "demographics": {"age": 64, "gender": "Male"},
        "physical": {"height_cm": 172.0, "weight_kg": 96.0, "bmi": 32.5},
        "vitals": {"systolic_bp": 160, "diastolic_bp": 98, "heart_rate": 85},
        "laboratory": {
            "glucose": 188.0,
            "hba1c": 7.8,
            "total_cholesterol": 260.0,
            "hdl": 36.0,
            "ldl": 175.0,
            "triglycerides": 245.0
        },
        "lifestyle": {
            "smoking": "Current",
            "physical_activity": "Sedentary",
            "alcohol": "Moderate"
        },
        "medical_history": {
            "hypertension": True,
            "existing_diabetes": False,
            "family_history_diabetes": True,
            "family_history_cvd": True
        }
    }
    status_code, resp = post_json(API_ANALYZE_URL, payload)
    assert status_code == 200, f"Expected 200, got {status_code}"
    assert resp["status"] == "success"

    diab = resp["predictions"]["diabetes"]
    cvd = resp["predictions"]["cardiovascular"]

    assert diab["risk_level"] == "High"
    assert cvd["risk_level"] == "High"
    assert diab["risk_percentage"] >= 70
    assert cvd["risk_percentage"] >= 70
    assert any("glucose" in f.lower() for f in diab["contributing_factors"])
    assert any("hypertension" in f.lower() for f in cvd["contributing_factors"])


# =============================================================================
# Scenario D: Invalid Patient Data (Rejection & Safe Handling)
# =============================================================================

def test_scenario_d_invalid_patient_data():
    # Impossible BP: Diastolic BP >= Systolic BP
    payload_bad_bp = {
        "patient_id": "SCENARIO-D-BAD-BP",
        "demographics": {"age": 40, "gender": "Male"},
        "physical": {"height_cm": 170.0, "weight_kg": 70.0, "bmi": 24.2},
        "vitals": {"systolic_bp": 90, "diastolic_bp": 120, "heart_rate": 70},
        "laboratory": {"glucose": 95.0},
        "lifestyle": {"smoking": "Never", "physical_activity": "Moderate", "alcohol": "None"},
        "medical_history": {}
    }
    code, err_resp = post_json(API_ANALYZE_URL, payload_bad_bp)
    assert code == 422, f"Expected 422 for inverted BP, got {code}"
    assert "detail" in err_resp

    # Out-of-bounds glucose (> 500 mg/dL)
    payload_bad_glucose = {
        "patient_id": "SCENARIO-D-BAD-GLUCOSE",
        "demographics": {"age": 40, "gender": "Male"},
        "physical": {"height_cm": 170.0, "weight_kg": 70.0, "bmi": 24.2},
        "vitals": {"systolic_bp": 120, "diastolic_bp": 80, "heart_rate": 70},
        "laboratory": {"glucose": 750.0},
        "lifestyle": {"smoking": "Never", "physical_activity": "Moderate", "alcohol": "None"},
        "medical_history": {}
    }
    code, err_resp = post_json(API_ANALYZE_URL, payload_bad_glucose)
    assert code == 422, f"Expected 422 for glucose > 500, got {code}"


# =============================================================================
# Scenario E: Incomplete Patient Data (Optional Lab Values Omitted)
# =============================================================================

def test_scenario_e_incomplete_patient_data():
    # Only required fasting glucose provided; all lipid panel & HbA1c omitted (None)
    payload = {
        "patient_id": "SCENARIO-E-INCOMPLETE",
        "demographics": {"age": 45, "gender": "Female"},
        "physical": {"height_cm": 162.0, "weight_kg": 62.0, "bmi": 23.6},
        "vitals": {"systolic_bp": 122, "diastolic_bp": 78, "heart_rate": 72},
        "laboratory": {
            "glucose": 96.0,
            "hba1c": None,
            "total_cholesterol": None,
            "hdl": None,
            "ldl": None,
            "triglycerides": None
        },
        "lifestyle": {
            "smoking": "Never",
            "physical_activity": "Moderate",
            "alcohol": "None"
        },
        "medical_history": {
            "hypertension": False,
            "existing_diabetes": False,
            "family_history_diabetes": False,
            "family_history_cvd": False
        }
    }
    code, resp = post_json(API_ANALYZE_URL, payload)
    assert code == 200, f"Expected 200 for missing optional labs, got {code}"
    assert resp["status"] == "success"
    assert resp["patient"]["laboratory"]["hba1c"] is None
    assert resp["patient"]["laboratory"]["total_cholesterol"] is None
    assert resp["predictions"]["diabetes"]["risk_percentage"] >= 0
    assert resp["predictions"]["cardiovascular"]["risk_percentage"] >= 0


# =============================================================================
# Scenario F: EMR Patient Record Workflow
# =============================================================================

def test_scenario_f_emr_patient():
    emr_payload = {
        "resource_type": "MockEMRPatientRecord",
        "emr_system_id": "HOSP-SCENARIO-F-01",
        "patient_identity": {
            "mrn": "MRN-SCENARIO-F-999",
            "age": 55,
            "gender": "Male"
        },
        "physical_measurements": {
            "height_cm": 176.0,
            "weight_kg": 80.0,
            "bmi": None  # Triggers automatic clinical BMI computation: 80 / (1.76^2) = 25.8
        },
        "clinical_vitals": {
            "systolic_bp": 134,
            "diastolic_bp": 84,
            "heart_rate": 72
        },
        "laboratory_results": {
            "fasting_glucose": 110.0,
            "hba1c": 5.9,
            "total_cholesterol": 205.0,
            "hdl": 46.0,
            "ldl": 132.0,
            "triglycerides": 140.0
        },
        "lifestyle_history": {
            "smoking_status": "Current Smoker",
            "physical_activity_level": "Sedentary",
            "alcohol_consumption": "Moderate"
        },
        "diagnoses_and_history": {
            "hypertension_diagnosed": True,
            "existing_diabetes_diagnosed": False,
            "family_history_diabetes": True,
            "family_history_cvd": True
        }
    }
    code, resp = post_json(API_EMR_URL, emr_payload)
    assert code == 200, f"Expected 200 for EMR scenario, got {code}"
    assert resp["status"] == "success"
    assert resp["prediction_source"] == "emr_integration_adapter"
    assert resp["patient"]["patient_id"] == "MRN-SCENARIO-F-999"
    # Verify BMI was calculated automatically
    assert resp["patient"]["physical"]["bmi"] == 25.8
    # Verify both predictions returned
    assert resp["predictions"]["diabetes"]["risk_percentage"] >= 0
    assert resp["predictions"]["cardiovascular"]["risk_percentage"] >= 0


# =============================================================================
# Runner
# =============================================================================

TESTS = [
    test_scenario_a_low_risk_profile,
    test_scenario_b_moderate_risk_profile,
    test_scenario_c_high_risk_profile,
    test_scenario_d_invalid_patient_data,
    test_scenario_e_incomplete_patient_data,
    test_scenario_f_emr_patient,
]


def run_tests():
    print("=" * 70)
    print("RUNNING END-TO-END CLINICAL SCENARIOS TEST SUITE (A - F)")
    print("=" * 70)
    passed = 0
    failed = 0
    for t in TESTS:
        try:
            t()
            print(f"PASS: {t.__name__}")
            passed += 1
        except Exception as exc:
            print(f"FAIL: {t.__name__} - {str(exc)}")
            failed += 1

    print("=" * 70)
    print(f"SCENARIOS RESULTS: {passed} PASSED, {failed} FAILED (TOTAL {len(TESTS)})")
    print("=" * 70)
    return passed, failed, 0


if __name__ == "__main__":
    passed, failed, skipped = run_tests()
    if failed > 0:
        sys.exit(1)
