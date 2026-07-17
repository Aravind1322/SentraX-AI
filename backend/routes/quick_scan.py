"""
SentraX AI Backend — routes/quick_scan.py
Quick Scan unified dataset analysis and routing endpoint.
"""

from fastapi import APIRouter, UploadFile, File, Depends, Header, BackgroundTasks
import io
import csv
from typing import Dict, Any, List, Optional
from services.url_service import scan_url
from services.sms_service import scan_sms
from services.fraud_service import scan_fraud
from services.employee_service import scan_employee
from datetime import datetime
from utils.security import get_current_user, RoleChecker

router = APIRouter()


@router.post("", summary="Perform a quick scan on a dataset file")
async def quick_scan_endpoint(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: Dict[str, Any] = Depends(RoleChecker(["Anonymous Analyst", "Security Analyst", "Administrator"]))
):
    """
    Upload a dataset file (CSV, TXT, or PDF) for automatic type detection
    and internal routing to URL, SMS, Fraud, or Employee scanners.
    """
    file_name = file.filename.lower()
    content = await file.read()
    
    ds_type = "Unknown Dataset"
    ds_mod = "Unknown Module"
    scan_type = ""
    threat_level = "LOW"
    result_summary = ""
    records: List[Dict[str, Any]] = []
    
    show_fraud_summary = False
    total_records = 0
    high_risk_count = 0
    medium_risk_count = 0
    low_risk_count = 0
    
    pdf_error_occurred = False
    pdf_text_preview = ""
    
    scan_time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if file_name.endswith('.csv'):
        try:
            decoded = content.decode("utf-8", errors="ignore")
            # Parse CSV rows
            f = io.StringIO(decoded)
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            
            if fieldnames:
                cols_lower = {str(c).strip().lower() for c in fieldnames}
                col_map = {c.lower().strip(): c for c in fieldnames}
                
                # 1. Transaction Dataset
                if {"amount", "location", "device"}.issubset(cols_lower):
                    ds_type = "Transaction Dataset"
                    ds_mod = "Fraud Detection API"
                    scan_type = "Fraud"
                    show_fraud_summary = True
                    
                    raw_rows = list(reader)
                    total_records = len(raw_rows)
                    
                    for row in raw_rows:
                        # Extract and parse values
                        amount_col = col_map["amount"]
                        location_col = col_map["location"]
                        device_col = col_map["device"]
                        
                        try:
                            amount_val = float(str(row.get(amount_col, 0)).replace(',', '').strip())
                        except:
                            amount_val = 0.0
                        
                        loc_val = str(row.get(location_col, "")).strip()
                        dev_val = str(row.get(device_col, "")).strip()
                        
                        # Call the backend service
                        res = scan_fraud(amount_val, loc_val, dev_val)
                        score = res["risk_score"]
                        status = res["status"]
                        
                        from services.ioc_detector import check_and_trigger_ioc_alert
                        background_tasks.add_task(
                            check_and_trigger_ioc_alert,
                            "Fraud", f"${amount_val} @ {loc_val}",
                            current_user.get("email", "anonymous@sentrax.ai")
                        )
                        
                        if status == "HIGH RISK":
                            high_risk_count += 1
                        elif status == "MEDIUM RISK":
                            medium_risk_count += 1
                        else:
                            low_risk_count += 1
                        
                        # Reconstruct the row with appended columns
                        new_row = dict(row)
                        new_row["Risk Score"] = score
                        new_row["Status"] = status
                        new_row["Scan Time"] = scan_time_str
                        records.append(new_row)
                    
                    if high_risk_count > 0:
                        threat_level = "HIGH"
                    elif medium_risk_count > 0:
                        threat_level = "MEDIUM"
                    else:
                        threat_level = "LOW"
                        
                    result_summary = f"Total Records: {total_records} | High Risk: {high_risk_count} | Medium Risk: {medium_risk_count} | Low Risk: {low_risk_count}"
                
                # 2. URL Dataset
                elif "url" in cols_lower:
                    ds_type = "URL Dataset"
                    ds_mod = "URL Intelligence"
                    scan_type = "URL"
                    
                    raw_rows = list(reader)
                    total_records = len(raw_rows)
                    susp_cnt = 0
                    
                    for row in raw_rows:
                        url_col = col_map["url"]
                        url_val = str(row.get(url_col, "")).strip()
                        
                        res = await scan_url(url_val)
                        is_susp = res["label"] == "Fraud / Phishing"
                        status = "SUSPICIOUS" if is_susp else "SAFE"
                        
                        from services.ioc_detector import check_and_trigger_ioc_alert
                        background_tasks.add_task(
                            check_and_trigger_ioc_alert,
                            "URL", url_val,
                            current_user.get("email", "anonymous@sentrax.ai")
                        )
                        if is_susp:
                            susp_cnt += 1
                            
                        records.append({
                            "URL": url_val,
                            "Status": status,
                            "Scan Time": scan_time_str
                        })
                        
                    if susp_cnt > 0:
                        threat_level = "HIGH"
                    else:
                        threat_level = "LOW"
                        
                    result_summary = f"Total URLs: {total_records} | Suspicious: {susp_cnt} | Safe: {total_records - susp_cnt}"
                
                # 3. SMS Dataset
                elif "message" in cols_lower:
                    ds_type = "SMS Dataset"
                    ds_mod = "Scam Filtering"
                    scan_type = "SMS"
                    
                    raw_rows = list(reader)
                    total_records = len(raw_rows)
                    scam_cnt = 0
                    
                    for row in raw_rows:
                        msg_col = col_map["message"]
                        msg_val = str(row.get(msg_col, "")).strip()
                        
                        res = scan_sms(msg_val)
                        is_scam = res["label"] == "Scam Message"
                        pred = "SCAM" if is_scam else "SAFE"
                        
                        from services.ioc_detector import check_and_trigger_ioc_alert
                        background_tasks.add_task(
                            check_and_trigger_ioc_alert,
                            "SMS", msg_val,
                            current_user.get("email", "anonymous@sentrax.ai")
                        )
                        if is_scam:
                            scam_cnt += 1
                            
                        records.append({
                            "Message": msg_val,
                            "Prediction": pred,
                            "Scan Time": scan_time_str
                        })
                        
                    if scam_cnt > 0:
                        threat_level = "HIGH"
                    else:
                        threat_level = "LOW"
                        
                    result_summary = f"Total Messages: {total_records} | Scam: {scam_cnt} | Safe: {total_records - scam_cnt}"
                
                # 4. Employee Dataset
                elif {"employee", "login_time"}.issubset(cols_lower):
                    ds_type = "Employee Dataset"
                    ds_mod = "Employee Monitoring"
                    scan_type = "Employee"
                    
                    raw_rows = list(reader)
                    total_records = len(raw_rows)
                    susp_cnt = 0
                    
                    for row in raw_rows:
                        emp_col = col_map["employee"]
                        time_col = col_map["login_time"]
                        emp_val = str(row.get(emp_col, "")).strip()
                        time_val = str(row.get(time_col, "")).strip()
                        
                        res = scan_employee(emp_val, time_val)
                        is_susp = res["risk_level"] == "SUSPICIOUS"
                        if is_susp:
                            susp_cnt += 1
                            
                        records.append({
                            "Employee": emp_val,
                            "Risk Level": res["risk_level"],
                            "Scan Time": scan_time_str
                        })
                        
                    if susp_cnt > 0:
                        threat_level = "MEDIUM"
                    else:
                        threat_level = "LOW"
                        
                    result_summary = f"Total Logs: {total_records} | Suspicious: {susp_cnt} | Normal: {total_records - susp_cnt}"
                
                # 5. Generic CSV
                else:
                    ds_type = "Generic CSV Dataset"
                    ds_mod = "Standard Analyzer"
                    scan_type = "Generic"
                    raw_rows = list(reader)
                    for row in raw_rows:
                        new_row = dict(row)
                        new_row["Scan Time"] = scan_time_str
                        records.append(new_row)
                    
                    result_summary = f"Total Records: {len(raw_rows)}"
            else:
                ds_type = "Empty CSV"
                ds_mod = "Standard Analyzer"
                result_summary = "No columns found"
                
        except Exception as e:
            ds_type = "Error CSV"
            ds_mod = "Standard Analyzer"
            result_summary = f"Error: {str(e)}"

    elif file_name.endswith('.txt'):
        try:
            decoded = content.decode("utf-8", errors="ignore")
            lines = [line.strip() for line in decoded.splitlines() if line.strip()]
            
            ds_type = "SMS Dataset (Plain Text)"
            ds_mod = "Scam Filtering"
            scan_type = "TXT"
            
            total_records = len(lines)
            scam_cnt = 0
            
            for line in lines:
                res = scan_sms(line)
                is_scam = res["label"] == "Scam Message"
                pred = "SCAM" if is_scam else "SAFE"
                
                from services.ioc_detector import check_and_trigger_ioc_alert
                background_tasks.add_task(
                    check_and_trigger_ioc_alert,
                    "SMS", line,
                    current_user.get("email", "anonymous@sentrax.ai")
                )
                if is_scam:
                    scam_cnt += 1
                    
                records.append({
                    "Message": line,
                    "Prediction": pred,
                    "Scan Time": scan_time_str
                })
                
            if scam_cnt > 0:
                threat_level = "HIGH"
            else:
                threat_level = "LOW"
                
            result_summary = f"Total Lines: {total_records} | Scam: {scam_cnt} | Safe: {total_records - scam_cnt}"
        except Exception as e:
            ds_type = "Error TXT"
            ds_mod = "Standard Analyzer"
            result_summary = f"Error: {str(e)}"

    elif file_name.endswith('.pdf'):
        ds_type = "Document Dataset (PDF)"
        ds_mod = "PDF Threat Intelligence"
        scan_type = "PDF"
        
        try:
            import pypdf
            pdf_file = io.BytesIO(content)
            reader = pypdf.PdfReader(pdf_file)
            extracted = []
            for i in range(min(5, len(reader.pages))):
                text = reader.pages[i].extract_text()
                if text:
                    extracted.append(text)
            pdf_text_preview = "\n".join(extracted)
            if not pdf_text_preview.strip():
                pdf_text_preview = "[No readable text extracted from PDF]"
        except Exception:
            pdf_error_occurred = True
            
        records = [
            {"Metric": "Scan Parameter", "Value": "PDF Threat Analysis"},
            {"Metric": "File Name", "Value": file.filename},
            {"Metric": "Preview Extract Size (chars)", "Value": len(pdf_text_preview) if not pdf_error_occurred else 0}
        ]
        for row in records:
            row["Scan Time"] = scan_time_str
            
        result_summary = "PDF Threat Assessment Completed"


    return {
        "ds_type": ds_type,
        "ds_mod": ds_mod,
        "scan_type": scan_type,
        "threat_level": threat_level,
        "result_summary": result_summary,
        "show_fraud_summary": show_fraud_summary,
        "total_records": total_records,
        "high_risk_count": high_risk_count,
        "medium_risk_count": medium_risk_count,
        "low_risk_count": low_risk_count,
        "records": records,
        "pdf_text_preview": pdf_text_preview,
        "pdf_error": pdf_error_occurred
    }
