"""
Hospital / EMR Integration Schemas
Defines structured EMR-style patient payload representations based exclusively
on the clinical fields supported by the I-HEART prediction platform.
"""

from typing import Optional
from pydantic import BaseModel, Field, model_validator


class EMRPatientIdentity(BaseModel):
    """Patient demographic and medical record identification."""
    mrn: str = Field(..., description="Hospital Medical Record Number or Patient ID")
    age: int = Field(..., ge=1, le=125, description="Patient age in completed years")
    gender: str = Field(..., description="Biological sex recorded in EMR (e.g., Male, Female, Other)")


class EMRPhysicalMeasurements(BaseModel):
    """Clinical anthropometric measurements."""
    height_cm: float = Field(..., ge=40.0, le=260.0, description="Height in centimeters")
    weight_kg: float = Field(..., ge=15.0, le=350.0, description="Weight in kilograms")
    bmi: Optional[float] = Field(
        None,
        ge=5.0,
        le=90.0,
        description="Calculated BMI. If null, automatically computed from height and weight."
    )


class EMRClinicalVitals(BaseModel):
    """Hemodynamic and vital signs from clinical encounter."""
    systolic_bp: int = Field(..., ge=60, le=260, description="Systolic blood pressure (mmHg)")
    diastolic_bp: int = Field(..., ge=40, le=160, description="Diastolic blood pressure (mmHg)")
    heart_rate: int = Field(..., ge=35, le=220, description="Resting heart rate (bpm)")

    @model_validator(mode="after")
    def validate_bp_relationship(self):
        if self.diastolic_bp >= self.systolic_bp:
            raise ValueError(
                f"Diastolic blood pressure ({self.diastolic_bp} mmHg) must be strictly lower than "
                f"systolic blood pressure ({self.systolic_bp} mmHg)."
            )
        return self


class EMRLaboratoryResults(BaseModel):
    """Diagnostic laboratory measurements (glycemic & lipid panel)."""
    fasting_glucose: float = Field(..., ge=30.0, le=500.0, description="Fasting plasma glucose (mg/dL)")
    hba1c: Optional[float] = Field(None, ge=3.0, le=18.0, description="Glycated hemoglobin HbA1c (%)")
    total_cholesterol: Optional[float] = Field(None, ge=50.0, le=500.0, description="Total serum cholesterol (mg/dL)")
    hdl: Optional[float] = Field(None, ge=10.0, le=150.0, description="High-density lipoprotein (mg/dL)")
    ldl: Optional[float] = Field(None, ge=20.0, le=350.0, description="Low-density lipoprotein (mg/dL)")
    triglycerides: Optional[float] = Field(None, ge=30.0, le=800.0, description="Serum triglycerides (mg/dL)")


class EMRLifestyleHistory(BaseModel):
    """Social and behavioral health history."""
    smoking_status: str = Field(..., description="Tobacco smoking status (e.g., Never, Former, Current)")
    physical_activity_level: str = Field(..., description="Physical activity frequency (Sedentary, Moderate, Active)")
    alcohol_consumption: str = Field(..., description="Alcohol use pattern (None, Moderate, Frequent)")


class EMRDiagnosesAndHistory(BaseModel):
    """Documented medical conditions and family predisposition."""
    hypertension_diagnosed: bool = Field(False, description="Clinically diagnosed hypertension")
    existing_diabetes_diagnosed: bool = Field(False, description="Prior documented diagnosis of diabetes")
    family_history_diabetes: bool = Field(False, description="Documented family history of diabetes")
    family_history_cvd: bool = Field(False, description="Documented family history of cardiovascular disease")


class MockEMRPayload(BaseModel):
    """
    Mock Hospital / EMR Patient Record Payload.
    Represents an external hospital data extraction format mapped into I-HEART.
    NOTE: Development and test representation; not a formal HL7/FHIR standard.
    """
    resource_type: str = Field("MockEMRPatientRecord", description="EMR resource descriptor")
    emr_system_id: str = Field(..., description="Source hospital or EMR system identifier (e.g., HOSP-METRO-01)")
    patient_identity: EMRPatientIdentity
    physical_measurements: EMRPhysicalMeasurements
    clinical_vitals: EMRClinicalVitals
    laboratory_results: EMRLaboratoryResults
    lifestyle_history: EMRLifestyleHistory
    diagnoses_and_history: EMRDiagnosesAndHistory
