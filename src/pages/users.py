"""
SentraX Streamlit — src/pages/users.py
Premium Enterprise User Management Page. Only accessible to Administrators.
"""

import streamlit as st
import pandas as pd
import requests
import random
import string
import time
from src.utils.auth_state import get_auth_headers

BACKEND_URL = "http://127.0.0.1:8000"


def get_users() -> list:
    """Fetch registered users list from the secure admin backend endpoint."""
    try:
        resp = requests.get(f"{BACKEND_URL}/api/admin/users", headers=get_auth_headers(), timeout=5)
        if resp.status_code == 200:
            return resp.json()
        else:
            st.error("Failed to load user directory from backend API.")
    except Exception as e:
        st.error(f"Connection error to backend: {e}")
    return []


def generate_temp_password() -> str:
    """Generate a secure 12-character temporary password for reset."""
    chars = string.ascii_letters + string.digits + "!@#$%"
    return "".join(random.choice(chars) for _ in range(12))


def render_users():
    st.markdown('<div class="brand">👥 User Management</div>', unsafe_allow_html=True)
    st.markdown('<div class="tag">// SOC ENTERPRISE IDENTITY & ROLE CONTROL</div>', unsafe_allow_html=True)
    st.write("")

    # Refresh top row
    col_ref, _ = st.columns([1, 4])
    with col_ref:
        if st.button("🔄 Refresh Directory", key="btn_refresh_directory", use_container_width=True):
            st.rerun()

    users = get_users()
    if not users:
        st.info("No registered users returned from database.")
        return

    df = pd.DataFrame(users)

    # ── Search & Filter Controls ──────────────────────────────────────────────
    st.markdown("#### 🔍 Filter Directory")
    col_search, col_role, col_status = st.columns([2, 1, 1])

    with col_search:
        search_query = st.text_input("Search by Name or Email", value="")
    with col_role:
        role_filter = st.selectbox("Role Filter", ["All", "Administrator", "Security Analyst", "Viewer"])
    with col_status:
        status_filter = st.selectbox("Status Filter", ["All", "Active", "Inactive"])

    # Apply search & filter rules
    filtered_df = df.copy()
    if search_query:
        filtered_df = filtered_df[
            filtered_df["full_name"].str.contains(search_query, case=False, na=False) |
            filtered_df["email"].str.contains(search_query, case=False, na=False)
        ]
    if role_filter != "All":
        filtered_df = filtered_df[filtered_df["role"] == role_filter]
    if status_filter != "All":
        is_active_val = 1 if status_filter == "Active" else 0
        filtered_df = filtered_df[filtered_df["is_active"] == is_active_val]

    # ── Sorting Controls ──────────────────────────────────────────────────────
    col_sort, col_dir = st.columns([2, 1])
    with col_sort:
        sort_by = st.selectbox("Sort By", ["User ID", "Name", "Role", "Created Date"])
    with col_dir:
        sort_dir = st.selectbox("Sort Direction", ["Ascending", "Descending"])

    sort_col_map = {
        "User ID": "id",
        "Name": "full_name",
        "Role": "role",
        "Created Date": "created_at"
    }
    ascending = sort_dir == "Ascending"
    filtered_df = filtered_df.sort_values(by=sort_col_map[sort_by], ascending=ascending)

    # ── Directory Table Render ────────────────────────────────────────────────
    st.markdown("### 📋 User Directory")
    display_df = filtered_df.copy()
    display_df["Status"] = display_df["is_active"].apply(lambda x: "🟢 Active" if x == 1 else "🔴 Inactive")
    display_df["Role Badge"] = display_df["role"].apply(
        lambda r: "🛡️ Administrator" if r == "Administrator" else ("💼 Security Analyst" if r == "Security Analyst" else "👁️ Viewer")
    )

    table_df = display_df[["id", "full_name", "email", "Role Badge", "Status", "created_at", "last_login"]].copy()
    table_df.columns = ["User ID", "Full Name", "Email", "Role", "Status", "Created Date", "Last Login"]

    st.dataframe(table_df, use_container_width=True, hide_index=True)

    # ── Administrator Action Console ──────────────────────────────────────────
    st.markdown("---")
    st.markdown("### ⚡ Administrator Action Console")

    user_options = {f"{u['full_name']} ({u['email']})": u for u in filtered_df.to_dict('records')}

    if not user_options:
        st.info("No registered users match the active search filters.")
        return

    selected_user_key = st.selectbox("Select User to Manage", list(user_options.keys()))
    selected_user = user_options[selected_user_key]

    c_details, c_actions, c_audit = st.columns([1.2, 1.2, 2.1])

    with c_details:
        st.markdown("#### 👤 Profile Details")
        st.write(f"**ID:** `{selected_user['id']}`")
        st.write(f"**Name:** {selected_user['full_name']}")
        st.write(f"**Email:** {selected_user['email']}")
        st.write(f"**Role:** `{selected_user['role']}`")
        st.write(f"**Status:** {'🟢 Active' if selected_user['is_active'] == 1 else '🔴 Inactive'}")
        st.write(f"**Created:** {selected_user['created_at']}")
        st.write(f"**Last Login:** {selected_user['last_login'] or 'Never'}")

    with c_actions:
        st.markdown("#### 🛠️ Modify Account")

        # 1. Change Role Action
        new_role = st.selectbox(
            "Change Role",
            ["Administrator", "Security Analyst", "Viewer"],
            index=["Administrator", "Security Analyst", "Viewer"].index(selected_user["role"])
        )
        if st.button("Save New Role", key="btn_save_role", use_container_width=True):
            if new_role == selected_user["role"]:
                st.info("Role is already set to this value.")
            else:
                headers = get_auth_headers()
                r = requests.patch(
                    f"{BACKEND_URL}/api/admin/users/{selected_user['id']}/role",
                    json={"role": new_role},
                    headers=headers,
                    timeout=5
                )
                if r.status_code == 200:
                    st.success(f"Role updated to {new_role} successfully!")
                    time.sleep(1)
                    st.rerun()
                else:
                    detail = r.json().get("detail", "Error updating role")
                    st.error(f"Failed: {detail}")

        # 2. Toggle Status Action
        st.write("")
        if selected_user["is_active"] == 1:
            if st.button("🔴 Deactivate Account", key="btn_deactivate", use_container_width=True):
                headers = get_auth_headers()
                r = requests.patch(
                    f"{BACKEND_URL}/api/admin/users/{selected_user['id']}/status",
                    json={"is_active": 0},
                    headers=headers,
                    timeout=5
                )
                if r.status_code == 200:
                    st.success("Account deactivated successfully!")
                    time.sleep(1)
                    st.rerun()
                else:
                    detail = r.json().get("detail", "Error deactivating account")
                    st.error(f"Failed: {detail}")
        else:
            if st.button("🟢 Activate Account", key="btn_activate", use_container_width=True):
                headers = get_auth_headers()
                r = requests.patch(
                    f"{BACKEND_URL}/api/admin/users/{selected_user['id']}/status",
                    json={"is_active": 1},
                    headers=headers,
                    timeout=5
                )
                if r.status_code == 200:
                    st.success("Account activated successfully!")
                    time.sleep(1)
                    st.rerun()
                else:
                    detail = r.json().get("detail", "Error activating account")
                    st.error(f"Failed: {detail}")

        # 3. Password Reset Action
        st.write("")
        st.markdown("**🔑 Password Control**")
        if st.button("Generate Temporary Password", key="btn_reset_pw", use_container_width=True):
            temp_pw = generate_temp_password()
            headers = get_auth_headers()
            r = requests.post(
                f"{BACKEND_URL}/api/admin/users/{selected_user['id']}/reset-password",
                json={"password": temp_pw},
                headers=headers,
                timeout=5
            )
            if r.status_code == 200:
                st.success("Password reset successfully!")
                st.warning(f"Temporary Password (copy now, shown only once): `{temp_pw}`")
            else:
                detail = r.json().get("detail", "Error resetting password")
                st.error(f"Failed: {detail}")

    with c_audit:
        st.markdown("#### 📜 Audit History")
        try:
            headers = get_auth_headers()
            r = requests.get(f"{BACKEND_URL}/api/admin/users/{selected_user['id']}/audit", headers=headers, timeout=5)
            if r.status_code == 200:
                logs = r.json()
                if logs:
                    for l in logs:
                        st.markdown(
                            f"**{l['timestamp']}** | `{l['event_type']}` | IP: `{l['ip_address'] or 'Local'}`\n"
                            f"> {l['details']}"
                        )
                else:
                    st.info("No audit logs found for this user.")
            else:
                st.error("Failed to load audit history.")
        except Exception as e:
            st.error(f"Error loading audit: {e}")
