import streamlit as st
import pandas as pd
import re
import io
from src.utils.detector import score_fraud_row, get_fraud_status
from src.utils.report_generator import generate_executive_pdf_report

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

        if file_name.endswith('.csv'):
            try:
                raw_df = pd.read_csv(uploaded_file)
                cols_lower = {str(c).strip().lower() for c in raw_df.columns}
                col_map = {c.lower(): c for c in raw_df.columns}

                if {"amount", "location", "device"}.issubset(cols_lower):
                    ds_type = "Transaction Dataset"
                    ds_mod = "Fraud Detection API"
                    
                    df_work = raw_df.rename(columns={
                        col_map["amount"]: "amount",
                        col_map["location"]: "location",
                        col_map["device"]: "device",
                    })

                    df_work["Risk Score"] = df_work.apply(score_fraud_row, axis=1)
                    df_work["Status"] = df_work["Risk Score"].apply(get_fraud_status)

                    result_df = raw_df.copy()
                    result_df["Risk Score"] = df_work["Risk Score"].values
                    result_df["Status"] = df_work["Status"].values
                    result_df["Scan Time"] = scan_time_val

                    total_records = len(df_work)
                    high_risk_count = int((df_work["Status"] == "HIGH RISK").sum())
                    medium_risk_count = int((df_work["Status"] == "MEDIUM RISK").sum())
                    low_risk_count = int((df_work["Status"] == "LOW RISK").sum())
                    show_fraud_summary = True

                elif "url" in cols_lower:
                    ds_type = "URL Dataset"
                    ds_mod = "URL Intelligence"
                    
                    url_col = col_map["url"]
                    keywords = ["paypal", "verify", "secure-update", "bank", "login"]
                    
                    def check_url(val):
                        val_str = str(val).lower()
                        if any(kw in val_str for kw in keywords):
                            return "SUSPICIOUS"
                        return "SAFE"

                    result_df = pd.DataFrame()
                    result_df["URL"] = raw_df[url_col]
                    result_df["Status"] = raw_df[url_col].apply(check_url)
                    result_df["Scan Time"] = scan_time_val

                elif "message" in cols_lower:
                    ds_type = "SMS Dataset"
                    ds_mod = "Scam Filtering"
                    
                    msg_col = col_map["message"]
                    keywords = ["lottery", "winner", "claim", "urgent", "verify", "prize"]

                    def check_sms(val):
                        val_str = str(val).lower()
                        if any(kw in val_str for kw in keywords):
                            return "SCAM"
                        return "SAFE"

                    result_df = pd.DataFrame()
                    result_df["Message"] = raw_df[msg_col]
                    result_df["Prediction"] = raw_df[msg_col].apply(check_sms)
                    result_df["Scan Time"] = scan_time_val

                elif {"employee", "login_time"}.issubset(cols_lower):
                    ds_type = "Employee Dataset"
                    ds_mod = "Employee Monitoring"

                    emp_col = col_map["employee"]
                    time_col = col_map["login_time"]

                    def check_employee(val):
                        hour = get_login_hour(val)
                        if hour < 6:
                            return "SUSPICIOUS"
                        return "NORMAL"

                    result_df = pd.DataFrame()
                    result_df["Employee"] = raw_df[emp_col]
                    result_df["Risk Level"] = raw_df[time_col].apply(check_employee)
                    result_df["Scan Time"] = scan_time_val

                else:
                    ds_type = "Generic CSV Dataset"
                    ds_mod = "Standard Analyzer"
                    result_df = raw_df.copy()
                    result_df["Scan Time"] = scan_time_val

            except Exception as e:
                st.error(f"Error parsing CSV file: {str(e)}")

        elif file_name.endswith('.txt'):
            try:
                content = uploaded_file.read().decode("utf-8")
                lines = [line.strip() for line in content.splitlines() if line.strip()]
                
                ds_type = "SMS Dataset (Plain Text)"
                ds_mod = "Scam Filtering"

                keywords = ["lottery", "winner", "claim", "urgent", "verify", "prize"]
                def check_sms(val):
                    val_str = str(val).lower()
                    if any(kw in val_str for kw in keywords):
                        return "SCAM"
                    return "SAFE"

                result_df = pd.DataFrame()
                result_df["Message"] = lines
                result_df["Prediction"] = pd.Series(lines).apply(check_sms).values
                result_df["Scan Time"] = scan_time_val
            except Exception as e:
                st.error(f"Error parsing TXT file: {str(e)}")

        elif file_name.endswith('.pdf'):
            ds_type = "Document Dataset (PDF)"
            ds_mod = "PDF Threat Intelligence"
            
            try:
                import pypdf
                reader = pypdf.PdfReader(uploaded_file)
                extracted = []
                for i in range(min(5, len(reader.pages))):
                    text = reader.pages[i].extract_text()
                    if text:
                        extracted.append(text)
                pdf_text_preview = "\n".join(extracted)
                if not pdf_text_preview.strip():
                    pdf_text_preview = "[No readable text extracted from PDF]"
            except Exception as e:
                pdf_error_occurred = True

            result_df = pd.DataFrame([
                {"Metric": "Scan Parameter", "Value": "PDF Threat Analysis"},
                {"Metric": "File Name", "Value": uploaded_file.name},
                {"Metric": "Preview Extract Size (chars)", "Value": len(pdf_text_preview) if not pdf_error_occurred else 0}
            ])
            result_df["Scan Time"] = scan_time_val

        # Database saving logic (excluding PDF previews)
        if ds_type and ds_mod and not file_name.endswith('.pdf'):
            threat_level = "LOW"
            result_summary = ""
            scan_type = ""

            if ds_type == "Transaction Dataset":
                scan_type = "Fraud"
                if high_risk_count > 0:
                    threat_level = "HIGH"
                elif medium_risk_count > 0:
                    threat_level = "MEDIUM"
                else:
                    threat_level = "LOW"
                result_summary = f"Total Records: {total_records} | High Risk: {high_risk_count} | Medium Risk: {medium_risk_count} | Low Risk: {low_risk_count}"

            elif ds_type == "URL Dataset":
                scan_type = "URL"
                susp = int((result_df["Status"] == "SUSPICIOUS").sum())
                if susp > 0:
                    threat_level = "HIGH"
                else:
                    threat_level = "LOW"
                result_summary = f"Total URLs: {len(result_df)} | Suspicious: {susp} | Safe: {len(result_df) - susp}"

            elif ds_type == "SMS Dataset":
                scan_type = "SMS"
                scam = int((result_df["Prediction"] == "SCAM").sum())
                if scam > 0:
                    threat_level = "HIGH"
                else:
                    threat_level = "LOW"
                result_summary = f"Total Messages: {len(result_df)} | Scam: {scam} | Safe: {len(result_df) - scam}"

            elif ds_type == "Employee Dataset":
                scan_type = "Employee"
                susp = int((result_df["Risk Level"] == "SUSPICIOUS").sum())
                if susp > 0:
                    threat_level = "MEDIUM"
                else:
                    threat_level = "LOW"
                result_summary = f"Total Logs: {len(result_df)} | Suspicious: {susp} | Normal: {len(result_df) - susp}"

            elif ds_type == "SMS Dataset (Plain Text)":
                scan_type = "TXT"
                scam = int((result_df["Prediction"] == "SCAM").sum())
                if scam > 0:
                    threat_level = "HIGH"
                else:
                    threat_level = "LOW"
                result_summary = f"Total Lines: {len(result_df)} | Scam: {scam} | Safe: {len(result_df) - scam}"

            if scan_type and result_summary:
                scan_id = f"{uploaded_file.name}_{scan_type}_{result_summary}"
                if st.session_state.get("last_saved_scan") != scan_id:
                    try:
                        from src.utils.database import save_history_scan
                        save_history_scan(scan_type, uploaded_file.name, result_summary, threat_level)
                        st.session_state["last_saved_scan"] = scan_id
                    except Exception as e:
                        pass

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
                st.dataframe(result_df.head(5), use_container_width=True, hide_index=True)

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

                st.dataframe(result_df, use_container_width=True, hide_index=True)

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
                    use_container_width=True
                )
                dl_cols[1].download_button(
                    label="📥 Download TXT",
                    data=txt_bytes,
                    file_name="quick_scan_report.txt",
                    mime="text/plain",
                    use_container_width=True
                )
                if not file_name.endswith('.pdf') and pdf_success:
                    dl_cols[2].download_button(
                        label="📄 Download Executive PDF Report",
                        data=pdf_bytes,
                        file_name="executive_threat_report.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )

    st.markdown('</div>', unsafe_allow_html=True)
