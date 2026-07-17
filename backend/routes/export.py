"""
SentraX AI Backend — routes/export.py
Endpoints for exporting persistent scan history data to CSV or PDF formats.
"""

from fastapi import APIRouter, Depends, BackgroundTasks
from fastapi.responses import StreamingResponse
import io
import csv
from database import get_connection, cleanup_old_history
from utils.security import get_current_user, RoleChecker
from typing import Dict, Any

# Conditional imports for ReportLab to construct the PDF
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

router = APIRouter()


@router.get("/csv", summary="Export complete scan history to CSV")
async def export_csv(
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(RoleChecker(["Security Analyst", "Administrator"]))
):
    """
    Generate and stream a CSV file containing all persistent scan records.
    """
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write headers
    writer.writerow([
        "ID", "Scan Type", "Input Data", "Risk Score", "Label/Result",
        "Threat Level", "Confidence %", "Timestamp"
    ])
    
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, scan_type, input_data, score, label, threat_level, confidence, timestamp
                FROM scan_history
                ORDER BY timestamp DESC, id DESC
            """)
            for row in cursor.fetchall():
                writer.writerow([
                    row["id"],
                    row["scan_type"],
                    row["input_data"],
                    row["score"],
                    row["label"],
                    row["threat_level"],
                    row["confidence"],
                    row["timestamp"]
                ])
    except Exception as e:
        print(f"Error generating CSV export: {e}")
        writer.writerow(["Error generating report", str(e)])

    output.seek(0)
    
    background_tasks.add_task(cleanup_old_history)
    
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=sentrax_scan_history.csv"}
    )


@router.get("/pdf", summary="Export scan history summary to PDF")
async def export_pdf(
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(RoleChecker(["Security Analyst", "Administrator"]))
):
    """
    Generate and return an Executive PDF threat report from actual database records.
    """
    background_tasks.add_task(cleanup_old_history)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    
    styles = getSampleStyleSheet()
    
    # Custom cyber styles
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        textColor=colors.HexColor("#00f0ff"),
        spaceAfter=15,
        alignment=1  # Centered
    )
    
    meta_style = ParagraphStyle(
        'MetaStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor("#a1a1a1"),
        spaceAfter=5
    )

    story = []
    
    # Title
    story.append(Paragraph("<b>SentraX AI - Executive SOC Threat Report</b>", title_style))
    story.append(Spacer(1, 10))
    
    # Metadata
    story.append(Paragraph(f"<b>Generated On:</b> {datetime_now_str()}", meta_style))
    story.append(Paragraph("<b>Classification:</b> RESTRICTED // SECURITY OPERATIONS CENTRE", meta_style))
    story.append(Spacer(1, 15))
    
    # Fetch scans
    table_data = [[
        "ID", "Type", "Input Data", "Score", "Label", "Threat Level", "Time"
    ]]
    
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            # Limit to last 100 rows to ensure doc fits and builds quickly
            cursor.execute("""
                SELECT id, scan_type, input_data, score, label, threat_level, timestamp
                FROM scan_history
                ORDER BY timestamp DESC, id DESC
                LIMIT 100
            """)
            rows = cursor.fetchall()
            
            for row in rows:
                # Truncate input data for presentation
                inp = str(row["input_data"])
                if len(inp) > 30:
                    inp = inp[:27] + "..."
                    
                table_data.append([
                    str(row["id"]),
                    str(row["scan_type"]),
                    inp,
                    str(row["score"]),
                    str(row["label"]),
                    str(row["threat_level"]),
                    str(row["timestamp"])[:16] # YYYY-MM-DD HH:MM
                ])
                
    except Exception as e:
        print(f"Error querying scan history for PDF: {e}")
        table_data.append(["Error querying data", str(e), "", "", "", "", ""])

    # Table styling
    col_widths = [30, 60, 150, 40, 90, 70, 100]
    t = Table(table_data, colWidths=col_widths)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#061224")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor("#00f0ff")),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#1e293b")),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor("#020617")),
        ('TEXTCOLOR', (0,1), (-1,-1), colors.white),
    ]))
    story.append(t)
    
    doc.build(story)
    buffer.seek(0)
    
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=sentrax_executive_report.pdf"}
    )


def datetime_now_str() -> str:
    from datetime import datetime
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
