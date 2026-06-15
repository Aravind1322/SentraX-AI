import sys
import os
import streamlit as st

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.utils.database import init_db

from src.components.styles import load_styles
from src.pages.home import render_home
from src.pages.scanner import render_scanner
from src.pages.sms import render_sms
from src.pages.dashboard import render_dashboard
from src.pages.enterprise import render_enterprise
from src.pages.about import render_about
from src.pages.assistant import render_copilot

st.set_page_config(
    page_title="SentraX AI",
    page_icon="🛡️",
    layout="wide"
)

load_styles()
init_db()

st.sidebar.title("🛡️ SentraX AI")

page = st.sidebar.radio(
    "Navigate",
    ["🏠 Home", "🔍 Scanner", "📩 SMS", "📊 Dashboard", "🏢 Enterprise", "ℹ️ About"]
)

if page == "🏠 Home":
    render_home()
elif page == "🔍 Scanner":
    render_scanner()
elif page == "📩 SMS":
    render_sms()
elif page == "📊 Dashboard":
    render_dashboard()
elif page == "🏢 Enterprise":
    render_enterprise()
elif page == "ℹ️ About":
    render_about()

# Render Floating AI Copilot globally across all pages
render_copilot()