"""
SentraX AI Backend — schemas.py
Pydantic request/response models for all scan types.
Placeholder definitions — business logic added in a future sprint.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


# ── URL Scan ───────────────────────────────────────────────────────────────────

class URLScanRequest(BaseModel):
    url: str = Field(..., example="https://example.com/login", description="The URL to analyse.")

class URLScanResponse(BaseModel):
    url:             str
    label:           str            = Field(..., example="Safe",  description="Classification label.")
    score:           int            = Field(..., ge=0, le=100,    description="Threat score (0–100).")
    reasons:         List[str]      = Field(default_factory=list, description="Heuristic reasons.")
    technical:       Dict[str, Any] = Field(default_factory=dict, description="Low-level technical metrics.")
    confidence:      int            = Field(..., ge=0, le=100,    description="Detection confidence %.")
    threat_level:    str            = Field(..., example="LOW",   description="HIGH / MODERATE / LOW.")
    recommendations: List[str]      = Field(default_factory=list, description="Recommended actions.")
    external_intelligence: Optional[Dict[str, Any]] = Field(None, description="Third-party Threat Intelligence verdicts.")


# ── SMS Scan ───────────────────────────────────────────────────────────────────

class SMSScanRequest(BaseModel):
    message: str = Field(..., example="You have won a prize! Click here to claim.", description="SMS text to analyse.")

class SMSScanResponse(BaseModel):
    message: str
    label: str = Field(..., example="Legitimate")
    score: int = Field(..., ge=0, le=100)
    reasons: List[str] = Field(default_factory=list)
    confidence: int = Field(..., ge=0, le=100)
    threat_level: str = Field(..., example="LOW")
    recommendations: List[str] = Field(default_factory=list)
    external_intelligence: Optional[Dict[str, Any]] = Field(None, description="Third-party Threat Intelligence verdicts.")


# ── Fraud Scan ─────────────────────────────────────────────────────────────────

class FraudScanRequest(BaseModel):
    amount: float = Field(..., ge=0, example=25000.0, description="Transaction amount in INR.")
    location: str = Field(..., example="Mumbai", description="Transaction location.")
    device: str  = Field(..., example="new device", description="Device used for the transaction.")
    customer_id: Optional[str] = Field(None, example="CUST-001")

class FraudScanResponse(BaseModel):
    customer_id:     Optional[str]
    risk_score:      int            = Field(..., ge=0, le=100,    description="Fraud risk score 0-100.")
    status:          str            = Field(..., example="HIGH RISK",  description="HIGH RISK / LOW RISK label.")
    recommendation:  str            = Field(..., example="BLOCK / OTP VERIFY", description="Single recommended action.")
    reasons:         List[str]      = Field(default_factory=list, description="Triggered heuristic reasons.")
    confidence:      int            = Field(..., ge=0, le=100,    description="Detection confidence %.")
    threat_level:    str            = Field(..., example="HIGH",  description="HIGH / MEDIUM / LOW.")
    recommendations: List[str]      = Field(default_factory=list, description="Detailed recommended actions.")
    external_intelligence: Optional[Dict[str, Any]] = Field(None, description="Third-party Threat Intelligence verdicts.")


# ── Employee Scan ──────────────────────────────────────────────────────────────

class EmployeeScanRequest(BaseModel):
    employee: str = Field(..., example="john.doe", description="Employee identifier.")
    login_time: str = Field(..., example="03:15", description="Login time in HH:MM format.")
    department: Optional[str] = Field(None, example="Engineering")

class EmployeeScanResponse(BaseModel):
    employee: str
    login_time: str
    risk_level: str = Field(..., example="SUSPICIOUS")
    reasons: List[str] = Field(default_factory=list)
    confidence: int = Field(..., ge=0, le=100)
    threat_level: str = Field(..., example="MEDIUM")
    recommendations: List[str] = Field(default_factory=list)
    external_intelligence: Optional[Dict[str, Any]] = Field(None, description="Third-party Threat Intelligence verdicts.")
