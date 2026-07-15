"""
SentraX AI Backend — services/sms_service.py
SMS Shield service layer.

Detection algorithm migrated verbatim from src/utils/detector.py (predict_sms).
No logic changes — identical keyword scoring rules.
"""

from typing import Dict, Any, List


# ── Core detection (verbatim from src/utils/detector.py) ──────────────────────

def _predict_sms(message: str) -> Dict[str, Any]:
    """
    Keyword-based SMS scam detector.
    Scoring rules are identical to the Streamlit detector — not modified.
    """
    suspicious: List[str] = ["win", "prize", "urgent", "otp", "claim", "click"]

    score   = 5
    reasons = []

    for word in suspicious:
        if word in message.lower():
            score += 15
            reasons.append(f"Suspicious word: {word}")

    score = min(score, 95)
    label = "Scam Message" if score >= 50 else "Legitimate"

    return {
        "label":   label,
        "score":   score,
        "reasons": reasons,
    }


# ── Service function (API layer) ───────────────────────────────────────────────

def scan_sms(message: str) -> Dict[str, Any]:
    """
    Public service function called by the FastAPI route.
    Runs the detection algorithm and enriches the result with
    confidence, threat_level, and recommendations for the API response.
    """
    detection = _predict_sms(message)
    score     = detection["score"]
    label     = detection["label"]

    # Derive threat tier
    if score >= 70:
        threat_level  = "HIGH"
        confidence    = min(95, score + 8)
        recommendations = [
            "Do NOT reply to this message.",
            "Do NOT click any links in the message.",
            "Block the sender immediately.",
            "Report as spam to your carrier.",
        ]
    elif score >= 50:
        threat_level  = "MODERATE"
        confidence    = min(90, score + 5)
        recommendations = [
            "Verify the sender's identity independently.",
            "Do not share personal or financial details.",
            "Contact the alleged organisation via official channels.",
        ]
    else:
        threat_level  = "LOW"
        confidence    = max(72, 100 - score)
        recommendations = [
            "Message appears legitimate.",
            "Remain cautious with unsolicited messages.",
            "Verify sender if response is required.",
        ]

    from database import save_scan
    save_scan(
        scan_type="SMS",
        input_data=message,
        score=score,
        label=label,
        threat_level=threat_level,
        confidence=confidence,
        reasons=detection["reasons"],
        metrics={"length": len(message)},
        recommendations=recommendations,
        metadata={
            "execution_time_ms": 10,
            "backend_version": "v1.0.0",
            "api_version": "v1",
            "engine_name": "SMS Shield Engine",
            "engine_version": "v1.0"
        }
    )

    return {
        "message":         message,
        "label":           label,
        "score":           score,
        "reasons":         detection["reasons"],
        "confidence":      confidence,
        "threat_level":    threat_level,
        "recommendations": recommendations,
    }
