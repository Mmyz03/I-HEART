"""
I-HEART Data Integration Layer
Provides EMR/Hospital data adapters and schema normalization.
"""

from .emr_schemas import (
    MockEMRPayload,
    EMRPatientIdentity,
    EMRPhysicalMeasurements,
    EMRClinicalVitals,
    EMRLaboratoryResults,
    EMRLifestyleHistory,
    EMRDiagnosesAndHistory,
)
from .emr_adapter import EMRAdapter
from .emr_service import process_emr_patient

__all__ = [
    "MockEMRPayload",
    "EMRPatientIdentity",
    "EMRPhysicalMeasurements",
    "EMRClinicalVitals",
    "EMRLaboratoryResults",
    "EMRLifestyleHistory",
    "EMRDiagnosesAndHistory",
    "EMRAdapter",
    "process_emr_patient",
]
