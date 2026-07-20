import streamlit as st
import time
import requests as http_requests
from src.utils.explainer import explain_sms
from src.utils.auth_state import get_auth_headers, BACKEND_URL as _BACKEND_URL


def _call_backend_sms(message: str):
    """
    POST to /api/sms/scan and return the result dict,
    or None if the backend is unavailable.
    """
    try:
        resp = http_requests.post(
            f"{_BACKEND_URL}/api/sms/scan",
            json={"message": message},
            headers=get_auth_headers(),
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        # Normalise to the shape expected by the existing UI + explainer
        return {
            "label":   data.get("label", "Legitimate"),
            "score":   data.get("score", 5),
            "reasons": data.get("reasons", []),
        }
    except (http_requests.ConnectionError, http_requests.Timeout):
        return None
    except Exception:
        return None


def render_sms():
    st.markdown('<div class="brand">SMS Shield</div>', unsafe_allow_html=True)
    st.markdown('<div class="tag">// SCAM MESSAGE INTELLIGENCE</div>', unsafe_allow_html=True)

    st.markdown('<div class="glass">', unsafe_allow_html=True)

    sms = st.text_area("Paste suspicious SMS message", placeholder="e.g. Congratulations! You have won a prize. Claim now...")

    if st.button("Analyze Message"):

        # ── V4.3 Staged loading animation ─────────────────────────────
        stages = [
            "&#x1F4E8;  Reading SMS content...",
            "&#x1F916;  Running AI Detection Engine...",
            "&#x26A0;&#xFE0F;  Classifying Scam Indicators...",
            "&#x1F4BE;  Logging Scan Result...",
        ]
        stage_ph = st.empty()
        prog_ph  = st.empty()
        prog_bar = prog_ph.progress(0)

        for i, stage in enumerate(stages):
            stage_html = ""
            for j, s in enumerate(stages):
                if j < i:
                    cls  = "v43-stage v43-stage-done"
                    icon = "&#x2705;"
                elif j == i:
                    cls  = "v43-stage v43-stage-active"
                    icon = "&#x27F3;"
                else:
                    cls  = "v43-stage v43-stage-pending"
                    icon = "&#x25CB;"
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
        result = _call_backend_sms(sms)

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
            score = result["score"]

            # ── Detection result banner ──────────────────────────────────
            if result["label"] == "Scam Message":
                st.markdown("""
                <div class="result-danger">
                    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;">
                        <h3 style="margin:0;color:#ff3b30;font-family:'Orbitron',sans-serif;font-size:18px;">&#x26A0;&#xFE0F; SCAM MESSAGE DETECTED</h3>
                        <span style="font-family:'JetBrains Mono',monospace;font-size:10px;font-weight:600;
                                     padding:3px 8px;background:rgba(255,59,48,0.2);border:1px solid #ff3b30;
                                     border-radius:4px;color:#ff3b30;letter-spacing:1px;">CRITICAL</span>
                    </div>
                    <p style="font-family:'JetBrains Mono',monospace;font-size:14px;margin:0;color:#ff8e8e;">
                        This message contains scam indicators. Do NOT respond or click any links.
                    </p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="result-safe">
                    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;">
                        <h3 style="margin:0;color:#00ff87;font-family:'Orbitron',sans-serif;font-size:18px;">&#x2705; LEGITIMATE MESSAGE</h3>
                        <span style="font-family:'JetBrains Mono',monospace;font-size:10px;font-weight:600;
                                     padding:3px 8px;background:rgba(0,255,135,0.2);border:1px solid #00ff87;
                                     border-radius:4px;color:#00ff87;letter-spacing:1px;">VERIFIED</span>
                    </div>
                    <p style="font-family:'JetBrains Mono',monospace;font-size:14px;margin:0;color:#a1ffcc;">
                        No scam patterns detected in this message.
                    </p>
                </div>
                """, unsafe_allow_html=True)

            # ── V4.3 Threat Score Gauge ──────────────────────────────────
            bar_color  = "#ff3b30" if score >= 70 else "#ffd60a" if score >= 50 else "#00ff87"
            tier_label = "HIGH" if score >= 70 else "MODERATE" if score >= 50 else "LOW"
            tier_bg    = ("rgba(255,59,48,0.12)"   if score >= 70
                          else "rgba(255,214,10,0.10)" if score >= 50
                          else "rgba(0,255,135,0.08)")
            filled     = "\u2588" * (score // 10)
            empty_b    = "\u2591" * (10 - score // 10)

            st.markdown(f"""
            <div class="v43-gauge-wrap">
                <div class="v43-gauge-label">Scam Risk Score</div>
                <div class="v43-gauge-score" style="color:{bar_color};">{score}
                    <span style="font-size:18px;color:#63768f;">/100</span>
                </div>
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

            # ── V4.3 Success notification cards ─────────────────────────
            st.markdown("""
            <div class="v43-notify v43-notify-success">&#x2705;&nbsp;&nbsp;Threat Analysis Completed &#x2014; via SentraX Backend API</div>
            <div class="v43-notify v43-notify-info">&#x1F4C4;&nbsp;&nbsp;SMS Scam Intelligence Report Generated</div>
            <div class="v43-notify v43-notify-warn">&#x1F5C2;&nbsp;&nbsp;Result Logged to Session History</div>
            """, unsafe_allow_html=True)

            # ── AI Analysis Explainability Card ─────────────────────────
            explain_sms(result)

    st.markdown('</div>', unsafe_allow_html=True)