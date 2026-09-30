"""
Automated Test Suite for Security, Privacy & Reliability
AI-Based Explainable Health Risk Prediction System (I-HEART)
Tests privacy safeguards, logging boundaries, secret exclusions in .gitignore,
CORS policies, path shielding in error handlers, and stateless reliability.
"""

import sys
import io
import re
import logging
import json
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from integration.emr_schemas import (
    MockEMRPayload,
    EMRPatientIdentity,
    EMRPhysicalMeasurements,
    EMRClinicalVitals,
    EMRLaboratoryResults,
    EMRLifestyleHistory,
    EMRDiagnosesAndHistory,
)
from integration.emr_service import process_emr_patient

API_BASE_URL = "http://127.0.0.1:8001"


# =============================================================================
# 1. Privacy in Logging (PHI / Clinical Values Safeguards)
# =============================================================================

def test_no_phi_or_clinical_values_logged():
    """Verify that clinical vitals, lab results, and patient measurements are never logged."""
    log_capture = io.StringIO()
    handler = logging.StreamHandler(log_capture)
    logger = logging.getLogger("iheart.integration.emr")
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    test_payload = MockEMRPayload(
        resource_type="MockEMRPatientRecord",
        emr_system_id="HOSP-SEC-AUDIT-99",
        patient_identity=EMRPatientIdentity(mrn="CONFIDENTIAL-MRN-9999", age=54, gender="Female"),
        physical_measurements=EMRPhysicalMeasurements(height_cm=165.0, weight_kg=78.5, bmi=None),
        clinical_vitals=EMRClinicalVitals(systolic_bp=146, diastolic_bp=92, heart_rate=82),
        laboratory_results=EMRLaboratoryResults(fasting_glucose=138.5, total_cholesterol=248.0),
        lifestyle_history=EMRLifestyleHistory(
            smoking_status="Never",
            physical_activity_level="Moderate",
            alcohol_consumption="None"
        ),
        diagnoses_and_history=EMRDiagnosesAndHistory(hypertension_diagnosed=True)
    )

    process_emr_patient(test_payload)
    output = log_capture.getvalue()
    logger.removeHandler(handler)

    # Check operational metadata IS present
    assert "HOSP-SEC-AUDIT-99" in output
    assert "MockEMRPatientRecord" in output

    # Check clinical PHI is NOT present
    assert "CONFIDENTIAL-MRN-9999" not in output
    assert "146" not in output
    assert "92" not in output
    assert "138.5" not in output
    assert "248.0" not in output
    assert "78.5" not in output


# =============================================================================
# 2. Secret & Environment File Protection
# =============================================================================

def test_gitignore_protects_env_and_secrets():
    """Verify .gitignore includes protection against committing secrets, env files, and logs."""
    gitignore_path = PROJECT_ROOT / ".gitignore"
    assert gitignore_path.exists(), ".gitignore file must exist"
    content = gitignore_path.read_text(encoding="utf-8")

    assert ".env" in content
    assert "*.key" in content or "*.pem" in content or "secrets" in content.lower()
    assert "__pycache__" in content
    assert "*.log" in content or "log" in content.lower()


def test_no_hardcoded_secrets_in_codebase():
    """Scan source files for accidental committed secrets or API tokens."""
    sensitive_patterns = [
        re.compile(r"api_key\s*=\s*['\"][A-Za-z0-9_\-]{20,}['\"]", re.IGNORECASE),
        re.compile(r"secret_key\s*=\s*['\"][A-Za-z0-9_\-]{20,}['\"]", re.IGNORECASE),
        re.compile(r"password\s*=\s*['\"][^'\"]{8,}['\"]", re.IGNORECASE),
        re.compile(r"-----BEGIN PRIVATE KEY-----"),
    ]

    target_dirs = [PROJECT_ROOT / "backend", PROJECT_ROOT / "ml", PROJECT_ROOT / "frontend"]
    for d in target_dirs:
        for p in d.rglob("*.py"):
            text = p.read_text(encoding="utf-8", errors="ignore")
            for pat in sensitive_patterns:
                assert not pat.search(text), f"Potential secret pattern found in {p}"


# =============================================================================
# 3. Path Disclosure Shielding in Error Responses
# =============================================================================

