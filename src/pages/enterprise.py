import streamlit as st
import pandas as pd
import requests as http_requests
from src.utils.detector import predict_url, predict_sms, score_fraud_row, get_fraud_status
from src.utils.database import get_recent_scans
from src.utils.auth_state import get_auth_headers, BACKEND_URL as _BACKEND_URL


def _call_backend_fraud(amount: float, location: str, device: str, api_key: str):
    """
    POST to /api/fraud/scan and return the result dict,
    or None if the backend is unavailable.
    """
    try:
        resp = http_requests.post(
            f"{_BACKEND_URL}/api/fraud/scan",
            json={
                "amount":      amount,
                "location":    location,
                "device":      device,
                "customer_id": api_key,
            },
            headers=get_auth_headers(),
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        return {
            "score":          data.get("risk_score", 10),
            "status":         data.get("status", "LOW RISK"),
            "recommendation": data.get("recommendation", "ALLOW TRANSACTION"),
            "reasons":        data.get("reasons", []),
        }
    except (http_requests.ConnectionError, http_requests.Timeout):
        return None
    except Exception:
        return None



def render_enterprise():
    # Inject page styles
    st.markdown("""
    <style>
    .telemetry-card {
        background: rgba(6, 18, 36, 0.45); 
        border: 1px solid rgba(0, 240, 255, 0.12); 
        border-radius: 12px; 
        padding: 16px 20px; 
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); 
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    .telemetry-card:hover {
        border-color: rgba(0, 240, 255, 0.35);
        box-shadow: 0 8px 30px rgba(0, 240, 255, 0.08);
        transform: translateY(-2px);
    }
    </style>
    """, unsafe_allow_html=True)

    if "enterprise_page" not in st.session_state:
        st.session_state.enterprise_page = "main"

    page = st.session_state.enterprise_page

    # ================= MAIN MENU =================

    if page == "main":

        st.markdown(
            '<div class="brand">Enterprise Shield</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="tag">// BUSINESS FRAUD TELEMETRY CONTROL PANEL</div>',
            unsafe_allow_html=True
        )

        st.markdown("""
        <div style="margin-top: 15px; margin-bottom: 25px;">
            <p style="text-align: center; font-size: 15px; color: #8be8ff; font-family: 'JetBrains Mono', monospace;">
                [CONNECTED] ACCESS LEVEL: SECURE SOC CONSOLE // SELECT MODULE TO INITIALIZE
            </p>
        </div>
        """, unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        c3, c4 = st.columns(2)
        c5, c6 = st.columns(2)

        with c1:
            st.markdown("""
            <div style="margin-bottom: 10px; font-family: 'JetBrains Mono', monospace; font-size: 12px; color: #63768f; text-align: center;">
                MODULE 01 // API_GATEWAY
            </div>
            """, unsafe_allow_html=True)
            if st.button(
                "📡 Fraud Detection API",
                width="stretch"
            ):
                st.session_state.enterprise_page = "api"
                st.rerun()

        with c2:
            st.markdown("""
            <div style="margin-bottom: 10px; font-family: 'JetBrains Mono', monospace; font-size: 12px; color: #63768f; text-align: center;">
                MODULE 02 // PERSONNEL_AUDIT
            </div>
            """, unsafe_allow_html=True)
            if st.button(
                "🛡️ Employee Monitoring",
                width="stretch"
            ):
                st.session_state.enterprise_page = "employee"
                st.rerun()

        with c3:
            st.markdown("""
            <div style="margin-bottom: 10px; font-family: 'JetBrains Mono', monospace; font-size: 12px; color: #63768f; text-align: center;">
                MODULE 03 // PHISHING_SMS_FILTER
            </div>
            """, unsafe_allow_html=True)
            if st.button(
                "⚡ Scam Filtering",
                width="stretch"
            ):
                st.session_state.enterprise_page = "scam"
                st.rerun()

        with c4:
            st.markdown("""
            <div style="margin-bottom: 10px; font-family: 'JetBrains Mono', monospace; font-size: 12px; color: #63768f; text-align: center;">
                MODULE 04 // URL_HEURISTICS
            </div>
            """, unsafe_allow_html=True)
            if st.button(
                "🌐 URL Intelligence",
                width="stretch"
            ):
                st.session_state.enterprise_page = "url"
                st.rerun()

        with c5:
            st.markdown("""
            <div style="margin-bottom: 10px; font-family: 'JetBrains Mono', monospace; font-size: 12px; color: #63768f; text-align: center;">
                MODULE 05 // SYSTEM_ANALYTICS
            </div>
            """, unsafe_allow_html=True)
            if st.button(
                "📊 Risk Analytics",
                width="stretch"
            ):
                st.session_state.enterprise_page = "analytics"
                st.rerun()

        with c6:
            st.markdown("""
            <div style="margin-bottom: 10px; font-family: 'JetBrains Mono', monospace; font-size: 12px; color: #63768f; text-align: center;">
                MODULE 06 // ACTIVE_SHIELD
            </div>
            """, unsafe_allow_html=True)
            if st.button(
                "🔐 Enterprise Shield",
                width="stretch"
            ):
                st.session_state.enterprise_page = "shield"
                st.rerun()

    # ================= API MODULE =================

    elif page == "api":

        st.markdown("""
        <div style="margin-top: 10px; margin-bottom: 20px;">
            <span style="font-family: 'JetBrains Mono', monospace; font-size: 13px; color: #ff007f;">
                ENTERPRISE // THREAT CONTROL CONSOLE
            </span>
        </div>
        """, unsafe_allow_html=True)

        if st.button("← RETURN TO MAIN CONSOLE"):
            st.session_state.enterprise_page = "main"
            st.rerun()

        st.markdown("""
        <div style="margin-top: 20px; margin-bottom: 25px;">
            <h2 style="font-family: 'Orbitron', sans-serif; font-size: 26px; color: #ffffff; margin: 0;">
                📡 Fraud Detection API Simulator
            </h2>
            <span style="font-family: 'JetBrains Mono', monospace; font-size: 12px; color: #8be8ff;">
                STATUS: READY // ENDPOINT ACTIVE
            </span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="glass">', unsafe_allow_html=True)

        api_key = st.text_input(
            "API Access Key",
            value="SENTRAX-API-2026-XYZ"
        )

        amount = st.number_input(
            "Transaction Value (₹)",
            min_value=0,
            value=25000
        )

        location = st.selectbox(
            "Transaction Origin Location",
            [
                "India",
                "Unknown",
                "USA",
                "UK"
            ]
        )

        device = st.selectbox(
            "Accessing Device Status",
            [
                "Known Device",
                "New Device"
            ]
        )

        st.write("")

        if st.button("Analyze Transaction Telemetry"):

            fraud = _call_backend_fraud(amount, location, device, api_key)

            if fraud is None:
                st.markdown("""
                <div style="background:rgba(255,59,48,0.07);border:1px solid rgba(255,59,48,0.30);
                            border-left:4px solid #ff3b30;border-radius:14px;padding:18px 22px;
                            margin:14px 0;font-family:'JetBrains Mono',monospace;font-size:14px;
                            color:#ff8e8e;">
                    &#x26A0;&#xFE0F;&nbsp;&nbsp;<b>Backend service unavailable.</b><br>
                    <span style="font-size:12px;color:#63768f;">
                        Please try again later.
                    </span>
                </div>
                """, unsafe_allow_html=True)

            else:
                score          = fraud["score"]
                status         = fraud["status"]
                recommendation = fraud["recommendation"]
                reasons        = fraud["reasons"]

                rec_color = "#ff3b30" if score >= 70 else "#00ff87"
                badge_bg  = "rgba(255, 59, 48, 0.08)" if score >= 70 else "rgba(0, 255, 135, 0.05)"

                st.markdown(f"""
                <div class="result-safe" style="border-left: 5px solid {rec_color}; background-color: rgba(6, 18, 36, 0.45); margin-top: 25px; margin-bottom: 25px;">
                    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px;">
                        <h3 style="margin: 0; font-family: 'Orbitron', sans-serif; color: {rec_color}; font-size: 16px;">
                            &#x1F4DF; RADAR RESPONSE STATUS
                        </h3>
                        <span style="font-family: 'JetBrains Mono', monospace; font-size: 10px; font-weight: 600; padding: 2px 8px; background-color: {badge_bg}; border: 1px solid {rec_color}; color: {rec_color}; border-radius: 4px;">
                            {status}
                        </span>
                    </div>
                    <p style="font-family: 'JetBrains Mono', monospace; font-size: 13px; margin: 0; color: #d9f7ff;">
                        TELEMETRY CODE: <b>{score}/100</b> | RECOMMENDED ACTION: <b>{recommendation}</b>
                    </p>
                </div>
                """, unsafe_allow_html=True)

                bar_color = "#ff3b30" if score >= 70 else "#ffd60a" if score >= 50 else "#00ff87"
                st.markdown(f"""
                <div style="width: 100%; background-color: rgba(255, 255, 255, 0.05); border-radius: 10px; height: 12px; border: 1px solid rgba(255, 255, 255, 0.1); overflow: hidden; margin-top: 15px; margin-bottom: 25px; box-shadow: inset 0 2px 4px rgba(0,0,0,0.5);">
                    <div style="width: {score}%; background: linear-gradient(90deg, #00f0ff, {bar_color}); height: 100%; box-shadow: 0 0 10px {bar_color};"></div>
                </div>
                """, unsafe_allow_html=True)

                c1, c2, c3 = st.columns(3)

                c1.markdown(f"""
                <div class="telemetry-card" style="border-left: 4px solid #00f0ff;">
                    <div style="display: flex; justify-content: space-between; align-items: center; color: #8be8ff; font-family: 'JetBrains Mono', monospace; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px;">
                        <span>Risk Score Index</span><span>&#x1F4CA;</span>
                    </div>
                    <div style="font-size: 24px; font-family: 'Orbitron', sans-serif; font-weight: 700; color: #ffffff; margin-top: 6px;">{score}/100</div>
                </div>
                """, unsafe_allow_html=True)

                c2.markdown(f"""
                <div class="telemetry-card" style="border-left: 4px solid #ff007f;">
                    <div style="display: flex; justify-content: space-between; align-items: center; color: #8be8ff; font-family: 'JetBrains Mono', monospace; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px;">
                        <span>Security Status</span><span>&#x1F6E1;&#xFE0F;</span>
                    </div>
                    <div style="font-size: 24px; font-family: 'Orbitron', sans-serif; font-weight: 700; color: #ffffff; margin-top: 6px;">{status}</div>
                </div>
                """, unsafe_allow_html=True)

                c3.markdown(f"""
                <div class="telemetry-card" style="border-left: 4px solid #00ff87;">
                    <div style="display: flex; justify-content: space-between; align-items: center; color: #8be8ff; font-family: 'JetBrains Mono', monospace; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px;">
                        <span>Recommendation</span><span>&#x1F4DF;</span>
                    </div>
                    <div style="font-size: 24px; font-family: 'Orbitron', sans-serif; font-weight: 700; color: #ffffff; margin-top: 6px;">{recommendation}</div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("""
                <div style="margin-top: 30px; margin-bottom: 15px;">
                    <span style="font-family: 'Orbitron', sans-serif; font-size: 13px; color: #8be8ff; letter-spacing: 2px; text-transform: uppercase;">
                        &#x1F50D; Threat Indicator Log
                    </span>
                    <hr style="border: 0; border-top: 1px solid rgba(0, 240, 255, 0.15); margin-top: 8px; margin-bottom: 15px;">
                </div>
                """, unsafe_allow_html=True)

                if reasons:
                    for r in reasons:
                        st.markdown(
                            f'<div class="reason-chip">&#x26A0;&#xFE0F; {r}</div>',
                            unsafe_allow_html=True
                        )
                else:
                    st.markdown(
                        '<div class="reason-chip" style="border-left: 3px solid #00ff87;">&#x1F6E1;&#xFE0F; No transaction heuristics triggered. Safe parameters.</div>',
                        unsafe_allow_html=True
                    )

                st.markdown("""
                <div style="margin-top: 30px; margin-bottom: 15px;">
                    <span style="font-family: 'Orbitron', sans-serif; font-size: 13px; color: #8be8ff; letter-spacing: 2px; text-transform: uppercase;">
                        &#x1F4DF; Raw JSON Telemetry Response
                    </span>
                    <hr style="border: 0; border-top: 1px solid rgba(0, 240, 255, 0.15); margin-top: 8px; margin-bottom: 15px;">
                </div>
                """, unsafe_allow_html=True)

                st.json({
                    "api_key":        api_key,
                    "amount":         amount,
                    "location":       location,
                    "device":         device,
                    "risk_score":     score,
                    "status":         status,
                    "recommendation": recommendation,
                })

        st.markdown('</div>', unsafe_allow_html=True)



    # ================= URL MODULE =================

    elif page == "url":

        st.markdown("""
        <div style="margin-top: 10px; margin-bottom: 20px;">
            <span style="font-family: 'JetBrains Mono', monospace; font-size: 13px; color: #ff007f;">
                ENTERPRISE // THREAT CONTROL CONSOLE
            </span>
        </div>
        """, unsafe_allow_html=True)

        if st.button("← RETURN TO MAIN CONSOLE"):
            st.session_state.enterprise_page = "main"
            st.rerun()

        st.markdown("""
        <div style="margin-top: 20px; margin-bottom: 25px;">
            <h2 style="font-family: 'Orbitron', sans-serif; font-size: 26px; color: #ffffff; margin: 0;">
                🌐 Enterprise URL Intelligence
            </h2>
            <span style="font-family: 'JetBrains Mono', monospace; font-size: 12px; color: #8be8ff;">
                STATUS: HEURISTICS ACTIVE // SCANNING SYSTEM LOADED
            </span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="glass">', unsafe_allow_html=True)

        url = st.text_input(
            "Analyze Enterprise URL Target",
            placeholder="https://secure-login.portal-access.com"
        )

        st.write("")

        if st.button("Run Cyber Threat Scan"):

            result = predict_url(url)

            badge_color = "#ff3b30" if result["label"] == "Fraud / Phishing" else "#00ff87"
            badge_bg = "rgba(255, 59, 48, 0.08)" if result["label"] == "Fraud / Phishing" else "rgba(0, 255, 135, 0.05)"

            st.markdown(f"""
            <div class="result-safe" style="border-left: 5px solid {badge_color}; background-color: rgba(6, 18, 36, 0.45); margin-top: 25px; margin-bottom: 25px;">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px;">
                    <h3 style="margin: 0; font-family: 'Orbitron', sans-serif; color: {badge_color}; font-size: 16px;">
                        🛡️ SCAN HEURISTICS OUTPUT
                    </h3>
                    <span style="font-family: 'JetBrains Mono', monospace; font-size: 10px; font-weight: 600; padding: 2px 8px; background-color: {badge_bg}; border: 1px solid {badge_color}; color: {badge_color}; border-radius: 4px;">
                        {result["label"].upper()}
                    </span>
                </div>
                <p style="font-family: 'JetBrains Mono', monospace; font-size: 13px; margin: 0; color: #d9f7ff;">
                    URL TARGET: <b>{url}</b><br>
                    THREAT INDEX: <b>{result["score"]}/100</b>
                </p>
            </div>
            """, unsafe_allow_html=True)

            bar_color = "#ff3b30" if result["score"] >= 70 else "#ffd60a" if result["score"] >= 50 else "#00ff87"
            st.markdown(f"""
            <div style="width: 100%; background-color: rgba(255, 255, 255, 0.05); border-radius: 10px; height: 12px; border: 1px solid rgba(255, 255, 255, 0.1); overflow: hidden; margin-top: 15px; margin-bottom: 25px; box-shadow: inset 0 2px 4px rgba(0,0,0,0.5);">
                <div style="width: {result["score"]}%; background: linear-gradient(90deg, #00f0ff, {bar_color}); height: 100%; box-shadow: 0 0 10px {bar_color};"></div>
            </div>
            """, unsafe_allow_html=True)

            c1, c2, c3 = st.columns(3)

            c1.markdown(f"""
            <div class="telemetry-card" style="border-left: 4px solid #00f0ff;">
                <div style="display: flex; justify-content: space-between; align-items: center; color: #8be8ff; font-family: 'JetBrains Mono', monospace; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px;">
                    <span>Threat Index Value</span>
                    <span>📊</span>
                </div>
                <div style="font-size: 24px; font-family: 'Orbitron', sans-serif; font-weight: 700; color: #ffffff; margin-top: 6px;">{result['score']}/100</div>
            </div>
            """, unsafe_allow_html=True)

            c2.markdown(f"""
            <div class="telemetry-card" style="border-left: 4px solid #ff007f;">
                <div style="display: flex; justify-content: space-between; align-items: center; color: #8be8ff; font-family: 'JetBrains Mono', monospace; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px;">
                    <span>Classification</span>
                    <span>🛡️</span>
                </div>
                <div style="font-size: 24px; font-family: 'Orbitron', sans-serif; font-weight: 700; color: #ffffff; margin-top: 6px;">{result["label"]}</div>
            </div>
            """, unsafe_allow_html=True)

            c3.markdown(f"""
            <div class="telemetry-card" style="border-left: 4px solid #00ff87;">
                <div style="display: flex; justify-content: space-between; align-items: center; color: #8be8ff; font-family: 'JetBrains Mono', monospace; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px;">
                    <span>Triggers Flagged</span>
                    <span>🔎</span>
                </div>
                <div style="font-size: 24px; font-family: 'Orbitron', sans-serif; font-weight: 700; color: #ffffff; margin-top: 6px;">{len(result["reasons"])}</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("""
            <div style="margin-top: 30px; margin-bottom: 15px;">
                <span style="font-family: 'Orbitron', sans-serif; font-size: 13px; color: #8be8ff; letter-spacing: 2px; text-transform: uppercase;">
                    📡 Raw Threat Parameters
                </span>
                <hr style="border: 0; border-top: 1px solid rgba(0, 240, 255, 0.15); margin-top: 8px; margin-bottom: 15px;">
            </div>
            """, unsafe_allow_html=True)

            st.json(result["technical"])

            st.markdown("""
            <div style="margin-top: 30px; margin-bottom: 15px;">
                <span style="font-family: 'Orbitron', sans-serif; font-size: 13px; color: #8be8ff; letter-spacing: 2px; text-transform: uppercase;">
                    🔍 Threat Indicator Details
                </span>
                <hr style="border: 0; border-top: 1px solid rgba(0, 240, 255, 0.15); margin-top: 8px; margin-bottom: 15px;">
            </div>
            """, unsafe_allow_html=True)

            if result["reasons"]:
                for r in result["reasons"]:
                    st.markdown(
                        f'<div class="reason-chip">⚠️ {r}</div>',
                        unsafe_allow_html=True
                    )
            else:
                st.markdown(
                    '<div class="reason-chip" style="border-left: 3px solid #00ff87;">🛡️ No heuristic patterns triggered. Target classified clear.</div>',
                    unsafe_allow_html=True
                )

        st.markdown('</div>', unsafe_allow_html=True)

    # ================= ANALYTICS MODULE =================

    elif page == "analytics":

        st.markdown("""
        <div style="margin-top: 10px; margin-bottom: 20px;">
            <span style="font-family: 'JetBrains Mono', monospace; font-size: 13px; color: #ff007f;">
                ENTERPRISE // THREAT CONTROL CONSOLE
            </span>
        </div>
        """, unsafe_allow_html=True)

        if st.button("← RETURN TO MAIN CONSOLE"):
            st.session_state.enterprise_page = "main"
            st.rerun()

        st.markdown("""
        <div style="margin-top: 20px; margin-bottom: 25px;">
            <h2 style="font-family: 'Orbitron', sans-serif; font-size: 26px; color: #ffffff; margin: 0;">
                📊 Enterprise Threat Metrics & Analytics
            </h2>
            <span style="font-family: 'JetBrains Mono', monospace; font-size: 12px; color: #8be8ff;">
                STATUS: DATA INTEGRATION SYNCHRONIZED
            </span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="glass">', unsafe_allow_html=True)

        rows = get_recent_scans()
        total = len(rows)
        fraud = sum(1 for r in rows if r[1] == "Fraud / Phishing")
        safe = sum(1 for r in rows if r[1] == "Safe")

        fraud_rate = (
            round((fraud / total) * 100, 2)
            if total > 0
            else 0
        )

        c1, c2, c3, c4 = st.columns(4)

        c1.markdown(f"""
        <div class="telemetry-card" style="border-left: 4px solid #00f0ff;">
            <div style="display: flex; justify-content: space-between; align-items: center; color: #8be8ff; font-family: 'JetBrains Mono', monospace; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px;">
                <span>Logs Analyzed</span>
                <span>📟</span>
            </div>
            <div style="font-size: 24px; font-family: 'Orbitron', sans-serif; font-weight: 700; color: #ffffff; margin-top: 6px;">{total}</div>
        </div>
        """, unsafe_allow_html=True)

        c2.markdown(f"""
        <div class="telemetry-card" style="border-left: 4px solid #ff3b30;">
            <div style="display: flex; justify-content: space-between; align-items: center; color: #8be8ff; font-family: 'JetBrains Mono', monospace; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px;">
                <span>Captured threats</span>
                <span>🚨</span>
            </div>
            <div style="font-size: 24px; font-family: 'Orbitron', sans-serif; font-weight: 700; color: #ffffff; margin-top: 6px;">{fraud}</div>
        </div>
        """, unsafe_allow_html=True)

        c3.markdown(f"""
        <div class="telemetry-card" style="border-left: 4px solid #00ff87;">
            <div style="display: flex; justify-content: space-between; align-items: center; color: #8be8ff; font-family: 'JetBrains Mono', monospace; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px;">
                <span>Safe Targets</span>
                <span>🛡️</span>
            </div>
            <div style="font-size: 24px; font-family: 'Orbitron', sans-serif; font-weight: 700; color: #ffffff; margin-top: 6px;">{safe}</div>
        </div>
        """, unsafe_allow_html=True)

        c4.markdown(f"""
        <div class="telemetry-card" style="border-left: 4px solid #ffd60a;">
            <div style="display: flex; justify-content: space-between; align-items: center; color: #8be8ff; font-family: 'JetBrains Mono', monospace; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px;">
                <span>Incident Ratio</span>
                <span>📈</span>
            </div>
            <div style="font-size: 24px; font-family: 'Orbitron', sans-serif; font-weight: 700; color: #ffffff; margin-top: 6px;">{fraud_rate}%</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="margin-top: 30px; margin-bottom: 15px;">
            <span style="font-family: 'Orbitron', sans-serif; font-size: 14px; color: #8be8ff; letter-spacing: 2px; text-transform: uppercase;">
                🚨 Enterprise Incident Alert Logs
            </span>
            <hr style="border: 0; border-top: 1px solid rgba(0, 240, 255, 0.15); margin-top: 8px; margin-bottom: 20px;">
        </div>
        """, unsafe_allow_html=True)

        if rows:
            for url, label, score, time_val in rows[:5]:
                badge_color = "#ff3b30" if label == "Fraud / Phishing" else "#00ff87"
                badge_bg = "rgba(255, 59, 48, 0.08)" if label == "Fraud / Phishing" else "rgba(0, 255, 135, 0.05)"

                st.markdown(f"""
                <div class="reason-chip" style="border-left: 4px solid {badge_color}; background-color: rgba(6, 18, 36, 0.45); padding: 12px; margin-bottom: 10px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; gap: 15px;">
                        <span style="font-family: 'JetBrains Mono', monospace; font-size: 13px; color: #ffffff; text-overflow: ellipsis; overflow: hidden; white-space: nowrap;">
                            {url}
                        </span>
                        <span style="font-family: 'JetBrains Mono', monospace; font-size: 10px; font-weight: 600; padding: 1px 6px; background-color: {badge_bg}; border: 1px solid {badge_color}; color: {badge_color}; border-radius: 4px;">
                            {label.upper()}
                        </span>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center; font-size: 11px; color: #8be8ff; font-family: 'JetBrains Mono', monospace; margin-top: 5px;">
                        <span>Risk score: {score}/100</span>
                        <span style="color: #63768f;">Log: {time_val}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown(
                '<div class="reason-chip" style="border-left: 3px solid #ffd60a;">📡 Database monitor online. No transaction alert records captured yet.</div>',
                unsafe_allow_html=True
            )

        st.markdown('</div>', unsafe_allow_html=True)

    # ================= SCAM MODULE =================

    elif page == "scam":

        st.markdown("""
        <div style="margin-top: 10px; margin-bottom: 20px;">
            <span style="font-family: 'JetBrains Mono', monospace; font-size: 13px; color: #ff007f;">
                ENTERPRISE // THREAT CONTROL CONSOLE
            </span>
        </div>
        """, unsafe_allow_html=True)

        if st.button("← RETURN TO MAIN CONSOLE"):
            st.session_state.enterprise_page = "main"
            st.rerun()

        st.markdown("""
        <div style="margin-top: 20px; margin-bottom: 25px;">
            <h2 style="font-family: 'Orbitron', sans-serif; font-size: 26px; color: #ffffff; margin: 0;">
                ⚡ Enterprise Scam & Content Filtering
            </h2>
            <span style="font-family: 'JetBrains Mono', monospace; font-size: 12px; color: #8be8ff;">
                STATUS: NLP LOGIC RUNNING // INBOUND PARSER STANDBY
            </span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="glass">', unsafe_allow_html=True)

        message = st.text_area(
            "Analyze Enterprise Communication Vector",
            height=140,
            placeholder="Paste suspicious text or SMS data to run indicators parse..."
        )

        st.write("")

        if st.button("Run Content Analysis"):

            result = predict_sms(message)

            badge_color = "#ff3b30" if result["label"] == "Scam Message" else "#00ff87"
            badge_bg = "rgba(255, 59, 48, 0.08)" if result["label"] == "Scam Message" else "rgba(0, 255, 135, 0.05)"

            st.markdown(f"""
            <div class="result-safe" style="border-left: 5px solid {badge_color}; background-color: rgba(6, 18, 36, 0.45); margin-top: 25px; margin-bottom: 25px;">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px;">
                    <h3 style="margin: 0; font-family: 'Orbitron', sans-serif; color: {badge_color}; font-size: 16px;">
                        🔬 CONTENT SCANNED OUTCOME
                    </h3>
                    <span style="font-family: 'JetBrains Mono', monospace; font-size: 10px; font-weight: 600; padding: 2px 8px; background-color: {badge_bg}; border: 1px solid {badge_color}; color: {badge_color}; border-radius: 4px;">
                        {result["label"].upper()}
                    </span>
                </div>
                <p style="font-family: 'JetBrains Mono', monospace; font-size: 13px; margin: 0; color: #d9f7ff;">
                    THREAT INDEX RATING: <b>{result["score"]}/100</b>
                </p>
            </div>
            """, unsafe_allow_html=True)

            bar_color = "#ff3b30" if result["score"] >= 70 else "#ffd60a" if result["score"] >= 50 else "#00ff87"
            st.markdown(f"""
            <div style="width: 100%; background-color: rgba(255, 255, 255, 0.05); border-radius: 10px; height: 12px; border: 1px solid rgba(255, 255, 255, 0.1); overflow: hidden; margin-top: 15px; margin-bottom: 25px; box-shadow: inset 0 2px 4px rgba(0,0,0,0.5);">
                <div style="width: {result["score"]}%; background: linear-gradient(90deg, #00f0ff, {bar_color}); height: 100%; box-shadow: 0 0 10px {bar_color};"></div>
            </div>
            """, unsafe_allow_html=True)

            c1, c2, c3 = st.columns(3)

            c1.markdown(f"""
            <div class="telemetry-card" style="border-left: 4px solid #ff007f;">
                <div style="display: flex; justify-content: space-between; align-items: center; color: #8be8ff; font-family: 'JetBrains Mono', monospace; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px;">
                    <span>Scam Score Rating</span>
                    <span>📊</span>
                </div>
                <div style="font-size: 24px; font-family: 'Orbitron', sans-serif; font-weight: 700; color: #ffffff; margin-top: 6px;">{result['score']}/100</div>
            </div>
            """, unsafe_allow_html=True)

            c2.markdown(f"""
            <div class="telemetry-card" style="border-left: 4px solid #ffd60a;">
                <div style="display: flex; justify-content: space-between; align-items: center; color: #8be8ff; font-family: 'JetBrains Mono', monospace; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px;">
                    <span>Classification</span>
                    <span>🔎</span>
                </div>
                <div style="font-size: 24px; font-family: 'Orbitron', sans-serif; font-weight: 700; color: #ffffff; margin-top: 6px;">{result["label"]}</div>
            </div>
            """, unsafe_allow_html=True)

            c3.markdown(f"""
            <div class="telemetry-card" style="border-left: 4px solid #00f0ff;">
                <div style="display: flex; justify-content: space-between; align-items: center; color: #8be8ff; font-family: 'JetBrains Mono', monospace; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px;">
                    <span>Flags Detected</span>
                    <span>⚠️</span>
                </div>
                <div style="font-size: 24px; font-family: 'Orbitron', sans-serif; font-weight: 700; color: #ffffff; margin-top: 6px;">{len(result["reasons"])}</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("""
            <div style="margin-top: 30px; margin-bottom: 15px;">
                <span style="font-family: 'Orbitron', sans-serif; font-size: 13px; color: #8be8ff; letter-spacing: 2px; text-transform: uppercase;">
                    🔍 Identified Scam Indicators
                </span>
                <hr style="border: 0; border-top: 1px solid rgba(0, 240, 255, 0.15); margin-top: 8px; margin-bottom: 15px;">
            </div>
            """, unsafe_allow_html=True)

            if result["reasons"]:
                for r in result["reasons"]:
                    st.markdown(
                        f'<div class="reason-chip">⚠️ Highlighted keyword: "{r}"</div>',
                        unsafe_allow_html=True
                    )
            else:
                st.markdown(
                    '<div class="reason-chip" style="border-left: 3px solid #00ff87;">🛡️ No scam-associated keyword patterns identified.</div>',
                    unsafe_allow_html=True
                )

        st.markdown('</div>', unsafe_allow_html=True)

    # ================= EMPLOYEE MODULE =================

    elif page == "employee":

        st.markdown("""
        <div style="margin-top: 10px; margin-bottom: 20px;">
            <span style="font-family: 'JetBrains Mono', monospace; font-size: 13px; color: #ff007f;">
                ENTERPRISE // THREAT CONTROL CONSOLE
            </span>
        </div>
        """, unsafe_allow_html=True)

        if st.button("← RETURN TO MAIN CONSOLE"):
            st.session_state.enterprise_page = "main"
            st.rerun()

        st.markdown("""
        <div style="margin-top: 20px; margin-bottom: 25px;">
            <h2 style="font-family: 'Orbitron', sans-serif; font-size: 26px; color: #ffffff; margin: 0;">
                🛡️ Employee Security Monitoring
            </h2>
            <span style="font-family: 'JetBrains Mono', monospace; font-size: 12px; color: #8be8ff;">
                STATUS: AUDIT LOG SYSTEM OPERATIONAL
            </span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="glass">', unsafe_allow_html=True)

        login_time = st.selectbox(
            "Access Login Timeframe",
            [
                "Normal Hours",
                "Late Night"
            ]
        )

        location = st.selectbox(
            "Access Request Location",
            [
                "Office",
                "Unknown",
                "Remote"
            ]
        )

        device = st.selectbox(
            "Request Device Profile",
            [
                "Known Device",
                "New Device"
            ]
        )

        st.write("")

        if st.button("Analyze Account Security activity"):

            score = 10
            reasons = []

            if login_time == "Late Night":
                score += 25
                reasons.append(
                    "Late night transaction / database access window"
                )

            if location == "Unknown":
                score += 30
                reasons.append(
                    "Unidentified IP routing path"
                )

            if device == "New Device":
                score += 25
                reasons.append(
                    "Unverified hardware configuration"
                )

            score = min(score, 99)

            status = (
                "Suspicious Activity"
                if score >= 70
                else "Normal Activity"
            )

            recommendation = (
                "Review Employee Access"
                if score >= 70
                else "Continue Monitoring"
            )

            badge_color = "#ff3b30" if score >= 70 else "#00ff87"
            badge_bg = "rgba(255, 59, 48, 0.08)" if score >= 70 else "rgba(0, 255, 135, 0.05)"

            st.markdown(f"""
            <div class="result-safe" style="border-left: 5px solid {badge_color}; background-color: rgba(6, 18, 36, 0.45); margin-top: 25px; margin-bottom: 25px;">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px;">
                    <h3 style="margin: 0; font-family: 'Orbitron', sans-serif; color: {badge_color}; font-size: 16px;">
                        🚨 SECURITY AUDIT LOG
                    </h3>
                    <span style="font-family: 'JetBrains Mono', monospace; font-size: 10px; font-weight: 600; padding: 2px 8px; background-color: {badge_bg}; border: 1px solid {badge_color}; color: {badge_color}; border-radius: 4px;">
                        {status.upper()}
                    </span>
                </div>
                <p style="font-family: 'JetBrains Mono', monospace; font-size: 13px; margin: 0; color: #d9f7ff;">
                    DEV RISK RATING: <b>{score}/100</b> | AUDIT ACTION: <b>{recommendation}</b>
                </p>
            </div>
            """, unsafe_allow_html=True)

            bar_color = "#ff3b30" if score >= 70 else "#ffd60a" if score >= 50 else "#00ff87"
            st.markdown(f"""
            <div style="width: 100%; background-color: rgba(255, 255, 255, 0.05); border-radius: 10px; height: 12px; border: 1px solid rgba(255, 255, 255, 0.1); overflow: hidden; margin-top: 15px; margin-bottom: 25px; box-shadow: inset 0 2px 4px rgba(0,0,0,0.5);">
                <div style="width: {score}%; background: linear-gradient(90deg, #00f0ff, {bar_color}); height: 100%; box-shadow: 0 0 10px {bar_color};"></div>
            </div>
            """, unsafe_allow_html=True)

            c1, c2, c3 = st.columns(3)

            c1.markdown(f"""
            <div class="telemetry-card" style="border-left: 4px solid #ff3b30;">
                <div style="display: flex; justify-content: space-between; align-items: center; color: #8be8ff; font-family: 'JetBrains Mono', monospace; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px;">
                    <span>Anomalous Risk Factor</span>
                    <span>🚨</span>
                </div>
                <div style="font-size: 24px; font-family: 'Orbitron', sans-serif; font-weight: 700; color: #ffffff; margin-top: 6px;">{score}/100</div>
            </div>
            """, unsafe_allow_html=True)

            c2.markdown(f"""
            <div class="telemetry-card" style="border-left: 4px solid #ffd60a;">
                <div style="display: flex; justify-content: space-between; align-items: center; color: #8be8ff; font-family: 'JetBrains Mono', monospace; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px;">
                    <span>Audited Status</span>
                    <span>🛡️</span>
                </div>
                <div style="font-size: 24px; font-family: 'Orbitron', sans-serif; font-weight: 700; color: #ffffff; margin-top: 6px;">{status}</div>
            </div>
            """, unsafe_allow_html=True)

            c3.markdown(f"""
            <div class="telemetry-card" style="border-left: 4px solid #00f0ff;">
                <div style="display: flex; justify-content: space-between; align-items: center; color: #8be8ff; font-family: 'JetBrains Mono', monospace; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px;">
                    <span>Action Audit</span>
                    <span>⚡</span>
                </div>
                <div style="font-size: 24px; font-family: 'Orbitron', sans-serif; font-weight: 700; color: #ffffff; margin-top: 6px;">{recommendation}</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("""
            <div style="margin-top: 30px; margin-bottom: 15px;">
                <span style="font-family: 'Orbitron', sans-serif; font-size: 13px; color: #8be8ff; letter-spacing: 2px; text-transform: uppercase;">
                    🔍 Identified Security Anomaly Indicators
                </span>
                <hr style="border: 0; border-top: 1px solid rgba(0, 240, 255, 0.15); margin-top: 8px; margin-bottom: 15px;">
            </div>
            """, unsafe_allow_html=True)

            if reasons:
                for r in reasons:
                    st.markdown(
                        f'<div class="reason-chip">⚠️ {r}</div>',
                        unsafe_allow_html=True
                    )
            else:
                st.markdown(
                    '<div class="reason-chip" style="border-left: 3px solid #00ff87;">🛡️ Access telemetry complies with standard policy guidelines.</div>',
                    unsafe_allow_html=True
                )

        st.markdown('</div>', unsafe_allow_html=True)

    # ================= SHIELD MODULE =================

    elif page == "shield":

        st.markdown("""
        <div style="margin-top: 10px; margin-bottom: 20px;">
            <span style="font-family: 'JetBrains Mono', monospace; font-size: 13px; color: #ff007f;">
                ENTERPRISE // THREAT CONTROL CONSOLE
            </span>
        </div>
        """, unsafe_allow_html=True)

        if st.button("← RETURN TO MAIN CONSOLE"):
            st.session_state.enterprise_page = "main"
            st.rerun()

        st.markdown("""
        <div style="margin-top: 20px; margin-bottom: 25px;">
            <h2 style="font-family: 'Orbitron', sans-serif; font-size: 26px; color: #ffffff; margin: 0;">
                🔐 Active Enterprise Security Shield Audit
            </h2>
            <span style="font-family: 'JetBrains Mono', monospace; font-size: 12px; color: #8be8ff;">
                STATUS: COMPLIANCE ENGINES READY
            </span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="glass">', unsafe_allow_html=True)

        firewall = st.selectbox(
            "Firewall Shield Integration",
            [
                "Enabled",
                "Disabled"
            ]
        )

        mfa = st.selectbox(
            "Multi-Factor Auth Policy",
            [
                "Enabled",
                "Disabled"
            ]
        )

        endpoint = st.selectbox(
            "Endpoint Telemetry Agent",
            [
                "Enabled",
                "Disabled"
            ]
        )

        st.write("")

        if st.button("Run Security Infrastructure Audit"):

            score = 100
            reasons = []

            if firewall == "Disabled":
                score -= 35
                reasons.append(
                    "Network Perimeter Firewall is deactivated"
                )

            if mfa == "Disabled":
                score -= 30
                reasons.append(
                    "MFA controls not enforced on active logins"
                )

            if endpoint == "Disabled":
                score -= 25
                reasons.append(
                    "Endpoint anti-virus telemetry agent offline"
                )

            score = max(score, 0)

            status = (
                "HIGH SECURITY"
                if score >= 75
                else "AT RISK"
            )

            recommendation = (
                "Maintain security posture"
                if score >= 75
                else "Enable missing protections immediately"
            )

            badge_color = "#00ff87" if score >= 75 else "#ff3b30"
            badge_bg = "rgba(0, 255, 135, 0.05)" if score >= 75 else "rgba(255, 59, 48, 0.08)"

            st.markdown(f"""
            <div class="result-safe" style="border-left: 5px solid {badge_color}; background-color: rgba(6, 18, 36, 0.45); margin-top: 25px; margin-bottom: 25px;">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px;">
                    <h3 style="margin: 0; font-family: 'Orbitron', sans-serif; color: {badge_color}; font-size: 16px;">
                        🔐 PLATFORM COMPLIANCE METRICS
                    </h3>
                    <span style="font-family: 'JetBrains Mono', monospace; font-size: 10px; font-weight: 600; padding: 2px 8px; background-color: {badge_bg}; border: 1px solid {badge_color}; color: {badge_color}; border-radius: 4px;">
                        {status}
                    </span>
                </div>
                <p style="font-family: 'JetBrains Mono', monospace; font-size: 13px; margin: 0; color: #d9f7ff;">
                    COMPLIANCE SCORE: <b>{score}/100</b> | REMEDY RECOMMENDATION: <b>{recommendation}</b>
                </p>
            </div>
            """, unsafe_allow_html=True)

            bar_color = "#00ff87" if score >= 75 else "#ff3b30"
            st.markdown(f"""
            <div style="width: 100%; background-color: rgba(255, 255, 255, 0.05); border-radius: 10px; height: 12px; border: 1px solid rgba(255, 255, 255, 0.1); overflow: hidden; margin-top: 15px; margin-bottom: 25px; box-shadow: inset 0 2px 4px rgba(0,0,0,0.5);">
                <div style="width: {score}%; background: linear-gradient(90deg, #00f0ff, {bar_color}); height: 100%; box-shadow: 0 0 10px {bar_color};"></div>
            </div>
            """, unsafe_allow_html=True)

            c1, c2, c3 = st.columns(3)

            c1.markdown(f"""
            <div class="telemetry-card" style="border-left: 4px solid #00ff87;">
                <div style="display: flex; justify-content: space-between; align-items: center; color: #8be8ff; font-family: 'JetBrains Mono', monospace; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px;">
                    <span>Compliance Rating</span>
                    <span>🔐</span>
                </div>
                <div style="font-size: 24px; font-family: 'Orbitron', sans-serif; font-weight: 700; color: #ffffff; margin-top: 6px;">{score}/100</div>
            </div>
            """, unsafe_allow_html=True)

            c2.markdown(f"""
            <div class="telemetry-card" style="border-left: 4px solid #ff007f;">
                <div style="display: flex; justify-content: space-between; align-items: center; color: #8be8ff; font-family: 'JetBrains Mono', monospace; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px;">
                    <span>Posture Status Code</span>
                    <span>🛡️</span>
                </div>
                <div style="font-size: 24px; font-family: 'Orbitron', sans-serif; font-weight: 700; color: #ffffff; margin-top: 6px;">{status}</div>
            </div>
            """, unsafe_allow_html=True)

            c3.markdown(f"""
            <div class="telemetry-card" style="border-left: 4px solid #00f0ff;">
                <div style="display: flex; justify-content: space-between; align-items: center; color: #8be8ff; font-family: 'JetBrains Mono', monospace; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px;">
                    <span>Remedy Action</span>
                    <span>⚙️</span>
                </div>
                <div style="font-size: 24px; font-family: 'Orbitron', sans-serif; font-weight: 700; color: #ffffff; margin-top: 6px;">{recommendation}</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("""
            <div style="margin-top: 30px; margin-bottom: 15px;">
                <span style="font-family: 'Orbitron', sans-serif; font-size: 13px; color: #8be8ff; letter-spacing: 2px; text-transform: uppercase;">
                    🛡️ Identified Audit Findings
                </span>
                <hr style="border: 0; border-top: 1px solid rgba(0, 240, 255, 0.15); margin-top: 8px; margin-bottom: 15px;">
            </div>
            """, unsafe_allow_html=True)

            if reasons:
                for r in reasons:
                    st.markdown(
                        f'<div class="reason-chip">⚠️ {r}</div>',
                        unsafe_allow_html=True
                    )
            else:
                st.markdown(
                    '<div class="reason-chip" style="border-left: 3px solid #00ff87;">🛡️ Compliance target met. All active protections enabled.</div>',
                    unsafe_allow_html=True
                )

        st.markdown('</div>', unsafe_allow_html=True)