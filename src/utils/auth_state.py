"""
SentraX Streamlit — utils/auth_state.py
Manages JWT login sessions, storage, roles, and dev bypass configurations.
"""

import os
import requests
import streamlit as st
import time
import re
from typing import Optional, Dict, Any

ENABLE_DEV_BYPASS = os.getenv("ENABLE_DEV_BYPASS", "False").lower() == "true"
BACKEND_URL = "https://sentrax-ai-6vqu.onrender.com"


def init_auth_session():
    """
    Initialise session state keys on first run.
    In dev mode, automatically sets an anonymous analyst identity
    unless the user has explicitly logged out this session.
    """
    # Initialise keys on very first page load
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "user" not in st.session_state:
        st.session_state.user = None
    if "token" not in st.session_state:
        st.session_state.token = None
    # Tracks whether the user intentionally logged out in this browser session
    if "_explicit_logout" not in st.session_state:
        st.session_state._explicit_logout = False
    # Action (login or register)
    if "auth_action" not in st.session_state:
        st.session_state.auth_action = "login"

    # Apply anonymous dev bypass only if user hasn't explicitly logged out
    if ENABLE_DEV_BYPASS and not st.session_state.authenticated and not st.session_state._explicit_logout:
        st.session_state.authenticated = True
        st.session_state.user = {
            "email": "anonymous@sentrax.ai",
            "role": "Anonymous Analyst",
            "full_name": "Anonymous Analyst",
        }
        # token stays None — backend will treat absent header as anonymous


def login_user(email: str, password: str) -> bool:
    """
    Submit JSON credentials to /api/auth/login.
    On success, stores access_token and user profile in session state.
    """
    try:
        url = f"{BACKEND_URL}/api/auth/login"
        # Backend expects JSON body: {"email": ..., "password": ...}
        resp = requests.post(url, json={"email": email, "password": password}, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            user_obj = data.get("user", {})
            st.session_state.token = data.get("access_token")
            st.session_state.user = {
                "email": user_obj.get("email", email),
                "role": user_obj.get("role", "Viewer"),
                "full_name": user_obj.get("full_name", email),
            }
            st.session_state.authenticated = True
            st.session_state._explicit_logout = False
            return True
        else:
            try:
                detail = resp.json().get("detail", "Login failed")
            except Exception:
                detail = resp.text or "Login failed"
            st.error(f"Authentication failed: {detail}")
    except requests.ConnectionError:
        st.error("Cannot reach backend. Ensure the FastAPI server is running at http://127.0.0.1:8000")
    except Exception as e:
        st.error(f"Login error: {e}")
    return False


def register_user_api(full_name: str, email: str, password: str) -> bool:
    """Submit registration data to /api/auth/register."""
    try:
        url = f"{BACKEND_URL}/api/auth/register"
        resp = requests.post(url, json={
            "full_name": full_name,
            "email": email,
            "password": password,
            "role": "Security Analyst"
        }, timeout=5)
        if resp.status_code == 200:
            return True
        else:
            try:
                detail = resp.json().get("detail", "Registration failed")
            except Exception:
                detail = resp.text or "Registration failed"
            st.error(f"Registration failed: {detail}")
    except requests.ConnectionError:
        st.error("Cannot reach backend. Ensure the FastAPI server is running.")
    except Exception as e:
        st.error(f"Registration error: {e}")
    return False


def logout_user():
    """Completely clear authentication state and mark the explicit logout flag."""
    st.session_state.token = None
    st.session_state.user = None
    st.session_state.authenticated = False
    st.session_state._explicit_logout = True
    st.rerun()


def get_auth_headers() -> Dict[str, str]:
    """
    Return an Authorization header dict when a JWT token is available.
    Falls back to an empty dict for anonymous sessions — the backend
    will recognise the missing header and grant anonymous analyst access.
    """
    token = st.session_state.get("token")
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}


def render_login_page():
    """Render the premium login or registration interface."""
    # Ensure action key is initialized
    if "auth_action" not in st.session_state:
        st.session_state.auth_action = "login"

    if st.session_state.auth_action == "login":
        st.markdown("""
        <div style="text-align:center;margin-top:60px;margin-bottom:30px;">
            <h2 style="font-family:'Orbitron',sans-serif;color:#ffffff;letter-spacing:2px;">🛡️ SENTRAX AI SOC LOGIN</h2>
            <p style="font-family:'JetBrains Mono',monospace;color:#63768f;font-size:11px;">ENTERPRISE CYBER INTELLIGENCE PLATFORM</p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with st.form("login_form"):
                email = st.text_input("Security Email", value="admin@sentrax.ai")
                password = st.text_input("Security Password", type="password", value="Admin@123")
                submit = st.form_submit_button("Authenticate Session")

                if submit:
                    if login_user(email, password):
                        st.success("Access Granted! Loading SOC command center...")
                        st.rerun()
            
            st.markdown("<div style='text-align: center; margin-top: 15px;'>", unsafe_allow_html=True)
            if st.button("Create Account", key="btn_toggle_register"):
                st.session_state.auth_action = "register"
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    elif st.session_state.auth_action == "register":
        st.markdown("""
        <div style="text-align:center;margin-top:60px;margin-bottom:30px;">
            <h2 style="font-family:'Orbitron',sans-serif;color:#ffffff;letter-spacing:2px;">🛡️ CREATE SOC ACCOUNT</h2>
            <p style="font-family:'JetBrains Mono',monospace;color:#63768f;font-size:11px;">ENTERPRISE CYBER INTELLIGENCE PLATFORM</p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with st.form("register_form"):
                full_name = st.text_input("Full Name")
                email = st.text_input("Security Email")
                password = st.text_input("Security Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")
                submit = st.form_submit_button("Create Account")

                if submit:
                    if not full_name or not email or not password or not confirm_password:
                        st.error("All fields are required.")
                    elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                        st.error("Please enter a valid email address.")
                    elif len(password) < 8:
                        st.error("Password must be at least 8 characters long.")
                    elif password != confirm_password:
                        st.error("Passwords do not match.")
                    else:
                        if register_user_api(full_name, email, password):
                            st.success("Account created successfully! Redirecting to login...")
                            time.sleep(1.5)
                            st.session_state.auth_action = "login"
                            st.rerun()

            st.markdown("<div style='text-align: center; margin-top: 15px;'>", unsafe_allow_html=True)
            if st.button("Back to Login", key="btn_toggle_login"):
                st.session_state.auth_action = "login"
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
