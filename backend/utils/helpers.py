"""
SentraX AI Backend — utils/helpers.py
Shared utility functions used across services and routes.
"""

import re
from datetime import datetime
from typing import Optional


def sanitise_string(value: str, max_length: int = 2048) -> str:
    """Strip leading/trailing whitespace and truncate to max_length."""
    return value.strip()[:max_length]


def parse_login_hour(login_time: str) -> Optional[int]:
    """
    Extract the hour component from a login time string.
    Accepts formats: 'HH:MM', 'HH:MM:SS', '3:15 AM', '03:15 PM'.
    Returns None if parsing fails.
    """
    s = login_time.strip()
    match = re.search(r"(\d{1,2}):(\d{2})", s)
    if not match:
        return None
    hour = int(match.group(1))
    if "pm" in s.lower() and hour < 12:
        hour += 12
    elif "am" in s.lower() and hour == 12:
        hour = 0
    return hour if 0 <= hour <= 23 else None


def get_threat_tier(score: int) -> tuple[str, str, str]:
    """
    Convert a numeric score (0–100) into a (tier_label, bar_color, tier_bg) tuple.
    Used consistently across all service layers.
    """
    if score >= 70:
        return "HIGH", "#ff3b30", "rgba(255,59,48,0.10)"
    elif score >= 40:
        return "MEDIUM", "#ffd60a", "rgba(255,214,10,0.08)"
    else:
        return "LOW", "#00ff87", "rgba(0,255,135,0.08)"


def utc_now_iso() -> str:
    """Return the current UTC time as an ISO 8601 string."""
    return datetime.utcnow().isoformat() + "Z"
