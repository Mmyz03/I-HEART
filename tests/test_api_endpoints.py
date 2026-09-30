"""
Automated Test Suite for API Endpoints & Server Stability
AI-Based Explainable Health Risk Prediction System (I-HEART)
Tests HTTP status codes, schema contracts, error formats, malformed JSON handling,
EMR endpoints, and server stability after invalid requests.
"""

import sys
import json
import urllib.request
import urllib.error
from pathlib import Path

BASE_URL = "http://127.0.0.1:8001"


def make_request(method, path, data=None, headers=None):
    url = f"{BASE_URL}{path}"
    req_headers = {"Content-Type": "application/json"}
    if headers:
        req_headers.update(headers)

    body_bytes = None
    if data is not None:
        if isinstance(data, (dict, list)):
            body_bytes = json.dumps(data).encode("utf-8")
        elif isinstance(data, str):
            body_bytes = data.encode("utf-8")
        elif isinstance(data, bytes):
            body_bytes = data

    req = urllib.request.Request(url, data=body_bytes, headers=req_headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            content = resp.read().decode("utf-8")
            return resp.status, resp.headers, content
    except urllib.error.HTTPError as e:
        content = e.read().decode("utf-8")
        return e.code, e.headers, content
    except Exception as exc:
        raise RuntimeError(f"Connection failure to {url}: {str(exc)}")


def get_sample_valid_analyze_payload():
    return {
        "patient_id": "API-TEST-PAT-01",
        "demographics": {"age": 42, "gender": "Female"},
        "physical": {"height_cm": 168.0, "weight_kg": 64.0, "bmi": 22.7},
        "vitals": {"systolic_bp": 118, "diastolic_bp": 76, "heart_rate": 70},
        "laboratory": {
            "glucose": 92.0,
            "hba1c": 5.2,
            "total_cholesterol": 180.0,
            "hdl": 55.0,
            "ldl": 105.0,
            "triglycerides": 110.0,
        },
        "lifestyle": {
            "smoking": "Never",
            "physical_activity": "Moderate",
            "alcohol": "None",
        },
        "medical_history": {
            "hypertension": False,
            "existing_diabetes": False,
            "family_history_diabetes": False,
            "family_history_cvd": False,
        },
    }


def get_sample_valid_emr_payload():
    return {
        "resource_type": "MockEMRPatientRecord",
        "emr_system_id": "HOSP-API-TEST-01",
        "patient_identity": {"mrn": "EMR-API-001", "age": 48, "gender": "Male"},
        "physical_measurements": {"height_cm": 178.0, "weight_kg": 78.0, "bmi": None},
        "clinical_vitals": {"systolic_bp": 126, "diastolic_bp": 82, "heart_rate": 74},
        "laboratory_results": {"fasting_glucose": 102.0, "total_cholesterol": 195.0},
        "lifestyle_history": {
            "smoking_status": "Former",
            "physical_activity_level": "Moderate",
            "alcohol_consumption": "None",
        },
        "diagnoses_and_history": {
            "hypertension_diagnosed": False,
            "existing_diabetes_diagnosed": False,
            "family_history_diabetes": False,
            "family_history_cvd": False,
        },
    }


# =============================================================================
# API Endpoint Tests
# =============================================================================

def test_root_landing_page():
    code, headers, body = make_request("GET", "/")
    assert code == 200, f"Expected 200 for /, got {code}"
    assert "I-HEART" in body or "Health Risk" in body


def test_assessment_page():
    code, headers, body = make_request("GET", "/assessment.html")
    assert code == 200, f"Expected 200 for /assessment.html, got {code}"
    assert "unified-patient-form" in body or "assessment" in body.lower()


def test_results_page():
    code, headers, body = make_request("GET", "/results.html")
    assert code == 200, f"Expected 200 for /results.html, got {code}"
    assert "results" in body.lower() or "dashboard" in body.lower()


def test_health_endpoint():
    code, headers, body = make_request("GET", "/api/health")
    assert code == 200, f"Expected 200 for /api/health, got {code}"
    data = json.loads(body)
    assert data["status"] == "ok"
    assert "running" in data["message"].lower()


def test_docs_endpoint():
    code, headers, body = make_request("GET", "/docs")
    assert code == 200, f"Expected 200 for /docs, got {code}"
    assert "swagger" in body.lower() or "openapi" in body.lower()


def test_analyze_valid_request():
    payload = get_sample_valid_analyze_payload()
    code, headers, body = make_request("POST", "/api/analyze", data=payload)
    assert code == 200, f"Expected 200 for valid /api/analyze, got {code}"
    resp = json.loads(body)
    assert resp["status"] == "success"
    assert "diabetes" in resp["predictions"]
    assert "cardiovascular" in resp["predictions"]
    assert 0 <= resp["predictions"]["diabetes"]["risk_percentage"] <= 100
    assert 0 <= resp["predictions"]["cardiovascular"]["risk_percentage"] <= 100


def test_analyze_missing_required_field():
    payload = get_sample_valid_analyze_payload()
    del payload["laboratory"]["glucose"]
    code, headers, body = make_request("POST", "/api/analyze", data=payload)
    assert code == 422, f"Expected 422 for missing glucose, got {code}"
    assert "detail" in json.loads(body)


def test_analyze_wrong_data_type():
    payload = get_sample_valid_analyze_payload()
    payload["demographics"]["age"] = "invalid_age_string"
    code, headers, body = make_request("POST", "/api/analyze", data=payload)
    assert code == 422, f"Expected 422 for string age, got {code}"


def test_analyze_malformed_json():
    code, headers, body = make_request("POST", "/api/analyze", data="{malformed json")
    assert code in [400, 422], f"Expected 400 or 422 for malformed JSON, got {code}"


def test_analyze_empty_payload():
    code, headers, body = make_request("POST", "/api/analyze", data={})
    assert code == 422, f"Expected 422 for empty object, got {code}"


def test_analyze_inverted_blood_pressure():
    payload = get_sample_valid_analyze_payload()
    payload["vitals"]["systolic_bp"] = 90
    payload["vitals"]["diastolic_bp"] = 110  # DBP > SBP
    code, headers, body = make_request("POST", "/api/analyze", data=payload)
    assert code == 422, f"Expected 422 for DBP > SBP, got {code}"
    assert "strictly lower than" in body or "detail" in body


def test_emr_test_valid_endpoint():
    payload = get_sample_valid_emr_payload()
    code, headers, body = make_request("POST", "/api/emr/test", data=payload)
    assert code == 200, f"Expected 200 for /api/emr/test, got {code}"
    resp = json.loads(body)
    assert resp["status"] == "success"
    assert resp["prediction_source"] == "emr_integration_adapter"
    assert resp["patient"]["patient_id"] == "EMR-API-001"


def test_emr_analyze_valid_endpoint():
    payload = get_sample_valid_emr_payload()
    code, headers, body = make_request("POST", "/api/emr/analyze", data=payload)
    assert code == 200, f"Expected 200 for /api/emr/analyze, got {code}"
    resp = json.loads(body)
    assert resp["status"] == "success"
    assert resp["prediction_source"] == "emr_integration_adapter"


def test_emr_missing_required_fields():
    payload = get_sample_valid_emr_payload()
    del payload["patient_identity"]["mrn"]
    code, headers, body = make_request("POST", "/api/emr/analyze", data=payload)
    assert code == 422, f"Expected 422 for missing MRN, got {code}"


def test_server_stability_after_burst_of_invalid_requests():
    """Verify server remains fully functional after a series of faulty/malformed requests."""
    faulty_inputs = [
        "",
        "{}",
        "{broken: 123",
        {"patient_id": 123},
        {"random_key": "junk"},
        {"demographics": {"age": -50}},
    ]
    for bad in faulty_inputs:
        make_request("POST", "/api/analyze", data=bad)

    # Server should still be 100% healthy
    h_code, _, h_body = make_request("GET", "/api/health")
    assert h_code == 200
    assert json.loads(h_body)["status"] == "ok"

    # Valid analyze request should still execute normally
    valid_payload = get_sample_valid_analyze_payload()
    a_code, _, a_body = make_request("POST", "/api/analyze", data=valid_payload)
    assert a_code == 200
    assert json.loads(a_body)["status"] == "success"


def test_no_file_system_paths_leaked_in_errors():
    """Verify that error messages do not disclose internal server directory paths."""
    # Send a broken request to analyze
    code, headers, body = make_request("POST", "/api/analyze", data={"bad": "payload"})
    assert code == 422
    body_str = body.lower()
    assert "e:\\projects" not in body_str
    assert "c:\\users" not in body_str


# =============================================================================
# Runner
# =============================================================================

TESTS = [
    test_root_landing_page,
    test_assessment_page,
    test_results_page,
    test_health_endpoint,
    test_docs_endpoint,
    test_analyze_valid_request,
    test_analyze_missing_required_field,
    test_analyze_wrong_data_type,
    test_analyze_malformed_json,
    test_analyze_empty_payload,
    test_analyze_inverted_blood_pressure,
    test_emr_test_valid_endpoint,
    test_emr_analyze_valid_endpoint,
    test_emr_missing_required_fields,
    test_server_stability_after_burst_of_invalid_requests,
    test_no_file_system_paths_leaked_in_errors,
]


def run_tests():
    print("=" * 70)
    print("RUNNING API ENDPOINTS & SERVER STABILITY TEST SUITE")
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
    print(f"API TEST RESULTS: {passed} PASSED, {failed} FAILED (TOTAL {len(TESTS)})")
    print("=" * 70)
    return passed, failed, 0


if __name__ == "__main__":
    passed, failed, skipped = run_tests()
    if failed > 0:
        sys.exit(1)
