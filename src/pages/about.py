import streamlit as st

def render_about():
    st.markdown('<div class="brand">About SentraX</div>', unsafe_allow_html=True)

    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.write("""
**SentraX AI** is an AI-powered cyber fraud intelligence platform.

Built for:
- phishing detection
- scam SMS analysis
- fraud scoring
- enterprise cyber defense

**Built by Arav ⚡**
""")
    st.markdown('</div>', unsafe_allow_html=True)