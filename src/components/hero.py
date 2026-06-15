import streamlit as st

def show_hero():
    st.markdown(
        '<div class="brand">🛡️ SentraX AI</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="tag">// DIGITAL FRAUD SHIELD & THREAT INTELLIGENCE</div>',
        unsafe_allow_html=True
    )

    st.markdown('<div class="glass">', unsafe_allow_html=True)

    st.markdown("""
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 15px;">
        <span style="display: inline-block; width: 10px; height: 10px; background-color: #00ff87; border-radius: 50%; box-shadow: 0 0 10px #00ff87;"></span>
        <span style="font-family: 'JetBrains Mono', monospace; font-size: 13px; color: #00ff87; letter-spacing: 2px; text-transform: uppercase;">
            System Status: Active & Monitoring
        </span>
    </div>
    <h1 style='font-size:46px; margin-bottom:12px; background: linear-gradient(135deg, #ffffff 60%, #8be8ff 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>
    Detect. Defend. Dominate.
    </h1>
    <p style='font-size:18px; color:#8be8ff; font-family: "Inter", sans-serif; line-height: 1.6; margin-bottom: 25px; max-width: 800px;'>
    SentraX AI is an advanced threat intelligence console. Harness predictive telemetry to scan malicious URLs, analyze scam communication vectors, and secure digital enterprise operations.
    </p>
    """, unsafe_allow_html=True)

    if st.button("Launch Protection"):
        st.success("🟢 SentraX Protection Activated")

    st.markdown('</div>', unsafe_allow_html=True)