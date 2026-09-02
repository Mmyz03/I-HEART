"""
AI-Based Explainable Health Risk Prediction System
Pydantic Schemas for Unified Patient Profile and Prediction Responses
"""

from typing import Optional, List
from pydantic import BaseModel, Field


# -----------------------------------------------------------------------------
# Section 1: Demographics
# -----------------------------------------------------------------------------
class Demographics(BaseModel):
    age: int = Field(..., ge=1, le=125, description="Patient age in years")
    gender: str = Field(..., description="Biological sex / gender (e.g., Male, Female, Other)")


# -----------------------------------------------------------------------------
# Section 2: Physical Measurements
# -----------------------------------------------------------------------------
class PhysicalMeasurements(BaseModel):
    height_cm: float = Field(..., ge=40.0, le=260.0, description="Height in centimeters")
    weight_kg: float = Field(..., ge=15.0, le=350.0, description="Weight in kilograms")
    bmi: float = Field(..., ge=5.0, le=90.0, description="Body Mass Index calculated as weight/(height/100)^2")


# -----------------------------------------------------------------------------
# Section 3: Vital Signs
# -----------------------------------------------------------------------------
class VitalSigns(BaseModel):
    systolic_bp: int = Field(..., ge=60, le=260, description="Systolic Blood Pressure in mmHg")
    diastolic_bp: int = Field(..., ge=40, le=160, description="Diastolic Blood Pressure in mmHg")
    heart_rate: int = Field(..., ge=35, le=220, description="Resting Heart Rate in bpm")


# -----------------------------------------------------------------------------
# Section 4: Laboratory Data
# -----------------------------------------------------------------------------
class LaboratoryData(BaseModel):
    glucose: float = Field(..., ge=30.0, le=500.0, description="Fasting Blood Glucose in mg/dL")
    hba1c: Optional[float] = Field(None, ge=3.0, le=18.0, description="Glycated Hemoglobin HbA1c in %")
    total_cholesterol: Optional[float] = Field(None, ge=50.0, le=500.0, description="Total Cholesterol in mg/dL")
    hdl: Optional[float] = Field(None, ge=10.0, le=150.0, description="High-Density Lipoprotein HDL in mg/dL")
    ldl: Optional[float] = Field(None, ge=20.0, le=350.0, description="Low-Density Lipoprotein LDL in mg/dL")
    triglycerides: Optional[float] = Field(None, ge=30.0, le=800.0, description="Serum Triglycerides in mg/dL")


# -----------------------------------------------------------------------------
# Section 5: Lifestyle Factors
# -----------------------------------------------------------------------------
class LifestyleData(BaseModel):
    smoking: str = Field(..., description="Smoking status (Never, Former, Current)")
    physical_activity: str = Field(..., description="Activity level (Sedentary, Moderate, Active)")
    alcohol: str = Field(..., description="Alcohol consumption (None, Moderate, Frequent)")


# -----------------------------------------------------------------------------
# Section 6: Medical History
# -----------------------------------------------------------------------------
class MedicalHistory(BaseModel):
    hypertension: bool = Field(False, description="Diagnosed hypertension")
    existing_diabetes: bool = Field(False, description="Diagnosed diabetes")
    family_history_diabetes: bool = Field(False, description="Family history of diabetes")
    family_history_cvd: bool = Field(False, description="Family history of cardiovascular disease")


# -----------------------------------------------------------------------------
# Unified Patient Health Profile (Single Intake Schema)
# -----------------------------------------------------------------------------
class UnifiedPatientProfile(BaseModel):
    patient_id: str = Field(..., description="Unique Patient Identifier or Reference Code")
    demographics: Demographics
    physical: PhysicalMeasurements
    vitals: VitalSigns
    laboratory: LaboratoryData
    lifestyle: LifestyleData
    medical_history: MedicalHistory


# -----------------------------------------------------------------------------
# Prediction Response Models
# -----------------------------------------------------------------------------
class DiseaseRiskResult(BaseModel):
    risk_percentage: int = Field(..., ge=0, le=100, description="Estimated risk percentage (0-100%)")
    risk_level: str = Field(..., description="Categorical classification: Low, Moderate, High")
    contributing_factors: List[str] = Field(default_factory=list, description="Primary clinical indicators influencing the risk")
    summary_note: str = Field(..., description="Clinical context note for the calculated risk")


class PredictionsContainer(BaseModel):
    diabetes: DiseaseRiskResult
    cardiovascular: DiseaseRiskResult


class AnalysisResponse(BaseModel):
    status: str = Field("prototype", description="System operational mode")
    prediction_source: str = Field("prototype_mock", description="Source of prediction logic")
    disclaimer: str = Field(
        "Academic prototype demonstration only. Not a medical diagnostic tool.",
        description="Standard academic research disclaimer"
    )
    patient: UnifiedPatientProfile
    predictions: PredictionsContainer
