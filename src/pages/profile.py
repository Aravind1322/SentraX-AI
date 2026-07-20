"""
SentraX Streamlit — src/pages/profile.py
User Profile Page. Accessible by all authenticated users to view profile & change password.
"""

import streamlit as st
import requests
import time
from src.utils.auth_state import get_auth_headers, BACKEND_URL


def get_profile() -> dict:
    """Fetch logged in user profile from secure auth backend."""
    try:
        resp = requests.get(f"{BACKEND_URL}/api/auth/me", headers=get_auth_headers(), timeout=5)
        if resp.status_code == 200:
            return resp.json()
        else:
            st.error("Failed to load profile from backend API.")
    except Exception as e:
        st.error(f"Connection error to backend: {e}")
    return {}


def render_profile():
    st.markdown('<div class="brand">👤 User Profile</div>', unsafe_allow_html=True)
    st.markdown('<div class="tag">// PERSONAL SOC WORKSPACE DETAILS</div>', unsafe_allow_html=True)
    st.write("")

    profile = get_profile()
    if not profile:
        st.warning("No profile data found. Please log in.")
        return

    col_info, col_password = st.columns(2)

    with col_info:
        st.markdown("""
        <div style="background:rgba(6,18,36,0.5);border:1px solid rgba(0,240,255,0.15);
                    border-top:3px solid #00f0ff;border-radius:10px;padding:24px;margin-bottom:20px;">
            <h4 style="color:#00f0ff;margin:0 0 16px 0;font-family:'Orbitron',sans-serif;font-size:16px;">
                IDENTITY INFORMATION
            </h4>
            <div style="font-family:'JetBrains Mono',monospace;font-size:13px;line-height:2;">
                <span style="color:#63768f;">Full Name:</span> <span style="color:#ffffff;">{}</span><br>
                <span style="color:#63768f;">Email Addr:</span> <span style="color:#ffffff;">{}</span><br>
                <span style="color:#63768f;">Role Level:</span> <span style="color:#ffd60a;">{}</span><br>
                <span style="color:#63768f;">Acc Status:</span> <span style="color:#00ff87;">{}</span><br>
                <span style="color:#63768f;">Created At:</span> <span style="color:#ffffff;">{}</span><br>
                <span style="color:#63768f;">Last Login:</span> <span style="color:#ffffff;">{}</span>
            </div>
        </div>
        """.format(
            profile.get("full_name", ""),
            profile.get("email", ""),
            profile.get("role", ""),
            "Active" if profile.get("is_active") == 1 else "Disabled",
            profile.get("created_at", ""),
            profile.get("last_login", "Never")
        ), unsafe_allow_html=True)

    with col_password:
        st.markdown("""
        <div style="background:rgba(6,18,36,0.5);border:1px solid rgba(0,240,255,0.15);
                    border-top:3px solid #ff3b30;border-radius:10px;padding:24px;margin-bottom:20px;">
            <h4 style="color:#ff3b30;margin:0 0 16px 0;font-family:'Orbitron',sans-serif;font-size:16px;">
                PASSWORD CONTROL
            </h4>
        </div>
        """, unsafe_allow_html=True)

        with st.form("change_password_form", clear_on_submit=True):
            current_pw = st.text_input("Current Password", type="password")
            new_pw = st.text_input("New Password (min 8 chars)", type="password")
            confirm_new_pw = st.text_input("Confirm New Password", type="password")
            submit = st.form_submit_button("Update Password", width="stretch")

            if submit:
                if not current_pw:
                    st.error("Please enter your current password.")
                elif len(new_pw) < 8:
                    st.error("New password must be at least 8 characters long.")
                elif new_pw != confirm_new_pw:
                    st.error("New passwords do not match.")
                else:
                    try:
                        headers = get_auth_headers()
                        payload = {
                            "current_password": current_pw,
                            "new_password": new_pw
                        }
                        r = requests.post(f"{BACKEND_URL}/api/auth/change-password", json=payload, headers=headers, timeout=5)
                        if r.status_code == 200:
                            st.success("Password changed successfully!")
                            time.sleep(1.5)
                            st.rerun()
                        else:
                            detail = r.json().get("detail", "Error changing password.")
                            st.error(f"Failed: {detail}")
                    except Exception as e:
                        st.error(f"Connection error: {e}")
