import streamlit as st
import time
from src.utils.detector import predict_url
from src.utils.report import generate_pdf
from src.utils.database import save_scan


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

        with st.spinner("Deep threat analysis running..."):
            time.sleep(1)

        result = predict_url(url)

        save_scan(url, result["label"], result["score"])

        if result["label"] == "Fraud / Phishing":
            st.markdown(f"""
            <div class="result-danger">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
                    <h3 style="margin: 0; color: #ff3b30; font-family: 'Orbitron', sans-serif; font-size: 18px;">🚨 FRAUD / PHISHING DETECTED</h3>
                    <span style="font-family: 'JetBrains Mono', monospace; font-size: 10px; font-weight: 600; padding: 3px 8px; background: rgba(255, 59, 48, 0.2); border: 1px solid #ff3b30; border-radius: 4px; color: #ff3b30; letter-spacing: 1px;">CRITICAL</span>
                </div>
                <p style="font-family: 'JetBrains Mono', monospace; font-size: 14px; margin: 0; color: #ff8e8e;">
                    Risk Assessment: <b>HIGH RISK</b> | Threat Score: <b>{result["score"]}/100</b>
                </p>
            </div>
            """, unsafe_allow_html=True)

        else:
            st.markdown(f"""
            <div class="result-safe">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
                    <h3 style="margin: 0; color: #00ff87; font-family: 'Orbitron', sans-serif; font-size: 18px;">✅ SAFE URL VERIFIED</h3>
                    <span style="font-family: 'JetBrains Mono', monospace; font-size: 10px; font-weight: 600; padding: 3px 8px; background: rgba(0, 255, 135, 0.2); border: 1px solid #00ff87; border-radius: 4px; color: #00ff87; letter-spacing: 1px;">VERIFIED</span>
                </div>
                <p style="font-family: 'JetBrains Mono', monospace; font-size: 14px; margin: 0; color: #a1ffcc;">
                    Risk Assessment: <b>NO IMMEDIATE THREAT</b> | Threat Score: <b>{result["score"]}/100</b>
                </p>
            </div>
            """, unsafe_allow_html=True)

        # High fidelity neon percentage progress bar
        bar_color = "#ff3b30" if result["score"] >= 70 else "#ffd60a" if result["score"] >= 50 else "#00ff87"
        st.markdown(f"""
        <div style="width: 100%; background-color: rgba(255, 255, 255, 0.05); border-radius: 10px; height: 12px; border: 1px solid rgba(255, 255, 255, 0.1); overflow: hidden; margin-top: 15px; margin-bottom: 25px; box-shadow: inset 0 2px 4px rgba(0,0,0,0.5);">
            <div style="width: {result["score"]}%; background: linear-gradient(90deg, #00f0ff, {bar_color}); height: 100%; box-shadow: 0 0 10px {bar_color};"></div>
        </div>
        """, unsafe_allow_html=True)

        tech = result["technical"]

        st.markdown("""
        <div style="margin-top: 25px; margin-bottom: 15px;">
            <span style="font-family: 'Orbitron', sans-serif; font-size: 14px; color: #8be8ff; letter-spacing: 2px; text-transform: uppercase;">
                🌐 Technical Security Metrics
            </span>
            <hr style="border: 0; border-top: 1px solid rgba(0, 240, 255, 0.15); margin-top: 8px; margin-bottom: 20px;">
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)

        c1.markdown(f"""
        <div class="telemetry-card" style="border-left: 4px solid #00f0ff;">
            <div style="display: flex; justify-content: space-between; align-items: center; color: #8be8ff; font-family: 'JetBrains Mono', monospace; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px;">
                <span>SSL Status</span>
                <span>🔒</span>
            </div>
            <div style="font-size: 24px; font-family: 'Orbitron', sans-serif; font-weight: 700; color: #ffffff; margin-top: 6px;">{tech["SSL"]}</div>
        </div>
        """, unsafe_allow_html=True)

        c2.markdown(f"""
        <div class="telemetry-card" style="border-left: 4px solid #ff007f;">
            <div style="display: flex; justify-content: space-between; align-items: center; color: #8be8ff; font-family: 'JetBrains Mono', monospace; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px;">
                <span>Redirects</span>
                <span>🔁</span>
            </div>
            <div style="font-size: 24px; font-family: 'Orbitron', sans-serif; font-weight: 700; color: #ffffff; margin-top: 6px;">{tech["Redirects"]}</div>
        </div>
        """, unsafe_allow_html=True)

        c3.markdown(f"""
        <div class="telemetry-card" style="border-left: 4px solid #00ff87;">
            <div style="display: flex; justify-content: space-between; align-items: center; color: #8be8ff; font-family: 'JetBrains Mono', monospace; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px;">
                <span>HTTPS Protocol</span>
                <span>🌐</span>
            </div>
            <div style="font-size: 24px; font-family: 'Orbitron', sans-serif; font-weight: 700; color: #ffffff; margin-top: 6px;">{tech["HTTPS"]}</div>
        </div>
        """, unsafe_allow_html=True)

        st.write("")  # padding spacer

        c4, c5, c6 = st.columns(3)

        c4.markdown(f"""
        <div class="telemetry-card" style="border-left: 4px solid #ffd60a;">
            <div style="display: flex; justify-content: space-between; align-items: center; color: #8be8ff; font-family: 'JetBrains Mono', monospace; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px;">
                <span>IP Host Target</span>
                <span>📡</span>
            </div>
            <div style="font-size: 24px; font-family: 'Orbitron', sans-serif; font-weight: 700; color: #ffffff; margin-top: 6px;">{tech["IP Based"]}</div>
        </div>
        """, unsafe_allow_html=True)

        c5.markdown(f"""
        <div class="telemetry-card" style="border-left: 4px solid #00f0ff;">
            <div style="display: flex; justify-content: space-between; align-items: center; color: #8be8ff; font-family: 'JetBrains Mono', monospace; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px;">
                <span>Scam Keywords</span>
                <span>🔑</span>
            </div>
            <div style="font-size: 24px; font-family: 'Orbitron', sans-serif; font-weight: 700; color: #ffffff; margin-top: 6px;">{tech["Keyword Hits"]}</div>
        </div>
        """, unsafe_allow_html=True)

        c6.markdown(f"""
        <div class="telemetry-card" style="border-left: 4px solid #ff007f;">
            <div style="display: flex; justify-content: space-between; align-items: center; color: #8be8ff; font-family: 'JetBrains Mono', monospace; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px;">
                <span>Character Length</span>
                <span>📏</span>
            </div>
            <div style="font-size: 24px; font-family: 'Orbitron', sans-serif; font-weight: 700; color: #ffffff; margin-top: 6px;">{tech["Length"]}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="margin-top: 30px; margin-bottom: 15px;">
            <span style="font-family: 'Orbitron', sans-serif; font-size: 14px; color: #8be8ff; letter-spacing: 2px; text-transform: uppercase;">
                🔍 Threat Indicator Details
            </span>
            <hr style="border: 0; border-top: 1px solid rgba(0, 240, 255, 0.15); margin-top: 8px; margin-bottom: 15px;">
        </div>
        """, unsafe_allow_html=True)

        if result["reasons"]:
            for reason in result["reasons"]:
                st.markdown(
                    f'<div class="reason-chip">⚠️ {reason}</div>',
                    unsafe_allow_html=True
                )

        else:
            st.markdown(
                '<div class="reason-chip" style="border-left: 3px solid #00ff87;">🛡️ No malicious heuristic patterns detected. Clean scan.</div>',
                unsafe_allow_html=True
            )

        recommendation = (
            "High risk URL. Do NOT open or enter credentials."
            if result["score"] >= 70
            else "Moderate / low risk. Verify carefully."
        )

        rec_border = "#ff3b30" if result["score"] >= 70 else "#ffd60a" if result["score"] >= 50 else "#00ff87"
        rec_glow = "rgba(255, 59, 48, 0.03)" if result["score"] >= 70 else "rgba(255, 214, 10, 0.03)" if result["score"] >= 50 else "rgba(0, 255, 135, 0.03)"

        st.markdown(f"""
        <div class="recommend-card" style="border-left: 4px solid {rec_border}; background-color: {rec_glow};">
            <h4 style="margin: 0 0 8px 0; font-family: 'Orbitron', sans-serif; color: #ffffff; font-size: 15px; letter-spacing: 1px;">🛡️ DEFENSIVE ACTION RECOMMENDATION</h4>
            <p style="margin: 0; color: #d9f7ff; font-size: 14px;">{recommendation}</p>
        </div>
        """, unsafe_allow_html=True)

        pdf_file = generate_pdf(
            url,
            result,
            recommendation
        )

        st.write("")
        st.write("")

        with open(pdf_file, "rb") as file:
            st.download_button(
                "📄 Download Threat Report (PDF)",
                data=file,
                file_name="SentraX_Threat_Report.pdf",
                mime="application/pdf"
            )

    st.markdown('</div>', unsafe_allow_html=True)