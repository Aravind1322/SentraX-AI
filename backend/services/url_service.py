"""
SentraX AI Backend — services/url_service.py
URL Intelligence service layer with improved enterprise threat scoring rules.
"""

import re
from urllib.parse import urlparse
from typing import Dict, Any

try:
    import validators
except ModuleNotFoundError:
    validators = None

import requests as http_requests


def _analyze_url_features(url: str) -> Dict[str, Any]:
    """
    Heuristic URL threat analyser.
    Scoring rules improved for enterprise phishing detection.
    """
    score = 0
    reasons = []

    https = url.startswith("https")
    ip_based = bool(re.search(r"\d+\.\d+\.\d+\.\d+", url))
    long_url = len(url) > 70

    # 1. Check Phishing Keywords with increased weights
    suspicious_words = [
        "login", "verify", "secure", "update", "account",
        "password", "paypal", "bank", "microsoft", "office365"
    ]
    keyword_hits = [w for w in suspicious_words if w in url.lower()]

    for word in keyword_hits:
        reasons.append(f"Suspicious keyword: {word}")
        score += 15  # Increased risk weight per keyword

    # Multi-keyword hit bonus
    if len(keyword_hits) >= 2:
        reasons.append("Multiple suspicious keywords detected")
        score += 20

    # 2. Check Suspicious TLD (.xyz, .top, .click, .tk, .cf, .gq)
    susp_tlds = [".xyz", ".top", ".click", ".tk", ".cf", ".gq"]
    
    # Extract hostname reliably
    parsed = urlparse(url)
    hostname = parsed.hostname or ""
    if not hostname:
        if not url.startswith(("http://", "https://")):
            parsed = urlparse("http://" + url)
            hostname = parsed.hostname or ""
        else:
            hostname = parsed.path.split('/')[0]
            
    has_susp_tld = any(hostname.lower().endswith(tld) for tld in susp_tlds)
    if has_susp_tld:
        reasons.append("Suspicious TLD detected")
        score += 25

    # 3. Connection & SSL check
    ssl_status = "Unknown"
    redirect_count = 0
    ssl_failed = False

    try:
        response = http_requests.get(url, timeout=5, allow_redirects=True)
        redirect_count = len(response.history)

        if redirect_count > 2:
            reasons.append(f"Multiple redirects ({redirect_count})")
            score += 15

        ssl_status = "Valid" if url.startswith("https") else "No SSL"

    except Exception:
        reasons.append("Connection / SSL validation failed")
        score += 25  # Increased weight for SSL/connection failure
        ssl_failed = True

    # 4. Scheme checks
    if not https:
        reasons.append("No HTTPS encryption")
        score += 20  # Increased weight for HTTP/no SSL

    # 5. Format & structure indicators
    if validators and not validators.url(url):
        reasons.append("Invalid URL format")
        score += 25

    if "@" in url:
        reasons.append("@ symbol detected")
        score += 20

    if long_url:
        reasons.append("Long suspicious URL")
        score += 15

    if ip_based:
        reasons.append("IP address based URL")
        score += 25

    # Cap maximum score at 99
    score = min(score, 99)

    # Classification boundaries:
    # Score >= 70: Fraud / Phishing
    # Score 40-69: Suspicious
    # Score < 40: Safe
    if score >= 70:
        label = "Fraud / Phishing"
    elif score >= 40:
        label = "Suspicious"
    else:
        label = "Safe"

    return {
        "label": label,
        "score": score,
        "reasons": reasons,
        "technical": {
            "HTTPS": "Yes" if https else "No",
            "IP Based": "Yes" if ip_based else "No",
            "Keyword Hits": len(keyword_hits),
            "Length": len(url),
            "SSL": ssl_status,
            "Redirects": redirect_count,
        },
    }


async def scan_url(url: str) -> Dict[str, Any]:
    """
    Public service function called by the FastAPI route.
    Runs the detection algorithm and enriches the result with
    threat_level, confidence, and recommendations for the API response.
    Queries external threat intelligence providers concurrently.
    """
    detection = _analyze_url_features(url)
    score = detection["score"]

    # Derive threat_level
    if score >= 70:
        threat_level = "HIGH"
        confidence = min(95, score + 10)
        recommendations = [
            "Do NOT open this URL in any browser.",
            "Block this domain at the network firewall.",
            "Report to your security team immediately.",
            "Warn users who may have received this link.",
        ]
    elif score >= 40:
        threat_level = "MEDIUM"
        confidence = min(90, score + 8)
        recommendations = [
            "Verify the URL origin before clicking.",
            "Check with IT security before proceeding.",
            "Do not enter credentials on this page.",
        ]
    else:
        threat_level = "LOW"
        confidence = max(75, 100 - score)
        recommendations = [
            "URL appears safe to access.",
            "Continue to monitor for unusual activity.",
            "Report any unexpected behaviour to IT.",
        ]

    # Query third-party threat intelligence concurrently
    external_intel = {}
    try:
        from services.external_intel_service import ExternalIntelService
        external_intel = await ExternalIntelService.run_lookup(url)
    except Exception as intel_err:
        import logging
        logging.getLogger("backend").warning(f"External lookup failed: {intel_err}")

    try:
        from database import save_scan
        save_scan(
            scan_type="URL",
            input_data=url,
            score=score,
            label=detection["label"],
            threat_level=threat_level,
            confidence=confidence,
            reasons=detection["reasons"],
            metrics=detection["technical"],
            recommendations=recommendations,
            metadata={
                "execution_time_ms": 15,
                "backend_version": "v1.0.0",
                "api_version": "v1",
                "engine_name": "URL Intelligence Engine",
                "engine_version": "v1.0"
            }
        )
    except Exception as db_err:
        import logging
        logging.getLogger("backend").warning(f"Database save_scan failed: {db_err}")

    return {
        "url": url,
        "label": detection["label"],
        "score": score,
        "reasons": detection["reasons"],
        "technical": detection["technical"],
        "confidence": confidence,
        "threat_level": threat_level,
        "recommendations": recommendations,
        "external_intelligence": external_intel,
    }
