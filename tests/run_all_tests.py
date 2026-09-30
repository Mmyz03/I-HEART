"""
Master Automated Test Runner & Verification Suite
AI-Based Explainable Health Risk Prediction System (I-HEART)
Step 4: Testing, Validation & System Hardening

Executes all test groups systematically:
  1. ML Pipelines (Diabetes & Cardiovascular Disease)
  2. Input Validation & Clinical Boundaries
  3. API Endpoints & Server Stability
  4. Explainable AI (XAI) & Attribution Resilience
  5. Hospital / EMR Integration Foundation
  6. End-to-End Scenarios (A through F)
  7. Security, Privacy & Reliability Safeguards
  8. Legacy Scenario Verification Regression
"""

import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "backend"))
sys.path.insert(0, str(PROJECT_ROOT / "tests"))


def run_suite(name, module_name, test_func_names=None):
    print("\n" + "=" * 75)
    print(f"SUITE: {name}")
    print("=" * 75)
    start_time = time.time()

    try:
        mod = __import__(module_name)
    except Exception as exc:
        print(f"CRITICAL: Failed to import {module_name}: {exc}")
        return 0, 1, 0, time.time() - start_time, [f"Import error: {exc}"]

    # If the module has its own run_tests function, call it
    if hasattr(mod, "run_tests"):
        try:
            passed, failed, skipped = mod.run_tests()
            duration = time.time() - start_time
            return passed, failed, skipped, duration, []
        except Exception as exc:
            return 0, 1, 0, time.time() - start_time, [str(exc)]

    # Otherwise discover functions starting with test_
    if test_func_names is None:
        test_func_names = [f for f in dir(mod) if f.startswith("test_") and callable(getattr(mod, f))]

    passed = 0
    failed = 0
    failures = []
    for fn in test_func_names:
        func = getattr(mod, fn)
        try:
            func()
            print(f"PASS: {fn}")
            passed += 1
        except Exception as exc:
            print(f"FAIL: {fn} - {exc}")
            failed += 1
            failures.append(f"{fn}: {exc}")

    duration = time.time() - start_time
    print(f"SUMMARY: {passed} passed, {failed} failed in {duration:.2f}s")
    return passed, failed, 0, duration, failures


def main():
    print("#" * 75)
    print("I-HEART COMPREHENSIVE AUTOMATED TEST EXECUTION")
    print("System Hardening, ML Validation, API, XAI, EMR, Security & E2E Suites")
    print("#" * 75)

    suites = [
        ("1. ML Pipelines (Diabetes & CVD)", "test_ml_pipeline"),
        ("2. Input Validation & Clinical Boundaries", "test_validation"),
        ("3. API Endpoints & Server Stability", "test_api_endpoints"),
        ("4. Explainable AI (XAI) & Attribution Resilience", "test_xai"),
        ("5. Hospital / EMR Integration Foundation", "test_emr_integration"),
        ("6. End-to-End Scenarios (A - F)", "test_scenarios_e2e"),
        ("7. Security, Privacy & Reliability Safeguards", "test_security_privacy"),
        ("8. Scenario Verification (verify_scenarios)", "verify_scenarios"),
    ]

    total_passed = 0
    total_failed = 0
    total_skipped = 0
    total_duration = 0.0
    all_failures = []
    suite_records = []

    for name, module_name in suites:
        if module_name == "verify_scenarios":
            # verify_scenarios has test_api()
            p, f, s, d, fails = run_suite(name, module_name, ["test_api"])
        elif module_name == "test_emr_integration":
            # test_emr_integration has numbered functions
            funcs = [f"test_{i}_{suffix}" for i, suffix in [
                (1, "valid_mock_emr_payload"),
                (2, "emr_to_internal_schema_mapping"),
                (3, "missing_required_fields"),
                (4, "invalid_field_types"),
                (5, "invalid_clinical_values"),
                (6, "existing_manual_prediction_flow_still_works"),
                (7, "diabetes_prediction_still_works"),
                (8, "cvd_prediction_still_works"),
                (9, "xai_output_remains_available"),
                (10, "no_raw_patient_data_logged"),
            ]]
            p, f, s, d, fails = run_suite(name, module_name, funcs)
        else:
            p, f, s, d, fails = run_suite(name, module_name)

        total_passed += p
        total_failed += f
        total_skipped += s
        total_duration += d
        suite_records.append((name, p, f, s, d))
        if fails:
            all_failures.extend(fails)

    print("\n" + "#" * 75)
    print("FINAL TEST EXECUTION SUMMARY TABLE")
    print("#" * 75)
    print(f"{'Test Group / Suite':<50} | {'Pass':<5} | {'Fail':<5} | {'Skip':<5} | {'Duration'}")
    print("-" * 75)
    for name, p, f, s, d in suite_records:
        print(f"{name:<50} | {p:<5} | {f:<5} | {s:<5} | {d:.2f}s")
    print("-" * 75)
    print(f"{'OVERALL TOTALS':<50} | {total_passed:<5} | {total_failed:<5} | {total_skipped:<5} | {total_duration:.2f}s")
    print("#" * 75)

    if total_failed == 0:
        print("\nOVERALL STATUS: ALL TEST SUITES PASSED (PASS)")
        print(f"Total Tests Executed: {total_passed + total_failed + total_skipped}")
        return 0
    else:
        print(f"\nOVERALL STATUS: FAIL ({total_failed} failures)")
        for fail in all_failures:
            print(f"  - {fail}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
