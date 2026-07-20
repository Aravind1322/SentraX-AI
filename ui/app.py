import sys
import os
import streamlit as st

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.utils.database import init_db
st.caption("Frontend Build v2 - July 20")

from src.components.styles import load_styles
from src.pages.home import render_home
from src.pages.scanner import render_scanner
from src.pages.sms import render_sms
from src.pages.quick_scan import render_quick_scan
from src.pages.dashboard import render_dashboard
from src.pages.enterprise import render_enterprise
from src.pages.about import render_about
from src.pages.users import render_users
from src.pages.threat_intel import render_threat_intel
from src.pages.profile import render_profile

from src.utils.auth_state import init_auth_session, render_login_page, logout_user

st.set_page_config(
    page_title="SentraX AI",
    page_icon="🛡️",
    layout="wide",
)
st.caption("Frontend Build v2 - July 20")

load_styles()
if "_db_initialized" not in st.session_state:
    init_db()
    st.session_state._db_initialized = True

# ── Authentication ─────────────────────────────────────────────────────────────
init_auth_session()
if not st.session_state.authenticated:
    render_login_page()
    st.stop()

# ── WebSocket listeners (start once per session; stored in session_state) ──────
try:
    from src.utils.websocket_client import AlertListener, DashboardListener, ScanFeedListener
    if "_alert_listener" not in st.session_state:
        st.session_state._alert_listener = AlertListener()
        st.session_state._alert_listener.start()
    if "_dash_listener" not in st.session_state:
        st.session_state._dash_listener = DashboardListener()
        st.session_state._dash_listener.start()
    if "_scan_listener" not in st.session_state:
        st.session_state._scan_listener = ScanFeedListener()
        st.session_state._scan_listener.start()
    _alert_listener = st.session_state._alert_listener
    _dash_listener = st.session_state._dash_listener
    _scan_listener = st.session_state._scan_listener
    _ws_available = True
except Exception:
    _ws_available = False
    _alert_listener = _dash_listener = _scan_listener = None

# ── Sidebar ────────────────────────────────────────────────────────────────────
st.sidebar.title("🛡️ SentraX AI")

user_role = st.session_state.user.get("role", "Anonymous Analyst")

if user_role == "Administrator":
    nav_options = ["🏠 Home", "🌐 URL Scanner", "📩 SMS Scanner", "⚡ Quick Scan", "📊 Dashboard", "🏢 Enterprise", "👥 User Management", "🎯 Threat Intelligence", "👤 Profile", "ℹ️ About"]
elif user_role == "Security Analyst":
    nav_options = ["🏠 Home", "🌐 URL Scanner", "📩 SMS Scanner", "⚡ Quick Scan", "📊 Dashboard", "🎯 Threat Intelligence", "👤 Profile", "ℹ️ About"]
elif user_role == "Viewer":
    nav_options = ["🏠 Home", "🌐 URL Scanner", "📩 SMS Scanner", "⚡ Quick Scan", "📊 Dashboard", "🎯 Threat Intelligence", "👤 Profile", "ℹ️ About"]
else:  # Anonymous Analyst fallback
    nav_options = ["🌐 URL Scanner", "📩 SMS Scanner", "⚡ Quick Scan", "ℹ️ About"]

# Initialize or sanitize navigation state
if "nav_radio" not in st.session_state or st.session_state.nav_radio not in nav_options:
    st.session_state.nav_radio = nav_options[0]

page = st.sidebar.radio("Navigate", nav_options, key="nav_radio")

st.sidebar.markdown("---")
st.sidebar.markdown(f"👤 **{st.session_state.user['full_name']}**")
st.sidebar.markdown(f"💼 Role: `{st.session_state.user['role']}`")
if st.sidebar.button("Logout Session"):
    logout_user()

# ── Live connection status indicator ──────────────────────────────────────────
if _ws_available:
    alerts_live = _alert_listener.connected
    dash_live   = _dash_listener.connected
    all_live    = alerts_live and dash_live
    dot   = "🟢" if all_live else "🟡"
    label = "LIVE" if all_live else "RECONNECTING…"
    st.sidebar.markdown(
        f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:10px;'
        f'color:{"#00ff87" if all_live else "#ffd60a"};margin-top:4px;">'
        f'{dot} WebSocket {label}</div>',
        unsafe_allow_html=True,
    )

# ── Page routing ───────────────────────────────────────────────────────────────
if page == "🏠 Home":
    render_home()
elif page == "🌐 URL Scanner":
    render_scanner()
elif page == "📩 SMS Scanner":
    render_sms()
elif page == "⚡ Quick Scan":
    render_quick_scan()
elif page == "📊 Dashboard":
    render_dashboard()
elif page == "🏢 Enterprise":
    render_enterprise()
elif page == "👥 User Management":
    render_users()
elif page == "🎯 Threat Intelligence":
    render_threat_intel()
elif page == "👤 Profile":
    render_profile()
elif page == "ℹ️ About":
    render_about()

# ── Real-time event processing ────────────────────────────────────────────────
if _ws_available:
    # 1. Security alert toasts
    for alert in _alert_listener.get_new_alerts():
        sev = str(alert.get('severity','LOW')).upper()
        if sev in ["HIGH", "CRITICAL"]:
            st.toast(
                f"🚨 **{sev} THREAT DETECTED**\n\n"
                f"**{alert.get('title','')}**\n"
                f"{alert.get('description','')}",
                icon="🚨"
            )
        else:
            st.toast(
                f"🛡️ **{sev} ALERT**\n\n"
                f"**{alert.get('title','')}**\n"
                f"{alert.get('description','')}",
                icon="🛡️"
            )

    # 2. Dashboard live updates — rerun once if any new data arrived
    new_scans = _scan_listener.get_new_scans()
    dash_events = _dash_listener.get_events()
    if (new_scans or dash_events) and page == "📊 Dashboard":
        st.rerun()