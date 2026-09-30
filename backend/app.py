"""
AI-Based Explainable Health Risk Prediction System for Diabetes and Cardiovascular Disease
FastAPI Backend Application Entry Point
"""

import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Ensure the backend folder is on the Python sys.path
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Path to frontend directory
frontend_dir = backend_dir.parent / "frontend"

# Import schemas and prediction service
try:
    from schemas import UnifiedPatientProfile, AnalysisResponse
    from services.prediction_service import analyze_unified_patient
    from integration.emr_schemas import MockEMRPayload
    from integration.emr_service import process_emr_patient
except ImportError:
    from .schemas import UnifiedPatientProfile, AnalysisResponse
    from .services.prediction_service import analyze_unified_patient
    from .integration.emr_schemas import MockEMRPayload
    from .integration.emr_service import process_emr_patient

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
        err_msg = str(exc)
        if any(token in err_msg.lower() for token in [":\\", "c:", "e:", "users\\", ".py"]):
            err_msg = "An internal processing error occurred during health risk analysis."
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during health risk analysis: {err_msg}"
        )


@app.post(
    "/api/emr/analyze",
    response_model=AnalysisResponse,
    status_code=status.HTTP_200_OK,
    tags=["EMR Integration"]
)
def analyze_emr_patient(emr_payload: MockEMRPayload):
    """
    Hospital / EMR Integration Endpoint.
    Accepts external EMR-formatted patient record, normalizes via EMRAdapter into
    the UnifiedPatientProfile contract, and routes to dual ML prediction pipelines.
    """
    try:
        response = process_emr_patient(emr_payload)
        return response
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"EMR Data Normalization Error: {str(ve)}"
        )
    except Exception as exc:
        err_msg = str(exc)
        if any(token in err_msg.lower() for token in [":\\", "c:", "e:", "users\\", ".py"]):
            err_msg = "An internal processing error occurred during EMR analysis."
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during EMR analysis: {err_msg}"
        )


@app.post(
    "/api/emr/test",
    response_model=AnalysisResponse,
    status_code=status.HTTP_200_OK,
    tags=["EMR Integration"]
)
def test_emr_integration_endpoint(emr_payload: MockEMRPayload):
    """
    Dedicated test endpoint for validating Hospital / EMR integration payloads.
    Alias of /api/emr/analyze.
    """
    return analyze_emr_patient(emr_payload)


# -----------------------------------------------------------------------------
# Frontend Page & Static File Serving (Unified Localhost)
# -----------------------------------------------------------------------------

@app.get("/", response_class=FileResponse, include_in_schema=False)
def serve_root():
    """Serves the frontend landing page at http://localhost:8001/."""
    index_file = frontend_dir / "index.html"
    if not index_file.exists():
        raise HTTPException(status_code=404, detail="Frontend index.html not found.")
    return FileResponse(index_file)


@app.get("/index.html", response_class=FileResponse, include_in_schema=False)
def serve_index_page():
    """Serves the frontend landing page directly."""
    return FileResponse(frontend_dir / "index.html")


@app.get("/assessment.html", response_class=FileResponse, include_in_schema=False)
def serve_assessment_page():
    """Serves the unified assessment form at http://localhost:8001/assessment.html."""
    assessment_file = frontend_dir / "assessment.html"
    if not assessment_file.exists():
        raise HTTPException(status_code=404, detail="Frontend assessment.html not found.")
    return FileResponse(assessment_file)


@app.get("/results.html", response_class=FileResponse, include_in_schema=False)
def serve_results_page():
    """Serves the results dashboard at http://localhost:8001/results.html."""
    results_file = frontend_dir / "results.html"
    if not results_file.exists():
        raise HTTPException(status_code=404, detail="Frontend results.html not found.")
    return FileResponse(results_file)


# Mount static assets (CSS, JS, images) - must be placed after all API & page routes
if frontend_dir.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    # Defaults to port 8001 as specified in the environment instructions
    uvicorn.run("app:app", host="127.0.0.1", port=8001, reload=False)

