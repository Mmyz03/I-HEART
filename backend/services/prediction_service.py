"""
AI-Based Explainable Health Risk Prediction System
Unified Prediction Service Orchestrator
Executes independent Diabetes and CVD trained ML pipelines on the unified patient record.
"""

from typing import Tuple, List

try:
    from schemas import (
        UnifiedPatientProfile,
        DiseaseRiskResult,
        PredictionsContainer,
        AnalysisResponse,
    )
    from services.diabetes_predictor import predict_diabetes
    from services.cvd_predictor import predict_cvd
except ImportError:
    from ..schemas import (
        UnifiedPatientProfile,
        DiseaseRiskResult,
        PredictionsContainer,
        AnalysisResponse,
    )
    from .diabetes_predictor import predict_diabetes
    from .cvd_predictor import predict_cvd


def analyze_unified_patient(patient: UnifiedPatientProfile) -> AnalysisResponse:
    """
    Main prediction service orchestrator.
    Routes one unified patient profile concurrently through the independent trained ML pipelines:
      1. Diabetes ML Pipeline (Feature mapping -> Preprocessor -> Trained Classifier)
      2. Cardiovascular Disease ML Pipeline (Feature mapping -> Preprocessor -> Trained Classifier)
    """
    diabetes_result = predict_diabetes(patient)
    cvd_result = predict_cvd(patient)

    return AnalysisResponse(
        status="success",
        prediction_source="trained_ml_models",
        disclaimer="Academic research prototype demonstration only. Not a medical diagnostic tool.",
        patient=patient,
        predictions=PredictionsContainer(
            diabetes=diabetes_result,
            cardiovascular=cvd_result
        )
    )
