import streamlit as st
from src.utils.detector import predict_sms

def render_sms():
    st.markdown('<div class="brand">SMS Shield</div>', unsafe_allow_html=True)
    st.markdown('<div class="tag">Scam Message Intelligence</div>', unsafe_allow_html=True)

    st.markdown('<div class="glass">', unsafe_allow_html=True)

    sms = st.text_area("Paste suspicious SMS")

    if st.button("Analyze Message"):
        result = predict_sms(sms)

        if result["label"] == "Scam Message":
            st.error("⚠️ Scam Message Detected")
            st.progress(result["score"])
            st.write(f"### Risk Score: {result['score']} / 100")
        else:
            st.success("✅ Legitimate Message")
            st.progress(result["score"])
            st.write(f"### Risk Score: {result['score']} / 100")

    st.markdown('</div>', unsafe_allow_html=True)