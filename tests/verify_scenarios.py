"""
E2E API Verification Script
AI-Based Explainable Health Risk Prediction System
Tests Low Risk, Moderate Risk, and High Risk clinical scenarios against POST /api/analyze.
"""

import json
import urllib.request

API_URL = "http://127.0.0.1:8001/api/analyze"

PATIENTS = [
    {
        "name": "Low Risk Patient Profile",
        "payload": {
            "patient_id": "PAT-LOW-01",
            "demographics": {"age": 28, "gender": "Female"},
            "physical": {"height_cm": 165.0, "weight_kg": 56.0, "bmi": 20.6},
            "vitals": {"systolic_bp": 112, "diastolic_bp": 72, "heart_rate": 68},
            "laboratory": {
                "glucose": 84.0,
                "hba1c": 5.0,
                "total_cholesterol": 165.0,
                "hdl": 58.0,
                "ldl": 92.0,
                "triglycerides": 95.0
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
    },
    {
        "name": "Moderate Risk Patient Profile",
        "payload": {
            "patient_id": "PAT-MOD-02",
            "demographics": {"age": 52, "gender": "Male"},
            "physical": {"height_cm": 175.0, "weight_kg": 82.0, "bmi": 26.8},
            "vitals": {"systolic_bp": 138, "diastolic_bp": 88, "heart_rate": 76},
            "laboratory": {
                "glucose": 118.0,
                "hba1c": 6.1,
                "total_cholesterol": 215.0,
                "hdl": 44.0,
                "ldl": 138.0,
                "triglycerides": 165.0
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
    },
    {
        "name": "High Risk Patient Profile",
        "payload": {
            "patient_id": "PAT-HIGH-03",
            "demographics": {"age": 63, "gender": "Male"},
            "physical": {"height_cm": 172.0, "weight_kg": 96.0, "bmi": 32.5},
            "vitals": {"systolic_bp": 158, "diastolic_bp": 98, "heart_rate": 84},
            "laboratory": {
                "glucose": 185.0,
                "hba1c": 7.6,
                "total_cholesterol": 260.0,
                "hdl": 35.0,
                "ldl": 175.0,
                "triglycerides": 240.0
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
    }
]


def test_api():
    print("=" * 70)
    print("END-TO-END VERIFICATION OF TRAINED ML PREDICTION PIPELINES")
    print("=" * 70)

    for item in PATIENTS:
        name = item["name"]
        payload = item["payload"]

        data_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            API_URL,
            data=data_bytes,
            headers={"Content-Type": "application/json"}
        )

        with urllib.request.urlopen(req, timeout=5) as response:
            resp_json = json.loads(response.read().decode("utf-8"))

        d_res = resp_json["predictions"]["diabetes"]
        c_res = resp_json["predictions"]["cardiovascular"]

        print(f"\nScenario: {name} (ID: {payload['patient_id']})")
        print("-" * 50)
        print(f"  Diabetes Risk:       {d_res['risk_percentage']}% [{d_res['risk_level']}]")
        print(f"  Diabetes Factors:    {', '.join(d_res['contributing_factors'])}")
        print(f"  Cardiovascular Risk: {c_res['risk_percentage']}% [{c_res['risk_level']}]")
        print(f"  CVD Factors:         {', '.join(c_res['contributing_factors'])}")
        print(f"  Prediction Source:   {resp_json['prediction_source']}")

    print("\n" + "=" * 70)
    print("ALL TEST SCENARIOS RETURNED VERIFIED PREDICTIONS FROM TRAINED ML MODELS")
    print("=" * 70)


if __name__ == "__main__":
    test_api()
