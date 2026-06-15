import re
try:
    import validators
except ModuleNotFoundError:
    validators = None
import requests


def analyze_url_features(url: str):
    score = 0
    reasons = []

    https = url.startswith("https")
    ip_based = bool(re.search(r"\d+\.\d+\.\d+\.\d+", url))
    long_url = len(url) > 70

    suspicious_words = ["login", "verify", "bank", "secure", "update", "account"]
    keyword_hits = [w for w in suspicious_words if w in url.lower()]

    ssl_status = "Unknown"
    redirect_count = 0

    try:
        response = requests.get(
            url,
            timeout=5,
            allow_redirects=True
        )

        redirect_count = len(response.history)

        if redirect_count > 2:
            reasons.append(f"Multiple redirects ({redirect_count})")
            score += 15

        ssl_status = "Valid" if url.startswith("https") else "No SSL"

    except:
        reasons.append("Connection / SSL validation failed")
        score += 20

    if not validators.url(url):
        reasons.append("Invalid URL format")
        score += 25

    if not https:
        reasons.append("No HTTPS encryption")
        score += 15

    for word in keyword_hits:
        reasons.append(f"Suspicious keyword: {word}")
        score += 12

    if "@" in url:
        reasons.append("@ symbol detected")
        score += 20

    if long_url:
        reasons.append("Long suspicious URL")
        score += 15

    if ip_based:
        reasons.append("IP address based URL")
        score += 25

    score = min(score, 99)

    label = "Fraud / Phishing" if score >= 50 else "Safe"

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
            "Redirects": redirect_count
        }
    }


def predict_url(url: str):
    return analyze_url_features(url)


def predict_sms(message: str):
    suspicious = ["win", "prize", "urgent", "otp", "claim", "click"]

    score = 5
    reasons = []

    for word in suspicious:
        if word in message.lower():
            score += 15
            reasons.append(f"Suspicious word: {word}")

    score = min(score, 95)

    label = "Scam Message" if score >= 50 else "Legitimate"

    return {
        "label": label,
        "score": score,
        "reasons": reasons
    }


def score_fraud_row(row):
    import pandas as pd
    s = 10
    if pd.to_numeric(row["amount"], errors="coerce") > 20000:
        s += 25
    if str(row["location"]).strip().lower() == "unknown":
        s += 30
    if str(row["device"]).strip().lower() == "new device":
        s += 25
    return min(s, 99)


def get_fraud_status(score):
    if score >= 70:
        return "HIGH RISK"
    elif score >= 40:
        return "MEDIUM RISK"
    else:
        return "LOW RISK"