def test_error_responses_do_not_leak_server_paths():
    """Verify API error details sanitize local server paths."""
    url = f"{API_BASE_URL}/api/analyze"
    req = urllib.request.Request(
        url,
        data=b'{"patient_id": 123}',
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        urllib.request.urlopen(req)
        assert False, "Should fail with 422"
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8").lower()
        # Verify no system drive paths leaked
        assert "e:\\projects" not in err_body
        assert "c:\\users" not in err_body
        assert "traceback" not in err_body


# =============================================================================
# 4. CORS Configuration for Localhost Deployment
# =============================================================================

def test_cors_headers_configured():
    """Verify CORS headers allow local unified dashboard client requests."""
    url = f"{API_BASE_URL}/api/health"
    req = urllib.request.Request(
        url,
        headers={"Origin": "http://127.0.0.1:8001"},
        method="GET"
    )
    with urllib.request.urlopen(req, timeout=5) as resp:
        cors_header = resp.headers.get("access-control-allow-origin")
        assert cors_header in ["*", "http://127.0.0.1:8001"], f"Unexpected CORS header: {cors_header}"


# =============================================================================
# 5. Statelessness & Repeated Request Reliability
# =============================================================================

def test_repeated_requests_statelessness():
    """Verify successive calls do not contaminate global state or leak prior patient data."""
    url = f"{API_BASE_URL}/api/analyze"

    patient_1 = {
        "patient_id": "STATELESS-PAT-001",
        "demographics": {"age": 25, "gender": "Female"},
        "physical": {"height_cm": 160.0, "weight_kg": 52.0, "bmi": 20.3},
        "vitals": {"systolic_bp": 110, "diastolic_bp": 70, "heart_rate": 68},
        "laboratory": {"glucose": 84.0},
        "lifestyle": {"smoking": "Never", "physical_activity": "Active", "alcohol": "None"},
        "medical_history": {}
    }

    patient_2 = {
        "patient_id": "STATELESS-PAT-002",
        "demographics": {"age": 68, "gender": "Male"},
        "physical": {"height_cm": 170.0, "weight_kg": 95.0, "bmi": 32.9},
        "vitals": {"systolic_bp": 165, "diastolic_bp": 102, "heart_rate": 86},
        "laboratory": {"glucose": 195.0},
        "lifestyle": {"smoking": "Current", "physical_activity": "Sedentary", "alcohol": "Moderate"},
        "medical_history": {"hypertension": True, "family_history_cvd": True}
    }

    # Request 1
    req1 = urllib.request.Request(url, data=json.dumps(patient_1).encode("utf-8"), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req1, timeout=5) as r1:
        res1 = json.loads(r1.read().decode("utf-8"))

    # Request 2
    req2 = urllib.request.Request(url, data=json.dumps(patient_2).encode("utf-8"), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req2, timeout=5) as r2:
        res2 = json.loads(r2.read().decode("utf-8"))

    # Re-request 1
    req1_again = urllib.request.Request(url, data=json.dumps(patient_1).encode("utf-8"), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req1_again, timeout=5) as r1_again:
        res1_again = json.loads(r1_again.read().decode("utf-8"))

    # Assert outputs are isolated and reproducible
    assert res1["patient"]["patient_id"] == "STATELESS-PAT-001"
    assert res2["patient"]["patient_id"] == "STATELESS-PAT-002"
    assert res1_again["patient"]["patient_id"] == "STATELESS-PAT-001"
    assert res1["predictions"]["diabetes"]["risk_percentage"] == res1_again["predictions"]["diabetes"]["risk_percentage"]
    assert res1["predictions"]["cardiovascular"]["risk_percentage"] == res1_again["predictions"]["cardiovascular"]["risk_percentage"]
    assert res1["predictions"]["diabetes"]["risk_percentage"] != res2["predictions"]["diabetes"]["risk_percentage"]


# =============================================================================
# Runner
# =============================================================================

TESTS = [
    test_no_phi_or_clinical_values_logged,
    test_gitignore_protects_env_and_secrets,
    test_no_hardcoded_secrets_in_codebase,
    test_error_responses_do_not_leak_server_paths,
    test_cors_headers_configured,
    test_repeated_requests_statelessness,
]


def run_tests():
    print("=" * 70)
    print("RUNNING SECURITY, PRIVACY & RELIABILITY TEST SUITE")
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
    print(f"SECURITY & PRIVACY RESULTS: {passed} PASSED, {failed} FAILED (TOTAL {len(TESTS)})")
    print("=" * 70)
    return passed, failed, 0


if __name__ == "__main__":
    passed, failed, skipped = run_tests()
    if failed > 0:
        sys.exit(1)
