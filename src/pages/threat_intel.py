"""
SentraX Streamlit — src/pages/threat_intel.py
Premium Threat Intelligence Center Page.
Supports CRUD, metrics dashboards, import/export, and audit history.
"""

import streamlit as st
import pandas as pd
import requests
import json
import time
from src.utils.auth_state import get_auth_headers, BACKEND_URL


def fetch_kpis() -> dict:
    """Fetch Threat Intel KPIs from backend."""
    try:
        r = requests.get(f"{BACKEND_URL}/api/ioc/kpis", headers=get_auth_headers(), timeout=5)
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        st.error(f"Error fetching KPIs: {e}")
    return {"total_threats": 0, "critical_iocs": 0, "high_risk_iocs": 0, "recently_added": 0}


def fetch_iocs() -> list:
    """Fetch all active IOC watchlist items."""
    try:
        r = requests.get(f"{BACKEND_URL}/api/ioc", headers=get_auth_headers(), timeout=5)
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        st.error(f"Error fetching IOC records: {e}")
    return []


def fetch_triggers() -> list:
    """Fetch recently triggered IOC matches."""
    try:
        r = requests.get(f"{BACKEND_URL}/api/ioc/triggers", headers=get_auth_headers(), timeout=5)
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        st.error(f"Error fetching triggers: {e}")
    return []


