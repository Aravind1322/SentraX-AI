"""
SentraX AI — Explainability Engine
====================================
Generates human-readable AI Analysis cards: reasons, confidence, and
recommended actions — one function per scan type.

No external calls. Pure heuristic introspection.
"""

import streamlit as st


# ─────────────────────────────────────────────────────────────────────────────
# Shared card renderer
# ─────────────────────────────────────────────────────────────────────────────

def _render_ai_card(reasons: list, confidence: int, recommendations: list,
                    tier_label: str, bar_color: str, tier_bg: str):
    """Render the shared glass-morphic AI Analysis card."""

    # Build reason bullets HTML
    if reasons:
        bullets_html = "".join(
            f'<div style="display:flex;align-items:flex-start;gap:10px;'
            f'padding:7px 0;border-bottom:1px solid rgba(0,240,255,0.06);">'
            f'<span style="color:#00f0ff;font-size:14px;flex-shrink:0;">▸</span>'
            f'<span style="font-family:\'JetBrains Mono\',monospace;font-size:13px;'
            f'color:#c9e8f5;line-height:1.5;">{r}</span>'
            f'</div>'
            for r in reasons
        )
    else:
        bullets_html = (
            '<div style="font-family:\'JetBrains Mono\',monospace;font-size:13px;'
            'color:#00ff87;padding:6px 0;">✅ No suspicious indicators detected. '
            'Classification: clean.</div>'
        )

    # Confidence bar
    conf_color = (
        "#ff3b30" if confidence >= 85
        else "#ffd60a" if confidence >= 65
        else "#00ff87"
    )
    conf_filled = "█" * (confidence // 10)
    conf_empty  = "░" * (10 - confidence // 10)

    # Recommendation list HTML
    rec_html = "".join(
        f'<div style="display:flex;align-items:flex-start;gap:10px;'
        f'padding:6px 0;border-bottom:1px solid rgba(0,240,255,0.05);">'
        f'<span style="color:#ffd60a;flex-shrink:0;">•</span>'
        f'<span style="font-family:\'JetBrains Mono\',monospace;font-size:13px;'
        f'color:#e0f0ff;">{r}</span>'
        f'</div>'
        for r in recommendations
    )

    st.markdown(f"""
    <div style="
        background: rgba(6,18,36,0.60);
        border: 1px solid rgba(0,240,255,0.16);
        border-left: 4px solid #00f0ff;
        border-radius: 18px;
        padding: 26px 28px;
        margin: 22px 0;
        backdrop-filter: blur(14px);
        box-shadow: 0 8px 36px rgba(0,0,0,0.40), 0 0 22px rgba(0,240,255,0.06);
    ">
        <div style="display:flex;align-items:center;justify-content:space-between;
                    margin-bottom:18px;padding-bottom:12px;
                    border-bottom:1px solid rgba(0,240,255,0.12);">
            <div style="display:flex;align-items:center;gap:10px;">
                <span style="font-size:20px;">🤖</span>
                <span style="font-family:'Orbitron',sans-serif;font-size:13px;
                             font-weight:700;letter-spacing:2.5px;
                             text-transform:uppercase;color:#00f0ff;">AI Analysis</span>
            </div>
            <span style="font-family:'JetBrains Mono',monospace;font-size:10px;
                         color:#63768f;letter-spacing:1px;">
                SENTRAX EXPLAINABILITY ENGINE v1.0
            </span>
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:24px;">
            <div>
                <div style="font-family:'Orbitron',sans-serif;font-size:10px;
                             font-weight:700;letter-spacing:2px;color:#8be8ff;
                             text-transform:uppercase;margin-bottom:10px;">
                    📋 Reason
                </div>
                {bullets_html}
            </div>
            <div>
                <div style="font-family:'Orbitron',sans-serif;font-size:10px;
                             font-weight:700;letter-spacing:2px;color:#8be8ff;
                             text-transform:uppercase;margin-bottom:10px;">
                    📈 Confidence
                </div>
                <div style="font-family:'Orbitron',sans-serif;font-size:30px;
                             font-weight:800;color:{conf_color};margin-bottom:6px;">
                    {confidence}%
                </div>
                <div style="width:100%;height:8px;background:rgba(255,255,255,0.05);
                             border-radius:6px;overflow:hidden;margin-bottom:6px;
                             border:1px solid rgba(255,255,255,0.06);">
                    <div style="width:{confidence}%;height:100%;border-radius:6px;
                                 background:linear-gradient(90deg,#00f0ff,{conf_color});
                                 box-shadow:0 0 8px {conf_color};"></div>
                </div>
                <div style="font-family:'JetBrains Mono',monospace;font-size:12px;
                             color:{conf_color};letter-spacing:2px;margin-bottom:16px;">
                    {conf_filled}{conf_empty}
                </div>
                <div style="display:inline-flex;align-items:center;gap:8px;
                             padding:5px 14px;border-radius:8px;margin-bottom:18px;
                             background:{tier_bg};border:1px solid {bar_color}44;">
                    <span style="font-family:'Orbitron',sans-serif;font-size:11px;
                                  font-weight:700;letter-spacing:1.5px;
                                  text-transform:uppercase;color:{bar_color};">
                        Threat Level: {tier_label}
                    </span>
                </div>
                <div style="font-family:'Orbitron',sans-serif;font-size:10px;
                             font-weight:700;letter-spacing:2px;color:#ffd60a;
                             text-transform:uppercase;margin-bottom:10px;">
                    🛡 Recommended Actions
                </div>
                {rec_html}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Per-scan-type explainers
# ─────────────────────────────────────────────────────────────────────────────

def explain_url(result: dict):
    """Explainability card for the URL Scanner."""
    score   = result["score"]
    reasons = result.get("reasons", [])
    tech    = result.get("technical", {})

    # Enrich reasons with human-readable labels
    human_reasons = []
    for r in reasons:
        if "keyword" in r.lower():
            word = r.split(":")[-1].strip()
            human_reasons.append(f"Banking / phishing keyword detected: '{word}'")
        elif "redirect" in r.lower():
            human_reasons.append(f"Multiple redirect hops found — common in phishing chains.")
        elif "ssl" in r.lower() or "connection" in r.lower():
            human_reasons.append("SSL certificate validation failed or connection refused.")
        elif "https" in r.lower():
            human_reasons.append("No HTTPS encryption — data may be intercepted.")
        elif "ip" in r.lower():
            human_reasons.append("IP-address-based URL — legitimate sites use domain names.")
        elif "long" in r.lower():
            human_reasons.append("Abnormally long URL — used to obscure the real destination.")
        elif "@" in r.lower():
            human_reasons.append("@ symbol in URL — used to trick browsers into ignoring the domain.")
        elif "invalid" in r.lower():
            human_reasons.append("URL format is invalid — not a well-formed web address.")
        else:
            human_reasons.append(r)

    if not human_reasons and score < 50:
        human_reasons = ["URL format appears valid.", "No suspicious keywords detected.",
                          "HTTPS encryption present.", "No redirect anomalies found."]

    confidence = min(95, score + 10) if score >= 50 else max(75, 100 - score)

    if score >= 70:
        recommendations = [
            "Do NOT open this URL in any browser.",
            "Block this domain at the network firewall.",
            "Report to your security team immediately.",
            "Warn users who may have received this link.",
        ]
        tier_label, bar_color, tier_bg = "HIGH", "#ff3b30", "rgba(255,59,48,0.10)"
    elif score >= 50:
        recommendations = [
            "Verify the URL origin before clicking.",
            "Check with IT security before proceeding.",
            "Do not enter credentials on this page.",
        ]
        tier_label, bar_color, tier_bg = "MODERATE", "#ffd60a", "rgba(255,214,10,0.08)"
    else:
        recommendations = [
            "URL appears safe to access.",
            "Continue to monitor for unusual activity.",
            "Report any unexpected behaviour to IT.",
        ]
        tier_label, bar_color, tier_bg = "LOW", "#00ff87", "rgba(0,255,135,0.08)"

    _render_ai_card(human_reasons, confidence, recommendations,
                    tier_label, bar_color, tier_bg)


def explain_sms(result: dict):
    """Explainability card for the SMS Scanner."""
    score   = result["score"]
    reasons = result.get("reasons", [])

    keyword_map = {
        "win":    "Prize / win keyword detected — classic lottery scam tactic.",
        "prize":  "Prize offer keyword found — unsolicited prize offers are scam signals.",
        "urgent": "Urgency language detected — creates panic to bypass rational judgement.",
        "otp":    "OTP / verification request detected — possible credential harvesting.",
        "claim":  "Claim action keyword found — pressures victim into immediate response.",
        "click":  "Click-here instruction detected — often leads to phishing pages.",
    }
    human_reasons = []
    for r in reasons:
        for kw, label in keyword_map.items():
            if kw in r.lower():
                human_reasons.append(label)
                break
        else:
            human_reasons.append(r)

    if not human_reasons and score < 50:
        human_reasons = [
            "No scam keywords detected in message body.",
            "Message does not contain urgency language.",
            "No OTP or prize-related content found.",
        ]

    confidence = min(95, score + 8) if score >= 50 else max(72, 100 - score)

    if score >= 70:
        recommendations = [
            "Do NOT reply to this message.",
            "Do NOT click any links in the message.",
            "Block the sender immediately.",
            "Report as spam to your carrier.",
        ]
        tier_label, bar_color, tier_bg = "HIGH", "#ff3b30", "rgba(255,59,48,0.10)"
    elif score >= 50:
        recommendations = [
            "Verify the sender's identity independently.",
            "Do not share personal or financial details.",
            "Contact the alleged organisation via official channels.",
        ]
        tier_label, bar_color, tier_bg = "MODERATE", "#ffd60a", "rgba(255,214,10,0.08)"
    else:
        recommendations = [
            "Message appears legitimate.",
            "Remain cautious with unsolicited messages.",
            "Verify sender if response is required.",
        ]
        tier_label, bar_color, tier_bg = "LOW", "#00ff87", "rgba(0,255,135,0.08)"

    _render_ai_card(human_reasons, confidence, recommendations,
                    tier_label, bar_color, tier_bg)


def explain_fraud_row(row: dict, score: int, status: str):
    """Explainability card for a single fraud transaction row."""
    import pandas as pd

    human_reasons = []
    try:
        amount = pd.to_numeric(row.get("amount", 0), errors="coerce")
        if amount > 20000:
            human_reasons.append(f"Transaction amount ₹{amount:,.0f} exceeds high-risk threshold (₹20,000).")
    except Exception:
        pass

    location = str(row.get("location", "")).strip().lower()
    if location == "unknown":
        human_reasons.append("Transaction location marked as 'Unknown' — unverifiable origin.")

    device = str(row.get("device", "")).strip().lower()
    if device == "new device":
        human_reasons.append("Transaction initiated from a new / unrecognised device.")

    if not human_reasons:
        human_reasons = [
            "All transaction parameters within normal thresholds.",
            "No high-risk device or location signals detected.",
            "Amount within acceptable limits.",
        ]

    confidence = 90 if score >= 70 else 75 if score >= 40 else 70

    if status == "HIGH RISK":
        recommendations = [
            "Freeze this transaction immediately.",
            "Verify customer identity via secondary authentication.",
            "Flag account for enhanced monitoring.",
            "Notify fraud investigation team.",
        ]
        tier_label, bar_color, tier_bg = "HIGH", "#ff3b30", "rgba(255,59,48,0.10)"
    elif status == "MEDIUM RISK":
        recommendations = [
            "Request additional verification from customer.",
            "Place transaction on hold pending review.",
            "Monitor account activity for 24 hours.",
        ]
        tier_label, bar_color, tier_bg = "MEDIUM", "#ffd60a", "rgba(255,214,10,0.08)"
    else:
        recommendations = [
            "Transaction appears within normal parameters.",
            "Continue standard monitoring protocols.",
            "No immediate action required.",
        ]
        tier_label, bar_color, tier_bg = "LOW", "#00ff87", "rgba(0,255,135,0.08)"

    _render_ai_card(human_reasons, confidence, recommendations,
                    tier_label, bar_color, tier_bg)


def explain_url_batch(total: int, suspicious: int):
    """Explainability card for batch URL Quick Scan results."""
    safe = total - suspicious
    pct  = round((suspicious / total) * 100) if total else 0

    human_reasons = []
    if suspicious > 0:
        human_reasons.append(f"{suspicious} of {total} URLs contain phishing/banking keywords.")
        human_reasons.append(f"{pct}% of scanned URLs flagged as suspicious.")
    if safe > 0:
        human_reasons.append(f"{safe} URL(s) passed all heuristic checks.")
    if not human_reasons:
        human_reasons = ["No URLs were detected in the dataset."]

    confidence = min(92, 60 + pct) if suspicious > 0 else 80
    score      = pct

    if suspicious > 0:
        recommendations = [
            "Block all flagged URLs at the proxy / firewall.",
            "Alert users who may have received these links.",
            "Submit flagged URLs for threat intelligence review.",
        ]
        tier_label, bar_color, tier_bg = "HIGH" if pct > 50 else "MODERATE", \
            "#ff3b30" if pct > 50 else "#ffd60a", \
            "rgba(255,59,48,0.10)" if pct > 50 else "rgba(255,214,10,0.08)"
    else:
        recommendations = [
            "All URLs passed the scan — no immediate action required.",
            "Continue routine URL hygiene practices.",
        ]
        tier_label, bar_color, tier_bg = "LOW", "#00ff87", "rgba(0,255,135,0.08)"

    _render_ai_card(human_reasons, confidence, recommendations,
                    tier_label, bar_color, tier_bg)


def explain_sms_batch(total: int, scam: int):
    """Explainability card for batch SMS / TXT Quick Scan results."""
    safe = total - scam
    pct  = round((scam / total) * 100) if total else 0

    human_reasons = []
    if scam > 0:
        human_reasons.append(f"{scam} of {total} messages contain scam keywords.")
        human_reasons.append(f"{pct}% of messages flagged as potential scam.")
    if safe > 0:
        human_reasons.append(f"{safe} message(s) appear clean with no suspicious language.")
    if not human_reasons:
        human_reasons = ["No messages were detected in the dataset."]

    confidence = min(90, 55 + pct) if scam > 0 else 80

    if scam > 0:
        recommendations = [
            "Block sending numbers associated with scam messages.",
            "Report batch to your carrier's spam reporting system.",
            "Educate users on recognising scam message patterns.",
        ]
        tier_label, bar_color, tier_bg = "HIGH" if pct > 50 else "MODERATE", \
            "#ff3b30" if pct > 50 else "#ffd60a", \
            "rgba(255,59,48,0.10)" if pct > 50 else "rgba(255,214,10,0.08)"
    else:
        recommendations = [
            "No scam messages detected — no action required.",
            "Continue standard communication monitoring.",
        ]
        tier_label, bar_color, tier_bg = "LOW", "#00ff87", "rgba(0,255,135,0.08)"

    _render_ai_card(human_reasons, confidence, recommendations,
                    tier_label, bar_color, tier_bg)


def explain_employee_batch(total: int, suspicious: int):
    """Explainability card for batch Employee Quick Scan results."""
    normal = total - suspicious
    pct    = round((suspicious / total) * 100) if total else 0

    human_reasons = []
    if suspicious > 0:
        human_reasons.append(f"{suspicious} employee login(s) occurred outside business hours (before 06:00).")
        human_reasons.append("Irregular login time is a primary indicator of insider threat or account compromise.")
    if normal > 0:
        human_reasons.append(f"{normal} login(s) fall within expected business-hour windows.")
    if not human_reasons:
        human_reasons = ["No employee records were detected in the dataset."]

    confidence = min(88, 55 + pct) if suspicious > 0 else 80

    if suspicious > 0:
        recommendations = [
            "Review login logs for flagged employees.",
            "Verify whether after-hours access was pre-authorised.",
            "Enforce multi-factor authentication on all accounts.",
            "Escalate repeat offenders to HR and security teams.",
        ]
        tier_label, bar_color, tier_bg = "MEDIUM", "#ffd60a", "rgba(255,214,10,0.08)"
    else:
        recommendations = [
            "All logins fall within expected hours — no action required.",
            "Continue routine employee activity monitoring.",
        ]
        tier_label, bar_color, tier_bg = "LOW", "#00ff87", "rgba(0,255,135,0.08)"

    _render_ai_card(human_reasons, confidence, recommendations,
                    tier_label, bar_color, tier_bg)
