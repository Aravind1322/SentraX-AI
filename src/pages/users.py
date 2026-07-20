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
from src.utils.auth_state import get_auth_headers, BACKEND_URL


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

    users = get_users()
    if not users:
        st.info("No registered users returned from database.")
        return

    df = pd.DataFrame(users)

    # ── User Statistics Row ──────────────────────────────────────────────────
    total_users = len(df)
    active_users = len(df[df["is_active"] == 1])
    disabled_users = len(df[df["is_active"] == 0])

    st.markdown("#### 📊 Directory Statistics")
    c_tot, c_act, c_dis = st.columns(3)
    c_tot.metric("Total Users", total_users)
    c_act.metric("Active Users", f"🟢 {active_users}")
    c_dis.metric("Disabled Users", f"🔴 {disabled_users}")
    st.write("")

    # ── Create New User Expander ─────────────────────────────────────────────
    with st.expander("➕ Create New User Account", expanded=False):
        with st.form("create_user_form", clear_on_submit=True):
            new_name = st.text_input("Full Name")
            new_email = st.text_input("Email Address")
            new_password = st.text_input("Password (min 8 chars)", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            new_role = st.selectbox("Role", ["Security Analyst", "Viewer", "Administrator"])
            new_status = st.selectbox("Initial Status", ["Active", "Disabled"])

            submit_create = st.form_submit_button("Register New User", width="stretch")

            if submit_create:
                if not new_name or not new_email:
                    st.error("Please fill in all fields.")
                elif len(new_password) < 8:
                    st.error("Password must be at least 8 characters long.")
                elif new_password != confirm_password:
                    st.error("Passwords do not match.")
                else:
                    try:
                        payload = {
                            "full_name": new_name.strip(),
                            "email": new_email.strip(),
                            "password": new_password,
                            "confirm_password": confirm_password,
                            "role": new_role,
                            "is_active": 1 if new_status == "Active" else 0
                        }
                        r = requests.post(f"{BACKEND_URL}/api/admin/users", json=payload, headers=get_auth_headers(), timeout=5)
                        if r.status_code == 200:
                            st.success("User created successfully!")
                            time.sleep(1.5)
                            st.rerun()
                        else:
                            detail = r.json().get("detail", "Error creating user.")
                            st.error(f"Failed: {detail}")
                    except Exception as e:
                        st.error(f"Error calling backend: {e}")

    # ── Search & Filter Controls ──────────────────────────────────────────────
    st.markdown("#### 🔍 Filter Directory")
    col_search, col_role, col_status = st.columns([2, 1, 1])

    with col_search:
        search_query = st.text_input("Search by Name, Email, or Role", value="")
    with col_role:
        role_filter = st.selectbox("Role Filter", ["All", "Administrator", "Security Analyst", "Viewer"])
    with col_status:
        status_filter = st.selectbox("Status Filter", ["All", "Active", "Disabled"])

    # Apply search & filter rules
    filtered_df = df.copy()
    if search_query:
        filtered_df = filtered_df[
            filtered_df["full_name"].str.contains(search_query, case=False, na=False) |
            filtered_df["email"].str.contains(search_query, case=False, na=False) |
            filtered_df["role"].str.contains(search_query, case=False, na=False)
        ]
    if role_filter != "All":
        filtered_df = filtered_df[filtered_df["role"] == role_filter]
    if status_filter != "All":
        is_active_val = 1 if status_filter == "Active" else 0
        filtered_df = filtered_df[filtered_df["is_active"] == is_active_val]

    # ── Sorting & Pagination Controls ─────────────────────────────────────────
    col_sort, col_dir, col_page = st.columns([2, 1, 1])
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

    # Simple Pagination
    items_per_page = 10
    total_items = len(filtered_df)
    total_pages = max(1, (total_items + items_per_page - 1) // items_per_page)
    with col_page:
        page_num = st.number_input("Page", min_value=1, max_value=total_pages, value=1)
    
    start_idx = (page_num - 1) * items_per_page
    end_idx = start_idx + items_per_page
    page_df = filtered_df.iloc[start_idx:end_idx]

    # ── Directory Table Render ────────────────────────────────────────────────
    st.markdown("### 📋 User Directory")
    display_df = page_df.copy()
    display_df["Status"] = display_df["is_active"].apply(lambda x: "🟢 Active" if x == 1 else "🔴 Disabled")
    display_df["Role Badge"] = display_df["role"].apply(
        lambda r: "🛡️ Administrator" if r == "Administrator" else ("💼 Security Analyst" if r == "Security Analyst" else "👁️ Viewer")
    )

    table_df = display_df.copy()
    table_df["Avatar"] = "👤"
    table_df["Actions"] = "⚙️ Manage below"
    table_df = table_df[["Avatar", "full_name", "email", "Role Badge", "Status", "last_login", "created_at", "Actions"]]
    table_df.columns = ["Avatar", "Full Name", "Email", "Role", "Status", "Last Login", "Created Date", "Actions"]

    st.dataframe(table_df, width="stretch", hide_index=True)

    # ── Administrator Action Console ──────────────────────────────────────────
    st.markdown("---")
    st.markdown("### ⚡ Administrator Action Console")

    user_options = {f"{u['full_name']} ({u['email']})": u for u in filtered_df.to_dict('records')}

    if not user_options:
        st.info("No registered users match the active search filters.")
        return

    selected_user_key = st.selectbox("Select User to Manage", list(user_options.keys()))
    selected_user = user_options[selected_user_key]

    c_details, c_actions = st.columns([1.2, 1.2])

    with c_details:
        st.markdown("#### 👤 Profile Details")
        st.write(f"**ID:** `{selected_user['id']}`")
        st.write(f"**Name:** {selected_user['full_name']}")
        st.write(f"**Email:** {selected_user['email']}")
        st.write(f"**Role:** `{selected_user['role']}`")
        st.write(f"**Status:** {'🟢 Active' if selected_user['is_active'] == 1 else '🔴 Disabled'}")
        st.write(f"**Created:** {selected_user['created_at']}")
        st.write(f"**Last Login:** {selected_user['last_login'] or 'Never'}")

    with c_actions:
        st.markdown("#### 🛠️ Modify Account")

        # 1. Edit User Details Form
        with st.form("edit_details_form"):
            edit_name = st.text_input("Name", value=selected_user["full_name"])
            edit_role = st.selectbox(
                "Role",
                ["Administrator", "Security Analyst", "Viewer"],
                index=["Administrator", "Security Analyst", "Viewer"].index(selected_user["role"])
            )
            edit_status = st.selectbox(
                "Status",
                ["Active", "Disabled"],
                index=0 if selected_user["is_active"] == 1 else 1
            )
            submit_edit = st.form_submit_button("Update User Details", width="stretch")

            if submit_edit:
                try:
                    payload = {
                        "full_name": edit_name.strip(),
                        "role": edit_role,
                        "is_active": 1 if edit_status == "Active" else 0
                    }
                    r = requests.put(
                        f"{BACKEND_URL}/api/admin/users/{selected_user['id']}",
                        json=payload,
                        headers=get_auth_headers(),
                        timeout=5
                    )
                    if r.status_code == 200:
                        st.success("User details updated successfully!")
                        time.sleep(1.5)
                        st.rerun()
                    else:
                        detail = r.json().get("detail", "Error updating details.")
                        st.error(f"Failed: {detail}")
                except Exception as e:
                    st.error(f"Connection error: {e}")

        # 2. Reset Password Control
        st.write("")
        st.markdown("**🔑 Password Control**")
        if st.button("Generate Temporary Password", key="btn_reset_pw", width="stretch"):
            temp_pw = generate_temp_password()
            r = requests.post(
                f"{BACKEND_URL}/api/admin/users/{selected_user['id']}/reset-password",
                json={"password": temp_pw},
                headers=get_auth_headers(),
                timeout=5
            )
            if r.status_code == 200:
                st.success("Password reset successfully!")
                st.warning(f"Temporary Password (copy now, shown only once): `{temp_pw}`")
            else:
                detail = r.json().get("detail", "Error resetting password")
                st.error(f"Failed: {detail}")

        # 3. Delete Account Action
        st.write("")
        st.markdown("**⚠️ Danger Zone**")
        confirm_delete = st.checkbox("Confirm permanent deletion", key=f"del_conf_{selected_user['id']}")
        if st.button("❌ Delete User Account", key="btn_delete_user", width="stretch"):
            if not confirm_delete:
                st.error("Please check the confirmation box to delete this user.")
            else:
                try:
                    r = requests.delete(
                        f"{BACKEND_URL}/api/admin/users/{selected_user['id']}",
                        headers=get_auth_headers(),
                        timeout=5
                    )
                    if r.status_code == 200:
                        st.success("User deleted successfully!")
                        time.sleep(1.5)
                        st.rerun()
                    else:
                        detail = r.json().get("detail", "Error deleting user.")
                        st.error(f"Failed: {detail}")
                except Exception as e:
                    st.error(f"Connection error: {e}")