def render_threat_intel():
    user_role = st.session_state.user.get("role", "Anonymous Analyst")
    if user_role not in ["Viewer", "Security Analyst", "Administrator"]:
        st.error("Access Denied: Insufficient permissions to view Threat Intelligence.")
        return

    st.markdown('<div class="brand">🎯 Threat Intelligence Center</div>', unsafe_allow_html=True)
    st.markdown('<div class="tag">// ACTIVE WATCHLIST & REAL-TIME CORRELATION ENGINE</div>', unsafe_allow_html=True)
    st.write("")

    # Top KPI Row
    kpis = fetch_kpis()
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Known Threats", kpis.get("total_threats", 0))
    col2.metric("Critical IOCs", kpis.get("critical_iocs", 0), delta_color="inverse")
    col3.metric("High Risk IOCs", kpis.get("high_risk_iocs", 0), delta_color="inverse")
    col4.metric("Recently Added (7d)", kpis.get("recently_added", 0))

    st.markdown("---")

    # Fetch IOC data once and reuse across all widgets
    iocs_all = fetch_iocs()

    # ── Refresh & Export Actions Row ──────────────────────────────────────────
    col_ref, col_exp, _ = st.columns([1, 1, 3])
    with col_ref:
        if st.button("🔄 Refresh Data", key="btn_refresh_intel", width="stretch"):
            st.rerun()

    with col_exp:
        if user_role in ["Security Analyst", "Administrator"]:
            iocs_data = iocs_all
            if iocs_data:
                export_json = json.dumps(iocs_data, indent=2)
                st.download_button(
                    label="📥 Export IOC List",
                    data=export_json,
                    file_name="sentrax_ioc_watchlist.json",
                    mime="application/json",
                    width="stretch"
                )
            else:
                st.button("📥 Export IOC List", disabled=True, width="stretch")

    # ── Add & Import IOCs (Admin Only) ────────────────────────────────────────
    if user_role == "Administrator":
        with st.expander("➕ Add Single IOC Signature", expanded=False):
            with st.form("form_add_ioc"):
                ioc_type = st.selectbox("IOC Type", ["domain", "url", "ip", "email", "phone", "file_hash"])
                value = st.text_input("IOC Value (exact match or domain suffix)")
                severity = st.selectbox("Severity", ["LOW", "MEDIUM", "HIGH", "CRITICAL"])
                confidence = st.slider("Confidence Score", 0, 100, 80)
                source = st.text_input("Intelligence Source", value="Manual Entry")
                description = st.text_area("Description / Threat Classification Details", value="Threat intelligence watchlist item")
                status_val = st.selectbox("Status", ["Active", "Inactive"])
                
                submitted = st.form_submit_button("Add to Watchlist")
                if submitted:
                    if not value.strip():
                        st.error("IOC Value cannot be empty.")
                    else:
                        payload = {
                            "ioc_type": ioc_type,
                            "value": value.strip(),
                            "severity": severity,
                            "confidence": confidence,
                            "source": source.strip(),
                            "description": description.strip(),
                            "status": status_val
                        }
                        r = requests.post(f"{BACKEND_URL}/api/ioc", json=payload, headers=get_auth_headers(), timeout=5)
                        if r.status_code == 200:
                            st.success(f"Successfully added IOC signature: {value}")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(f"Error adding IOC: {r.text}")

        with st.expander("📥 Import IOC Batch List (JSON)", expanded=False):
            st.markdown(
                "Upload or paste a JSON batch file containing a list of IOC signatures. "
                "Format: `[ { \"ioc_type\": \"domain\", \"value\": \"badsite.com\", \"severity\": \"HIGH\" }, ... ]`"
            )
            import_method = st.radio("Import Source", ["Upload File", "Paste Raw JSON"])
            
            if import_method == "Upload File":
                uploaded_file = st.file_uploader("Choose JSON File", type="json")
                if uploaded_file is not None:
                    try:
                        raw_data = json.load(uploaded_file)
                        if st.button("Verify and Import Uploaded IOCs"):
                            r = requests.post(f"{BACKEND_URL}/api/ioc/import", json=raw_data, headers=get_auth_headers(), timeout=10)
                            if r.status_code == 200:
                                st.success("IOC batch imported successfully!")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error(f"Import failed: {r.text}")
                    except Exception as json_err:
                        st.error(f"Invalid JSON format: {json_err}")
            else:
                json_paste = st.text_area("Paste JSON Payload", height=150)
                if st.button("Verify and Import Pasted IOCs"):
                    try:
                        raw_data = json.loads(json_paste)
                        r = requests.post(f"{BACKEND_URL}/api/ioc/import", json=raw_data, headers=get_auth_headers(), timeout=10)
                        if r.status_code == 200:
                            st.success("IOC batch imported successfully!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(f"Import failed: {r.text}")
                    except Exception as json_err:
                        st.error(f"Invalid JSON format: {json_err}")

    # ── Active Watchlist Directory Table ──────────────────────────────────────
    st.markdown("### 📋 Active Watchlist Indicators")
    iocs = iocs_all

    if iocs:
        df = pd.DataFrame(iocs)

        # Filters Row
        col_search, col_t_filter, col_s_filter = st.columns([2, 1, 1])
        with col_search:
            search_query = st.text_input("Search IOC Value or Description", value="")
        with col_t_filter:
            type_filter = st.selectbox("Filter Type", ["All"] + list(df["ioc_type"].unique()))
        with col_s_filter:
            sev_filter = st.selectbox("Filter Severity", ["All", "LOW", "MEDIUM", "HIGH", "CRITICAL"])

        # Apply Filters
        filtered_df = df.copy()
        if search_query:
            filtered_df = filtered_df[
                filtered_df["value"].str.contains(search_query, case=False, na=False) |
                filtered_df["description"].str.contains(search_query, case=False, na=False)
            ]
        if type_filter != "All":
            filtered_df = filtered_df[filtered_df["ioc_type"] == type_filter]
        if sev_filter != "All":
            filtered_df = filtered_df[filtered_df["severity"] == sev_filter]

        # Sorting Options
        col_sort, col_dir = st.columns([2, 1])
        with col_sort:
            sort_by = st.selectbox("Sort Watchlist By", ["Value", "Type", "Severity", "Created Date"])
        with col_dir:
            sort_dir = st.selectbox("Sort Watchlist Direction", ["Ascending", "Descending"])

        sort_col_map = {
            "Value": "value",
            "Type": "ioc_type",
            "Severity": "severity",
            "Created Date": "created_at"
        }
        ascending = sort_dir == "Ascending"
        filtered_df = filtered_df.sort_values(by=sort_col_map[sort_by], ascending=ascending)

        # Display Dataframe
        display_df = filtered_df.copy()
        display_df["Severity Badge"] = display_df["severity"].apply(
            lambda s: "🔴 CRITICAL" if s == "CRITICAL" else ("🟠 HIGH" if s == "HIGH" else ("🟡 MEDIUM" if s == "MEDIUM" else "🟢 LOW"))
        )
        display_df["Confidence %"] = display_df["confidence"].astype(str) + "%"
        
        table_df = display_df[["id", "ioc_type", "value", "Severity Badge", "Confidence %", "source", "description", "status", "created_at"]].copy()
        table_df.columns = ["ID", "Type", "Value", "Severity", "Confidence", "Source", "Description", "Status", "Created Date"]
        st.dataframe(table_df, width="stretch", hide_index=True)

        # ── Edit & Delete Console (Admin Only) ────────────────────────────────────
        if user_role == "Administrator":
            st.markdown("#### ⚙️ Edit / Delete watchlist records")
            ioc_options = {f"ID: {u['id']} | [{u['ioc_type'].upper()}] {u['value']}": u for u in filtered_df.to_dict('records')}
            
            if ioc_options:
                selected_key = st.selectbox("Select Signature to Edit or Delete", list(ioc_options.keys()))
                selected_ioc = ioc_options[selected_key]
                
                c_edit, c_del = st.columns(2)
                
                with c_edit:
                    with st.form("form_edit_ioc"):
                        edit_type = st.selectbox("Edit Type", ["domain", "url", "ip", "email", "phone", "file_hash"], index=["domain", "url", "ip", "email", "phone", "file_hash"].index(selected_ioc["ioc_type"]))
                        edit_val = st.text_input("Edit Value", value=selected_ioc["value"])
                        edit_sev = st.selectbox("Edit Severity", ["LOW", "MEDIUM", "HIGH", "CRITICAL"], index=["LOW", "MEDIUM", "HIGH", "CRITICAL"].index(selected_ioc["severity"]))
                        edit_conf = st.slider("Edit Confidence", 0, 100, selected_ioc["confidence"])
                        edit_src = st.text_input("Edit Source", value=selected_ioc["source"])
                        edit_desc = st.text_area("Edit Description", value=selected_ioc["description"])
                        edit_status = st.selectbox("Edit Status", ["Active", "Inactive"], index=["Active", "Inactive"].index(selected_ioc["status"]))
                        
                        save_edits = st.form_submit_button("Save Watchlist Edits")
                        if save_edits:
                            payload = {
                                "ioc_type": edit_type,
                                "value": edit_val.strip(),
                                "severity": edit_sev,
                                "confidence": edit_conf,
                                "source": edit_src.strip(),
                                "description": edit_desc.strip(),
                                "status": edit_status
                            }
                            r = requests.put(f"{BACKEND_URL}/api/ioc/{selected_ioc['id']}", json=payload, headers=get_auth_headers(), timeout=5)
                            if r.status_code == 200:
                                st.success("Watchlist signature updated successfully!")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error(f"Failed to update: {r.text}")
                                
                with c_del:
                    st.markdown("**Destructive Watchlist Action**")
                    st.warning("Deleting this signature stops active matching alerts immediately.")
                    if st.button("❌ Permanent Delete Signature", key="btn_del_ioc", width="stretch"):
                        r = requests.delete(f"{BACKEND_URL}/api/ioc/{selected_ioc['id']}", headers=get_auth_headers(), timeout=5)
                        if r.status_code == 200:
                            st.success("Watchlist signature deleted successfully!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(f"Failed to delete: {r.text}")
    else:
        st.info("Watchlist watchlist is currently empty.")

    # ── Threat History / Triggers Feed ────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 📜 Real-Time Threat History (IOC Triggers)")
    triggers = fetch_triggers()

    if triggers:
        triggers_df = pd.DataFrame(triggers)
        triggers_df["Severity Badge"] = triggers_df["severity"].apply(
            lambda s: "🔴 CRITICAL" if s == "CRITICAL" else ("🟠 HIGH" if s == "HIGH" else ("🟡 MEDIUM" if s == "MEDIUM" else "🟢 LOW"))
        )
        t_table = triggers_df[["timestamp", "user_email", "scanner", "ioc_value", "Severity Badge", "action"]].copy()
        t_table.columns = ["Timestamp", "User Email", "Scanner Module", "Trigger Value", "Threat Severity", "Outcome Action"]
        
        st.dataframe(t_table, width="stretch", hide_index=True)
    else:
        st.info("No threat signatures have triggered matches yet.")
