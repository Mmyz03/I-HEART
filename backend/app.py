"""
AI-Based Explainable Health Risk Prediction System for Diabetes and Cardiovascular Disease
FastAPI Backend Application Entry Point
"""

import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

# Ensure the backend folder is on the Python sys.path
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Import schemas and prediction service
try:
    from schemas import UnifiedPatientProfile, AnalysisResponse
    from services.prediction_service import analyze_unified_patient
except ImportError:
    from .schemas import UnifiedPatientProfile, AnalysisResponse
    from .services.prediction_service import analyze_unified_patient

# Initialize FastAPI app
app = FastAPI(
    title="AI Health Risk Prediction API",
    description="Unified Patient Health Risk Analysis API for Diabetes & Cardiovascular Disease (Review 1 Prototype)",
    version="1.0.0"
)

# Configure Cross-Origin Resource Sharing (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", tags=["Health"])
def health_check():
    """
    Health check endpoint to verify backend operational status.
    """
    return {
        "status": "ok",
        "message": "AI Health Risk Prediction API is running"
    }


@app.post(
    "/api/analyze",
    response_model=AnalysisResponse,
    status_code=status.HTTP_200_OK,
    tags=["Analysis"]
)
def analyze_patient_health(patient: UnifiedPatientProfile):
    """
    Unified Patient Health Analysis Endpoint.
    Accepts one unified patient health profile and returns dual risk assessments
    (Diabetes & Cardiovascular Disease) using the prototype prediction pipeline.
    """
    try:
        response = analyze_unified_patient(patient)
        return response
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during health risk analysis: {str(exc)}"
        )


if __name__ == "__main__":
    import uvicorn
    # Defaults to port 8001 as specified in the environment instructions
    uvicorn.run("app:app", host="127.0.0.1", port=8001, reload=False)
