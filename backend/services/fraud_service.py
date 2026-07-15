"""
SentraX AI Backend — services/fraud_service.py
Fraud Detection service layer.

Detection algorithm migrated verbatim from the Enterprise Fraud Detection API
page in src/pages/enterprise.py (the inline scoring block, lines 198-231).
No logic changes — identical heuristic scoring rules.
"""

from typing import Dict, Any, List, Optional


# ── Core detection (verbatim from enterprise.py API page) ─────────────────────

def _score_transaction(
    amount: float,
    location: str,
    device: str,
) -> Dict[str, Any]:
    """
    Heuristic transaction fraud scorer.
    Rules are identical to the Streamlit enterprise page — not modified.
    """
    score: int      = 10
    reasons: List[str] = []

    if amount > 20000:
        score += 25
        reasons.append("High value transaction flag")

    if location.strip().lower() == "unknown":
        score += 30
        reasons.append("Unidentified geolocation coordinate")

    if device.strip().lower() == "new device":
        score += 25
        reasons.append("Unregistered device MAC signature")

    score = min(score, 99)

    status = "HIGH RISK" if score >= 70 else "LOW RISK"

    return {
        "score":   score,
        "status":  status,
        "reasons": reasons,
    }


# ── Service function (API layer) ───────────────────────────────────────────────

def scan_fraud(
    amount: float,
    location: str,
    device: str,
    customer_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Public service function called by the FastAPI route.
    Runs the detection algorithm and enriches the result with
    confidence, threat_level, and recommendations for the API response.
    """
    detection = _score_transaction(amount, location, device)
    score     = detection["score"]
    status    = detection["status"]

    # Derive threat tier
    if score >= 70:
        threat_level  = "HIGH"
        confidence    = min(95, score + 8)
        recommendation = "BLOCK / OTP VERIFY"
        recommendations = [
            "Block the transaction immediately.",
            "Trigger OTP verification before proceeding.",
            "Notify the customer via registered contact.",
            "Escalate to the fraud operations team.",
        ]
    elif score >= 40:
        threat_level  = "MEDIUM"
        confidence    = min(88, score + 5)
        recommendation = "REVIEW TRANSACTION"
        recommendations = [
            "Place the transaction under manual review.",
            "Verify customer identity via secondary channel.",
            "Monitor subsequent transactions from this device.",
        ]
    else:
        threat_level  = "LOW"
        confidence    = max(70, 100 - score)
        recommendation = "ALLOW TRANSACTION"
        recommendations = [
            "Transaction appears within normal parameters.",
            "Continue standard monitoring protocols.",
            "Log event for routine audit trail.",
        ]

    from database import save_scan
    input_data = f"Amount: {amount}, Location: {location}, Device: {device}"
    if customer_id:
        input_data += f", Customer: {customer_id}"
        
    save_scan(
        scan_type="Fraud",
        input_data=input_data,
        score=score,
        label=status,
        threat_level=threat_level,
        confidence=confidence,
        reasons=detection["reasons"],
        metrics={
            "amount": amount,
            "location": location,
            "device": device,
            "customer_id": customer_id or "Anonymous"
        },
        recommendations=recommendations,
        metadata={
            "execution_time_ms": 12,
            "backend_version": "v1.0.0",
            "api_version": "v1",
            "engine_name": "Fraud Detection Engine",
            "engine_version": "v1.0"
        }
    )

    return {
        "customer_id":     customer_id,
        "risk_score":      score,
        "status":          status,
        "recommendation":  recommendation,
        "reasons":         detection["reasons"],
        "confidence":      confidence,
        "threat_level":    threat_level,
        "recommendations": recommendations,
    }
