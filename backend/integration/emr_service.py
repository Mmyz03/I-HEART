"""
Hospital / EMR Integration Service
Orchestrates EMR record ingestion, schema adaptation, and dual-disease risk analysis
via existing I-HEART ML pipelines without duplicating prediction logic.
"""

import logging
from typing import Union, Dict, Any
from .emr_schemas import MockEMRPayload
from .emr_adapter import EMRAdapter

try:
    from schemas import AnalysisResponse
    from services.prediction_service import analyze_unified_patient
except ImportError:
    from ..schemas import AnalysisResponse
    from ..services.prediction_service import analyze_unified_patient

logger = logging.getLogger("iheart.integration.emr")


def process_emr_patient(emr_payload: Union[MockEMRPayload, Dict[str, Any]]) -> AnalysisResponse:
    """
    Ingests an EMR-formatted patient record, converts it into the internal
    UnifiedPatientProfile contract, and executes the trained ML pipelines.

    Privacy & Security:
      - Raw clinical vitals and identifiers are NOT emitted to system logs.
      - Only operational metrics (system ID and event status) are tracked.
    """
    if isinstance(emr_payload, dict):
        emr_payload = MockEMRPayload(**emr_payload)

    # Privacy-conscious operational audit log (No clinical PII logged)
    logger.info(
        "Ingesting EMR record from source system: %s (resource: %s)",
        emr_payload.emr_system_id,
        emr_payload.resource_type
    )

    # 1. Normalize and adapt to canonical UnifiedPatientProfile
    unified_profile = EMRAdapter.emr_to_unified(emr_payload)

    # 2. Execute existing prediction pipelines through the orchestrator
    response = analyze_unified_patient(unified_profile)

    # 3. Label prediction source to indicate EMR adapter execution
    response.prediction_source = "emr_integration_adapter"
    response.status = "success"

    return response
