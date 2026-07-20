import streamlit as st
import time
import requests as http_requests
from src.utils.report import generate_pdf
from src.utils.database import save_scan
from src.utils.explainer import explain_url
from src.utils.auth_state import get_auth_headers, BACKEND_URL as _BACKEND_URL


def _call_backend_scan(url: str):
    """
    POST to /api/url/scan and return the result dict,
    or None if the backend is unavailable.
    """
    try:
        resp = http_requests.post(
            f"{_BACKEND_URL}/api/url/scan",
            json={"url": url},
            headers=get_auth_headers(),
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        # Normalise to the shape expected by the existing UI
        return {
            "label":   data.get("label", "Safe"),
            "score":   data.get("score", 0),
            "reasons": data.get("reasons", []),
            "technical": data.get("technical", {
                "HTTPS": "?", "IP Based": "?",
                "Keyword Hits": 0, "Length": len(url),
                "SSL": "?", "Redirects": 0,
            }),
        }
    except (http_requests.ConnectionError, http_requests.Timeout):
        return None
    except Exception:
        return None


def render_scanner():
    # Local cyber styling injections
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

    st.markdown('<div class="brand">SentraX Scan</div>', unsafe_allow_html=True)
    st.markdown('<div class="tag">// ADVANCED FRAUD URL INTELLIGENCE</div>', unsafe_allow_html=True)

    st.markdown('<div class="glass">', unsafe_allow_html=True)

    url = st.text_input("Paste suspicious URL", placeholder="https://example.com/login")

    if st.button("Scan Threat"):

        # ── V4.3 Staged loading animation ─────────────────────────────
        stages = [
            "🔗  Analyzing URL structure...",
            "🤖  Running AI Detection Engine...",
            "⚠️  Classifying Threat Level...",
            "💾  Saving to Threat History...",
        ]
        stage_ph = st.empty()
        prog_ph  = st.empty()
        prog_bar = prog_ph.progress(0)
        for i, stage in enumerate(stages):
            stage_html = ""
            for j, s in enumerate(stages):
                if j < i:
                    cls = "v43-stage v43-stage-done"
                    icon = "✅"
                elif j == i:
                    cls = "v43-stage v43-stage-active"
                    icon = "⟳"
                else:
                    cls = "v43-stage v43-stage-pending"
                    icon = "○"
                stage_html += f'<div class="{cls}">{icon}&nbsp;&nbsp;{s}</div>'
            stage_ph.markdown(
                f'<div style="background:rgba(6,18,36,0.50);border:1px solid rgba(0,240,255,0.10);'
                f'border-radius:14px;padding:14px 18px;margin:10px 0;">{stage_html}</div>',
                unsafe_allow_html=True
            )
            prog_bar.progress(int((i + 1) / len(stages) * 100))
            time.sleep(0.4)

        stage_ph.empty()
        prog_ph.empty()

        # ── Call the FastAPI backend ───────────────────────────────────
        result = _call_backend_scan(url)

        if result is None:
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
            save_scan(url, result["label"], result["score"])

            if result["label"] == "Fraud / Phishing":
                st.markdown("""
                <div class="result-danger">
                    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
                        <h3 style="margin: 0; color: #ff3b30; font-family: 'Orbitron', sans-serif; font-size: 18px;">&#x1F6A8; FRAUD / PHISHING DETECTED</h3>
                        <span style="font-family: 'JetBrains Mono', monospace; font-size: 10px; font-weight: 600; padding: 3px 8px; background: rgba(255, 59, 48, 0.2); border: 1px solid #ff3b30; border-radius: 4px; color: #ff3b30; letter-spacing: 1px;">CRITICAL</span>
                    </div>
                    <p style="font-family: 'JetBrains Mono', monospace; font-size: 14px; margin: 0; color: #ff8e8e;">
                        Risk Assessment: <b>HIGH RISK</b>
                    </p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="result-safe">
                    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
                        <h3 style="margin: 0; color: #00ff87; font-family: 'Orbitron', sans-serif; font-size: 18px;">&#x2705; SAFE URL VERIFIED</h3>
                        <span style="font-family: 'JetBrains Mono', monospace; font-size: 10px; font-weight: 600; padding: 3px 8px; background: rgba(0, 255, 135, 0.2); border: 1px solid #00ff87; border-radius: 4px; color: #00ff87; letter-spacing: 1px;">VERIFIED</span>
                    </div>
                    <p style="font-family: 'JetBrains Mono', monospace; font-size: 14px; margin: 0; color: #a1ffcc;">
                        Risk Assessment: <b>NO IMMEDIATE THREAT</b>
                    </p>
                </div>
                """, unsafe_allow_html=True)

            # ── V4.3 Threat Score Gauge ────────────────────────────────
            score      = result["score"]
            bar_color  = "#ff3b30" if score >= 70 else "#ffd60a" if score >= 50 else "#00ff87"
            tier_label = "HIGH" if score >= 70 else "MODERATE" if score >= 50 else "LOW"
            tier_bg    = ("rgba(255,59,48,0.12)" if score >= 70
                          else "rgba(255,214,10,0.10)" if score >= 50
                          else "rgba(0,255,135,0.08)")
            filled     = "\u2588" * (score // 10)
            empty_b    = "\u2591" * (10 - score // 10)
            st.markdown(f"""
            <div class="v43-gauge-wrap">
                <div class="v43-gauge-label">Threat Score Gauge</div>
                <div class="v43-gauge-score" style="color:{bar_color};">{score} <span style="font-size:18px;color:#63768f;">/100</span></div>
                <div class="v43-gauge-bar-track">
                    <div class="v43-gauge-bar-fill"
                         style="width:{score}%;background:linear-gradient(90deg,#00f0ff,{bar_color});
                                box-shadow:0 0 10px {bar_color};"></div>
                </div>
                <div style="font-family:'JetBrains Mono',monospace;font-size:13px;color:{bar_color};
                            letter-spacing:2px;margin-bottom:10px;">{filled}{empty_b}</div>
                <span class="v43-gauge-tier"
                      style="color:{bar_color};background:{tier_bg};border:1px solid {bar_color}33;">
                    Threat Level: {tier_label}
                </span>
            </div>
            """, unsafe_allow_html=True)

            # ── V4.3 Success notification cards ───────────────────────
            st.markdown("""
            <div class="v43-notify v43-notify-success">&#x2705;&nbsp;&nbsp;Threat Analysis Completed &#x2014; via SentraX Backend API</div>
            <div class="v43-notify v43-notify-info">&#x1F4C4;&nbsp;&nbsp;Executive Report Available for Download</div>
            <div class="v43-notify v43-notify-warn">&#x1F5C2;&nbsp;&nbsp;Scan Result Saved to History</div>
            """, unsafe_allow_html=True)

            # ── AI Analysis Explainability Card ────────────────────────
            explain_url(result)

            tech = result["technical"]

            st.markdown("""
            <div style="margin-top: 25px; margin-bottom: 15px;">
                <span style="font-family: 'Orbitron', sans-serif; font-size: 14px; color: #8be8ff; letter-spacing: 2px; text-transform: uppercase;">
                    &#x1F310; Technical Security Metrics
                </span>
                <hr style="border: 0; border-top: 1px solid rgba(0, 240, 255, 0.15); margin-top: 8px; margin-bottom: 20px;">
            </div>
            """, unsafe_allow_html=True)

            c1, c2, c3 = st.columns(3)

            c1.markdown(f"""
            <div class="telemetry-card" style="border-left: 4px solid #00f0ff;">
                <div style="display: flex; justify-content: space-between; align-items: center; color: #8be8ff; font-family: 'JetBrains Mono', monospace; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px;">
                    <span>SSL Status</span><span>&#x1F512;</span>
                </div>
                <div style="font-size: 24px; font-family: 'Orbitron', sans-serif; font-weight: 700; color: #ffffff; margin-top: 6px;">{tech["SSL"]}</div>
            </div>
            """, unsafe_allow_html=True)

            c2.markdown(f"""
            <div class="telemetry-card" style="border-left: 4px solid #ff007f;">
                <div style="display: flex; justify-content: space-between; align-items: center; color: #8be8ff; font-family: 'JetBrains Mono', monospace; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px;">
                    <span>Redirects</span><span>&#x1F501;</span>
                </div>
                <div style="font-size: 24px; font-family: 'Orbitron', sans-serif; font-weight: 700; color: #ffffff; margin-top: 6px;">{tech["Redirects"]}</div>
            </div>
            """, unsafe_allow_html=True)

            c3.markdown(f"""
            <div class="telemetry-card" style="border-left: 4px solid #00ff87;">
                <div style="display: flex; justify-content: space-between; align-items: center; color: #8be8ff; font-family: 'JetBrains Mono', monospace; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px;">
                    <span>HTTPS Protocol</span><span>&#x1F310;</span>
                </div>
                <div style="font-size: 24px; font-family: 'Orbitron', sans-serif; font-weight: 700; color: #ffffff; margin-top: 6px;">{tech["HTTPS"]}</div>
            </div>
            """, unsafe_allow_html=True)

            st.write("")  # padding spacer

            c4, c5, c6 = st.columns(3)

            c4.markdown(f"""
            <div class="telemetry-card" style="border-left: 4px solid #ffd60a;">
                <div style="display: flex; justify-content: space-between; align-items: center; color: #8be8ff; font-family: 'JetBrains Mono', monospace; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px;">
                    <span>IP Host Target</span><span>&#x1F4E1;</span>
                </div>
                <div style="font-size: 24px; font-family: 'Orbitron', sans-serif; font-weight: 700; color: #ffffff; margin-top: 6px;">{tech["IP Based"]}</div>
            </div>
            """, unsafe_allow_html=True)

            c5.markdown(f"""
            <div class="telemetry-card" style="border-left: 4px solid #00f0ff;">
                <div style="display: flex; justify-content: space-between; align-items: center; color: #8be8ff; font-family: 'JetBrains Mono', monospace; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px;">
                    <span>Scam Keywords</span><span>&#x1F511;</span>
                </div>
                <div style="font-size: 24px; font-family: 'Orbitron', sans-serif; font-weight: 700; color: #ffffff; margin-top: 6px;">{tech["Keyword Hits"]}</div>
            </div>
            """, unsafe_allow_html=True)

            c6.markdown(f"""
            <div class="telemetry-card" style="border-left: 4px solid #ff007f;">
                <div style="display: flex; justify-content: space-between; align-items: center; color: #8be8ff; font-family: 'JetBrains Mono', monospace; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px;">
                    <span>Character Length</span><span>&#x1F4CF;</span>
                </div>
                <div style="font-size: 24px; font-family: 'Orbitron', sans-serif; font-weight: 700; color: #ffffff; margin-top: 6px;">{tech["Length"]}</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("""
            <div style="margin-top: 30px; margin-bottom: 15px;">
                <span style="font-family: 'Orbitron', sans-serif; font-size: 14px; color: #8be8ff; letter-spacing: 2px; text-transform: uppercase;">
                    &#x1F50D; Threat Indicator Details
                </span>
                <hr style="border: 0; border-top: 1px solid rgba(0, 240, 255, 0.15); margin-top: 8px; margin-bottom: 15px;">
            </div>
            """, unsafe_allow_html=True)

            if result["reasons"]:
                for reason in result["reasons"]:
                    st.markdown(
                        f'<div class="reason-chip">&#x26A0;&#xFE0F; {reason}</div>',
                        unsafe_allow_html=True
                    )
            else:
                st.markdown(
                    '<div class="reason-chip" style="border-left: 3px solid #00ff87;">&#x1F6E1;&#xFE0F; No malicious heuristic patterns detected. Clean scan.</div>',
                    unsafe_allow_html=True
                )

            recommendation = (
                "High risk URL. Do NOT open or enter credentials."
                if result["score"] >= 70
                else "Moderate / low risk. Verify carefully."
            )

            rec_border = "#ff3b30" if result["score"] >= 70 else "#ffd60a" if result["score"] >= 50 else "#00ff87"
            rec_glow   = "rgba(255, 59, 48, 0.03)" if result["score"] >= 70 else "rgba(255, 214, 10, 0.03)" if result["score"] >= 50 else "rgba(0, 255, 135, 0.03)"

            st.markdown(f"""
            <div class="recommend-card" style="border-left: 4px solid {rec_border}; background-color: {rec_glow};">
                <h4 style="margin: 0 0 8px 0; font-family: 'Orbitron', sans-serif; color: #ffffff; font-size: 15px; letter-spacing: 1px;">&#x1F6E1;&#xFE0F; DEFENSIVE ACTION RECOMMENDATION</h4>
                <p style="margin: 0; color: #d9f7ff; font-size: 14px;">{recommendation}</p>
            </div>
            """, unsafe_allow_html=True)

            pdf_file = generate_pdf(url, result, recommendation)

            st.write("")
            st.write("")

            with open(pdf_file, "rb") as file:
                st.download_button(
                    "&#x1F4C4; Download Threat Report (PDF)",
                    data=file,
                    file_name="SentraX_Threat_Report.pdf",
                    mime="application/pdf"
                )

    st.markdown('</div>', unsafe_allow_html=True)