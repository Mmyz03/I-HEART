"""
Hospital / EMR Integration Adapter
Normalizes and converts external/EMR patient records into the canonical
I-HEART UnifiedPatientProfile schema.
"""

from typing import Union, Dict, Any
from .emr_schemas import MockEMRPayload

try:
    from schemas import (
        UnifiedPatientProfile,
        Demographics,
        PhysicalMeasurements,
        VitalSigns,
        LaboratoryData,
        LifestyleData,
        MedicalHistory,
    )
except ImportError:
    from ..schemas import (
        UnifiedPatientProfile,
        Demographics,
        PhysicalMeasurements,
        VitalSigns,
        LaboratoryData,
        LifestyleData,
        MedicalHistory,
    )


class EMRAdapter:
    """
    Adapter responsible for converting EMR-style patient data into the internal
    UnifiedPatientProfile contract expected by I-HEART ML pipelines.
    """

    @staticmethod
    def normalize_gender(raw_gender: str) -> str:
        """Normalizes biological sex / gender string into standard form."""
        if not raw_gender or not isinstance(raw_gender, str):
            raise ValueError("Patient gender must be a non-empty string.")
        g = raw_gender.strip().lower()
        if "fem" in g:
            return "Female"
        if "male" in g:
            return "Male"
        return "Other"

    @staticmethod
    def calculate_or_validate_bmi(height_cm: float, weight_kg: float, provided_bmi: Union[float, None]) -> float:
        """
        Uses provided BMI if valid; otherwise computes standard BMI formula:
        BMI = weight_kg / (height_m ^ 2)
        """
        if height_cm <= 0:
            raise ValueError("Height must be greater than zero centimeters.")
        if weight_kg <= 0:
            raise ValueError("Weight must be greater than zero kilograms.")

        if provided_bmi is not None and 5.0 <= provided_bmi <= 90.0:
            return float(round(provided_bmi, 1))

        # Compute standard clinical BMI
        height_m = height_cm / 100.0
        calculated = weight_kg / (height_m * height_m)
        return float(round(calculated, 1))

    @staticmethod
    def normalize_smoking(raw_smoking: str) -> str:
        """Normalizes smoking status to Never, Former, or Current."""
        if not raw_smoking or not isinstance(raw_smoking, str):
            raise ValueError("Smoking status must be a non-empty string.")
        s = raw_smoking.strip().lower()
        if "current" in s or "smoke" in s and "non" not in s and "never" not in s and "not" not in s:
            return "Current"
        if "former" in s or "past" in s or "ex" in s or "quit" in s:
            return "Former"
        return "Never"

    @staticmethod
    def normalize_activity(raw_activity: str) -> str:
        """Normalizes physical activity level to Sedentary, Moderate, or Active."""
        if not raw_activity or not isinstance(raw_activity, str):
            raise ValueError("Physical activity level must be a non-empty string.")
        a = raw_activity.strip().lower()
        if "sedentary" in a or "low" in a or "none" in a or "inactive" in a:
            return "Sedentary"
        if "active" in a or "high" in a or "vigorous" in a:
            return "Active"
        return "Moderate"

    @staticmethod
    def normalize_alcohol(raw_alcohol: str) -> str:
        """Normalizes alcohol intake to None, Moderate, or Frequent."""
        if not raw_alcohol or not isinstance(raw_alcohol, str):
            raise ValueError("Alcohol consumption must be a non-empty string.")
        al = raw_alcohol.strip().lower()
        if "none" in al or "never" in al or "no" in al or "zero" in al or "abstain" in al:
            return "None"
        if "freq" in al or "heavy" in al or "daily" in al or "high" in al:
            return "Frequent"
        return "Moderate"

    @classmethod
    def emr_to_unified(cls, payload: Union[MockEMRPayload, Dict[str, Any]]) -> UnifiedPatientProfile:
        """
        Converts a MockEMRPayload into a canonical UnifiedPatientProfile.
        Performs strict field validation, type checking, and clinical normalization.
        """
        if isinstance(payload, dict):
            payload = MockEMRPayload(**payload)

        # 1. Demographics
        gender = cls.normalize_gender(payload.patient_identity.gender)
        demographics = Demographics(
            age=payload.patient_identity.age,
            gender=gender
        )

        # 2. Physical Measurements
        bmi = cls.calculate_or_validate_bmi(
            height_cm=payload.physical_measurements.height_cm,
            weight_kg=payload.physical_measurements.weight_kg,
            provided_bmi=payload.physical_measurements.bmi
        )
        physical = PhysicalMeasurements(
            height_cm=payload.physical_measurements.height_cm,
            weight_kg=payload.physical_measurements.weight_kg,
            bmi=bmi
        )

        # 3. Vitals
        vitals = VitalSigns(
            systolic_bp=payload.clinical_vitals.systolic_bp,
            diastolic_bp=payload.clinical_vitals.diastolic_bp,
            heart_rate=payload.clinical_vitals.heart_rate
        )

        # 4. Laboratory Results (Fasting glucose is required; lipid/HbA1c are optional)
        laboratory = LaboratoryData(
            glucose=payload.laboratory_results.fasting_glucose,
            hba1c=payload.laboratory_results.hba1c,
            total_cholesterol=payload.laboratory_results.total_cholesterol,
            hdl=payload.laboratory_results.hdl,
            ldl=payload.laboratory_results.ldl,
            triglycerides=payload.laboratory_results.triglycerides
        )

        # 5. Lifestyle Factors
        lifestyle = LifestyleData(
            smoking=cls.normalize_smoking(payload.lifestyle_history.smoking_status),
            physical_activity=cls.normalize_activity(payload.lifestyle_history.physical_activity_level),
            alcohol=cls.normalize_alcohol(payload.lifestyle_history.alcohol_consumption)
        )

        # 6. Medical History & Conditions
        med_history = MedicalHistory(
            hypertension=bool(payload.diagnoses_and_history.hypertension_diagnosed),
            existing_diabetes=bool(payload.diagnoses_and_history.existing_diabetes_diagnosed),
            family_history_diabetes=bool(payload.diagnoses_and_history.family_history_diabetes),
            family_history_cvd=bool(payload.diagnoses_and_history.family_history_cvd)
        )

        # Build Canonical Unified Patient Profile
        unified_profile = UnifiedPatientProfile(
            patient_id=payload.patient_identity.mrn,
            demographics=demographics,
            physical=physical,
            vitals=vitals,
            laboratory=laboratory,
            lifestyle=lifestyle,
            medical_history=med_history
        )

        return unified_profile
