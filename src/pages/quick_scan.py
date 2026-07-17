import streamlit as st
import pandas as pd
import re
import io
import time
from src.utils.detector import score_fraud_row, get_fraud_status
from src.utils.report_generator import generate_executive_pdf_report
from src.utils.explainer import (
    explain_fraud_row,
    explain_url_batch,
    explain_sms_batch,
    explain_employee_batch,
)

def get_login_hour(login_time_val):
    try:
        s = str(login_time_val).strip()
        match = re.search(r'(\d{1,2}):\d{2}', s)
        if match:
            h = int(match.group(1))
            if 'pm' in s.lower() and h < 12:
                h += 12
            elif 'am' in s.lower() and h == 12:
                h = 0
            return h
        dt = pd.to_datetime(s)
        return dt.hour
    except:
        match = re.search(r'\d+', str(login_time_val))
        if match:
            h = int(match.group(0))
            if 0 <= h <= 23:
                return h
        return 12

def generate_quick_scan_pdf(df, ds_type, ds_mod):
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Title
    story.append(Paragraph("<b>SentraX AI - Quick Scan Report</b>", styles["Title"]))
    story.append(Spacer(1, 15))

    # Metadata
    story.append(Paragraph(f"<b>Dataset Type:</b> {ds_type}", styles["Normal"]))
    story.append(Paragraph(f"<b>Activated Module:</b> {ds_mod}", styles["Normal"]))
    story.append(Paragraph(f"<b>Scan Time:</b> {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}", styles["Normal"]))
    story.append(Spacer(1, 20))

    # Table
    cols_to_use = df.columns[:5]
    table_data = [list(cols_to_use)]
    for _, row in df.head(40).iterrows():
        table_data.append([str(val)[:30] for val in row[cols_to_use].values])

    t = Table(table_data)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#061224")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor("#8be8ff")),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor("#00f0ff")),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor("#020617")),
        ('TEXTCOLOR', (0,1), (-1,-1), colors.white),
    ]))
    story.append(t)

    if len(df) > 40:
        story.append(Spacer(1, 10))
        story.append(Paragraph(f"<i>* Showing first 40 of {len(df)} rows.</i>", styles["Normal"]))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def render_quick_scan():
    st.markdown("""
    <style>
    .telemetry-card {
        background: rgba(6, 18, 36, 0.45); 
        border: 1px solid rgba(0, 240, 255, 0.12); 
        border-radius: 12px; 
        padding: 16px 20px; 
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); 
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    .telemetry-card:hover {
        border-color: rgba(0, 240, 255, 0.35);
        box-shadow: 0 8px 30px rgba(0, 240, 255, 0.08);
        transform: translateY(-2px);
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="brand">⚡ QUICK SCAN</div>', unsafe_allow_html=True)
    st.markdown('<div class="tag">// UNIVERSAL THREAT DETECTOR</div>', unsafe_allow_html=True)

    st.markdown('<div class="glass">', unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Upload dataset file for quick threat analysis (CSV, TXT, PDF)",
        type=["csv", "txt", "pdf"],
        key="quick_scan"
    )

    if uploaded_file is not None:
        file_name = uploaded_file.name.lower()

        # ── V4.3 Staged loading animation ─────────────────────────────
        stages = [
            "📁  Uploading File...",
            "🔍  Detecting Scan Type...",
            "🤖  Running Threat Analysis...",
            "📊  Generating Report...",
            "💾  Saving Scan History...",
            "✅  Completed",
        ]
        stage_ph = st.empty()
        prog_ph  = st.empty()
        prog_bar = prog_ph.progress(0)
        for i, stage in enumerate(stages):
            stage_html = ""
            for j, s in enumerate(stages):
                if j < i:
                    cls  = "v43-stage v43-stage-done"
                    icon = "✅"
                elif j == i:
                    cls  = "v43-stage v43-stage-active"
                    icon = "⟳"
                else:
                    cls  = "v43-stage v43-stage-pending"
                    icon = "○"
                stage_html += f'<div class="{cls}">{icon}&nbsp;&nbsp;{s}</div>'
            stage_ph.markdown(
                f'<div style="background:rgba(6,18,36,0.50);border:1px solid rgba(0,240,255,0.10);'
                f'border-radius:14px;padding:14px 18px;margin:10px 0;">{stage_html}</div>',
                unsafe_allow_html=True
            )
            prog_bar.progress(int((i + 1) / len(stages) * 100))
            time.sleep(0.32)
        stage_ph.empty()
        prog_ph.empty()
        ds_type = None
        ds_mod = None
        result_df = pd.DataFrame()
        scan_time_val = pd.Timestamp.now()
        
        # Threat history and report metadata
        threat_level = "LOW"
        result_summary = ""
        scan_type = ""

        # Fraud/Scam variables for rendering
        show_fraud_summary = False
        total_records = 0
        high_risk_count = 0
        medium_risk_count = 0
        low_risk_count = 0

        # PDF state variables
        pdf_error_occurred = False
        pdf_text_preview = ""

        import requests as http_requests
        from src.utils.auth_state import get_auth_headers

        backend_url = "http://127.0.0.1:8000/api/quick-scan"
        
        try:
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            response = http_requests.post(backend_url, files=files, headers=get_auth_headers(), timeout=30)
            response.raise_for_status()
            res_data = response.json()
            
            ds_type = res_data["ds_type"]
            ds_mod = res_data["ds_mod"]
            scan_type = res_data["scan_type"]
            threat_level = res_data["threat_level"]
            result_summary = res_data["result_summary"]
            show_fraud_summary = res_data["show_fraud_summary"]
            total_records = res_data["total_records"]
            high_risk_count = res_data["high_risk_count"]
            medium_risk_count = res_data["medium_risk_count"]
            low_risk_count = res_data["low_risk_count"]
            pdf_text_preview = res_data["pdf_text_preview"]
            pdf_error_occurred = res_data["pdf_error"]
            
            result_df = pd.DataFrame(res_data["records"])
            
            # Database saving logic (excluding PDF previews)
            if ds_type and ds_mod and not file_name.endswith('.pdf'):
                if scan_type and result_summary:
                    scan_id = f"{uploaded_file.name}_{scan_type}_{result_summary}"
                    if st.session_state.get("last_saved_scan") != scan_id:
                        try:
                            from src.utils.database import save_history_scan
                            save_history_scan(scan_type, uploaded_file.name, result_summary, threat_level)
                            st.session_state["last_saved_scan"] = scan_id
                        except Exception as e:
                            pass
                            
        except (http_requests.ConnectionError, http_requests.Timeout):
            st.markdown("""
            <div style="background:rgba(255,59,48,0.07);border:1px solid rgba(255,59,48,0.30);
                        border-left:4px solid #ff3b30;border-radius:14px;padding:18px 22px;
                        margin:14px 0;font-family:'JetBrains Mono',monospace;font-size:14px;
                        color:#ff8e8e;">
                &#x26A0;&#xFE0F;&nbsp;&nbsp;<b>Backend service unavailable.</b><br>
                <span style="font-size:12px;color:#63768f;">
                    Ensure the FastAPI server is running at http://127.0.0.1:8000
                    &nbsp;(<code>uvicorn main:app --reload</code> inside the backend/ folder).
                </span>
            </div>
            """, unsafe_allow_html=True)
            ds_type = None
            ds_mod = None
            result_df = pd.DataFrame()
            
        except Exception as e:
            st.error(f"Error parsing file: {str(e)}")
            ds_type = None
            ds_mod = None
            result_df = pd.DataFrame()


        # Display Auto Detection Results
        if ds_type and ds_mod:
            st.markdown(f"""
            <div class="result-safe" style="border-left: 5px solid #00f0ff;
                 background-color: rgba(6, 18, 36, 0.45);
                 margin-top: 15px; margin-bottom: 25px; padding: 15px;">
                <div style="font-family: 'Orbitron', sans-serif; color: #00f0ff;
                            font-size: 14px; font-weight: 600; text-transform: uppercase;
                            margin-bottom: 8px;">
                    🤖 AUTO DETECTION RESULT
                </div>
                <p style="font-family: 'JetBrains Mono', monospace; font-size: 13px;
                           margin: 0 0 6px 0; color: #ffffff;">
                    Dataset Type: <b>{ds_type}</b>
                </p>
                <p style="font-family: 'JetBrains Mono', monospace; font-size: 13px;
                           margin: 0; color: #8be8ff;">
                    Activated Module: <b>{ds_mod}</b>
                </p>
            </div>
            """, unsafe_allow_html=True)

            if file_name.endswith('.pdf'):
                if pdf_error_occurred:
                    st.error("PDF analysis support is currently unavailable.")
                    st.warning("Please install the required PDF dependency or try another file.")
                else:
                    st.markdown("""
                    <div style="margin-bottom: 10px; font-family: 'JetBrains Mono', monospace;
                                font-size: 11px; color: #63768f; text-transform: uppercase;
                                letter-spacing: 1px;">
                        ● PDF CONTENT PREVIEW
                    </div>
                    """, unsafe_allow_html=True)
                    st.text_area("Extracted Text Preview", value=pdf_text_preview[:1000], height=200, disabled=True)
                    st.info("⚡ Advanced PDF threat analysis coming soon.")

            else:
                # Preview Table
                st.markdown("""
                <div style="margin-bottom: 10px; font-family: 'JetBrains Mono', monospace;
                            font-size: 11px; color: #63768f; text-transform: uppercase;
                            letter-spacing: 1px;">
                    ● SCAN PREVIEW — FIRST 5 ROWS
                </div>
                """, unsafe_allow_html=True)
                st.dataframe(result_df.head(5), width="stretch", hide_index=True)

            if show_fraud_summary:
                st.markdown("""
                <div style="margin-top: 25px; margin-bottom: 15px;">
                    <span style="font-family: 'Orbitron', sans-serif; font-size: 13px;
                                 color: #8be8ff; letter-spacing: 2px; text-transform: uppercase;">
                        📊 Batch Scan Summary
                    </span>
                    <hr style="border: 0; border-top: 1px solid rgba(0, 240, 255, 0.15);
                               margin-top: 8px; margin-bottom: 20px;">
                </div>
                """, unsafe_allow_html=True)

                mc1, mc2, mc3, mc4 = st.columns(4)

                mc1.markdown(f"""
                <div class="telemetry-card" style="border-left: 4px solid #00f0ff;">
                    <div style="display: flex; justify-content: space-between; align-items: center;
                                color: #8be8ff; font-family: 'JetBrains Mono', monospace;
                                font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px;">
                        <span>Total Records</span><span>📋</span>
                    </div>
                    <div style="font-size: 28px; font-family: 'Orbitron', sans-serif;
                                font-weight: 700; color: #ffffff; margin-top: 6px;">
                        {total_records}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                mc2.markdown(f"""
                <div class="telemetry-card" style="border-left: 4px solid #ff3b30;">
                    <div style="display: flex; justify-content: space-between; align-items: center;
                                color: #8be8ff; font-family: 'JetBrains Mono', monospace;
                                font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px;">
                        <span>High Risk</span><span>🚨</span>
                    </div>
                    <div style="font-size: 28px; font-family: 'Orbitron', sans-serif;
                                font-weight: 700; color: #ff3b30; margin-top: 6px;">
                        {high_risk_count}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                mc3.markdown(f"""
                <div class="telemetry-card" style="border-left: 4px solid #ffd60a;">
                    <div style="display: flex; justify-content: space-between; align-items: center;
                                color: #8be8ff; font-family: 'JetBrains Mono', monospace;
                                font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px;">
                        <span>Medium Risk</span><span>⚠️</span>
                    </div>
                    <div style="font-size: 28px; font-family: 'Orbitron', sans-serif;
                                font-weight: 700; color: #ffd60a; margin-top: 6px;">
                        {medium_risk_count}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                mc4.markdown(f"""
                <div class="telemetry-card" style="border-left: 4px solid #00ff87;">
                    <div style="display: flex; justify-content: space-between; align-items: center;
                                color: #8be8ff; font-family: 'JetBrains Mono', monospace;
                                font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px;">
                        <span>Low Risk</span><span>✅</span>
                    </div>
                    <div style="font-size: 28px; font-family: 'Orbitron', sans-serif;
                                font-weight: 700; color: #00ff87; margin-top: 6px;">
                        {low_risk_count}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # Full Results and Downloads Section
            if not result_df.empty:
                st.markdown("""
                <div style="margin-top: 30px; margin-bottom: 15px;">
                    <span style="font-family: 'Orbitron', sans-serif; font-size: 13px;
                                 color: #8be8ff; letter-spacing: 2px; text-transform: uppercase;">
                        🗃️ Analysis Report View
                    </span>
                    <hr style="border: 0; border-top: 1px solid rgba(0, 240, 255, 0.15);
                               margin-top: 8px; margin-bottom: 15px;">
                </div>
                """, unsafe_allow_html=True)

                st.dataframe(result_df, width="stretch", hide_index=True)

                # Generate download payloads
                csv_data = result_df.to_csv(index=False).encode('utf-8')
                
                txt_report = f"SentraX AI - Quick Scan Results Report\n"
                txt_report += f"==================================\n"
                txt_report += f"Dataset Type: {ds_type}\n"
                txt_report += f"Activated Module: {ds_mod}\n"
                txt_report += f"Scan Time: {scan_time_val}\n\n"
                if file_name.endswith('.pdf') and not pdf_error_occurred:
                    txt_report += f"Extracted Text Content:\n{pdf_text_preview}\n"
                else:
                    txt_report += result_df.to_string(index=False)
                txt_bytes = txt_report.encode('utf-8')

                pdf_success = True
                pdf_bytes = b""
                
                if not file_name.endswith('.pdf'):
                    try:
                        pdf_bytes = generate_executive_pdf_report(
                            uploaded_file.name,
                            scan_type,
                            threat_level,
                            result_summary
                        )
                    except Exception as pdf_gen_err:
                        pdf_success = False
                else:
                    pdf_success = False

                # Downloads layout
                st.markdown("<p style='font-size: 12px; color: #63768f; margin-bottom: 5px;'>DOWNLOAD TELEMETRY REPORT:</p>", unsafe_allow_html=True)
                
                if not file_name.endswith('.pdf') and not pdf_success:
                    st.error("Unable to generate Executive PDF report.")
                
                dl_cols = st.columns(3)
                
                dl_cols[0].download_button(
                    label="📥 Download CSV",
                    data=csv_data,
                    file_name="quick_scan_report.csv",
                    mime="text/csv",
                    width="stretch"
                )
                dl_cols[1].download_button(
                    label="📥 Download TXT",
                    data=txt_bytes,
                    file_name="quick_scan_report.txt",
                    mime="text/plain",
                    width="stretch"
                )
                if not file_name.endswith('.pdf') and pdf_success:
                    dl_cols[2].download_button(
                        label="📄 Download Executive PDF Report",
                        data=pdf_bytes,
                        file_name="executive_threat_report.pdf",
                        mime="application/pdf",
                        width="stretch"
                    )

                # ── V4.3 Success notification cards ───────────────────────────
                st.markdown("""
                <div style="margin-top:18px;">
                    <div class="v43-notify v43-notify-success">✅&nbsp;&nbsp;Threat Analysis Completed</div>
                    <div class="v43-notify v43-notify-info">📄&nbsp;&nbsp;Executive Report Generated</div>
                    <div class="v43-notify v43-notify-warn">🗂&nbsp;&nbsp;History Updated</div>
                </div>
                """, unsafe_allow_html=True)

                # ── AI Analysis Explainability Card ───────────────────────────
                if ds_type == "Transaction Dataset":
                    from src.utils.explainer import _render_ai_card
                    batch_reasons = []
                    if high_risk_count > 0:
                        batch_reasons.append(
                            f"{high_risk_count} transaction(s) exceeded the ₹20,000 high-risk threshold.")
                    if medium_risk_count > 0:
                        batch_reasons.append(
                            f"{medium_risk_count} transaction(s) triggered medium-risk indicators (unknown location or new device).")
                    if low_risk_count > 0:
                        batch_reasons.append(
                            f"{low_risk_count} transaction(s) were within normal parameters — no anomalies detected.")
                    if not batch_reasons:
                        batch_reasons = [f"All {total_records} transactions analysed. No anomalies found."]
                    _tier = "HIGH" if high_risk_count > 0 else "MEDIUM" if medium_risk_count > 0 else "LOW"
                    _col  = "#ff3b30" if _tier == "HIGH" else "#ffd60a" if _tier == "MEDIUM" else "#00ff87"
                    _bg   = ("rgba(255,59,48,0.10)" if _tier == "HIGH"
                             else "rgba(255,214,10,0.08)" if _tier == "MEDIUM"
                             else "rgba(0,255,135,0.08)")
                    _conf = 92 if _tier == "HIGH" else 78 if _tier == "MEDIUM" else 72
                    _recs = (
                        ["Freeze flagged transactions immediately.",
                         "Verify customer identity via secondary authentication.",
                         "Monitor accounts for repeated anomalies.",
                         "Escalate to fraud investigation team."]
                        if _tier == "HIGH" else
                        ["Place flagged transactions on hold pending review.",
                         "Request additional verification from customers.",
                         "Monitor account activity for 24 hours."]
                        if _tier == "MEDIUM" else
                        ["All transactions within normal parameters.",
                         "Continue standard monitoring protocols."]
                    )
                    _render_ai_card(batch_reasons, _conf, _recs, _tier, _col, _bg)

                elif ds_type == "URL Dataset":
                    susp = int((result_df["Status"] == "SUSPICIOUS").sum()) if "Status" in result_df.columns else 0
                    explain_url_batch(len(result_df), susp)

                elif ds_type in ("SMS Dataset", "SMS Dataset (Plain Text)"):
                    pred_col = "Prediction" if "Prediction" in result_df.columns else None
                    scam_cnt = int((result_df[pred_col] == "SCAM").sum()) if pred_col else 0
                    explain_sms_batch(len(result_df), scam_cnt)

                elif ds_type == "Employee Dataset":
                    risk_col = "Risk Level" if "Risk Level" in result_df.columns else None
                    susp_emp = int((result_df[risk_col] == "SUSPICIOUS").sum()) if risk_col else 0
                    explain_employee_batch(len(result_df), susp_emp)

    else:
        # ── V4.3 Empty State ──────────────────────────────────────────────────
        st.markdown("""
        <div class="v43-empty">
            <div class="v43-empty-icon">📂</div>
            <div class="v43-empty-title">No File Uploaded</div>
            <div class="v43-empty-body">
                Upload a <b style="color:#8be8ff;">CSV</b>,
                <b style="color:#8be8ff;">TXT</b> or
                <b style="color:#8be8ff;">PDF</b> file to begin threat analysis.<br>
                SentraX AI will auto-detect the dataset type and route<br>it to the appropriate intelligence engine.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
