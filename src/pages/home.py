import streamlit as st
from src.components.hero import show_hero

def render_home():
    show_hero()

    st.markdown("""
    <div style="margin-top: 30px; margin-bottom: 15px;">
        <span style="font-family: 'Orbitron', sans-serif; font-size: 14px; color: #8be8ff; letter-spacing: 2px; text-transform: uppercase;">
            📊 Live Threat Telemetry
        </span>
        <hr style="border: 0; border-top: 1px solid rgba(0, 240, 255, 0.15); margin-top: 8px; margin-bottom: 20px;">
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)

    c1.metric("Threats Blocked", "1,284", "+12%")
    c2.metric("Scam Messages", "472", "+8%")
    c3.metric("Risk Alerts", "89", "+17%")