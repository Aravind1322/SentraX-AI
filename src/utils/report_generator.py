import io
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_executive_pdf_report(filename, scan_type, threat_level, result_summary):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=54, rightMargin=54, topMargin=54, bottomMargin=54)
    styles = getSampleStyleSheet()
    
    # 1. Unique Report ID
    now = datetime.now()
    report_id = now.strftime("SENTRAX-%Y%m%d-%H%M%S")
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        textColor=colors.HexColor('#061224'),
        spaceAfter=5,
        alignment=1 # Center
    )

    id_style = ParagraphStyle(
        'ReportID',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        textColor=colors.HexColor('#63768f'),
        spaceAfter=20,
        alignment=1 # Center
    )
    
    section_title_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        textColor=colors.HexColor('#061224'),
        spaceBefore=15,
        spaceAfter=8
    )
    
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor('#333333'),
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'Bullet',
        parent=body_style,
        fontName='Helvetica',
        leftIndent=20,
        firstLineIndent=-10,
        spaceAfter=4
    )

    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Italic'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        textColor=colors.HexColor('#63768f'),
        alignment=1 # Center
    )

    story = []

    # Title & Report ID
    story.append(Paragraph("SENTRAX AI &ndash; EXECUTIVE THREAT REPORT", title_style))
    story.append(Paragraph(f"REPORT ID: {report_id}", id_style))
    story.append(Spacer(1, 10))

    # Threat Level Accent
    severity_color = colors.HexColor('#00ff87') # LOW
    if threat_level == "HIGH":
        severity_color = colors.HexColor('#ff3b30')
    elif threat_level == "MEDIUM":
        severity_color = colors.HexColor('#ffd60a')

    # Metadata Block Table
    metadata_data = [
        [Paragraph("<b>Report Generated:</b>", body_style), Paragraph(now.strftime("%Y-%m-%d %H:%M:%S"), body_style)],
        [Paragraph("<b>Target Filename:</b>", body_style), Paragraph(filename, body_style)],
        [Paragraph("<b>Security Scan Type:</b>", body_style), Paragraph(scan_type, body_style)],
        [Paragraph("<b>Assessed Threat Level:</b>", body_style), Paragraph(f'<font color="{severity_color.hexval()}"><b>{threat_level}</b></font>', body_style)]
    ]
    meta_table = Table(metadata_data, colWidths=[150, 350])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f4f6f9')),
        ('PADDING', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#d1d5db')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 15))

    # Threat Summary Section
    story.append(Paragraph("THREAT SUMMARY ASSESSMENT", section_title_style))
    
    parts = [p.strip() for p in result_summary.split("|")]
    summary_data = []
    for part in parts:
        if ":" in part:
            k, v = part.split(":", 1)
            summary_data.append([Paragraph(f"<b>{k.strip()}</b>", body_style), Paragraph(v.strip(), body_style)])
        else:
            summary_data.append([Paragraph(part, body_style), Paragraph("", body_style)])
            
    summary_table = Table(summary_data, colWidths=[200, 300])
    summary_table.setStyle(TableStyle([
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor('#e5e7eb')),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 15))

    # Recommendations Section
    story.append(Paragraph("RECOMMENDED ACTION PLAN", section_title_style))
    
    recs = []
    if scan_type == "Fraud":
        if threat_level == "HIGH":
            recs = ["Freeze transaction", "Conduct manual review"]
        elif threat_level == "MEDIUM":
            recs = ["Verify transaction details"]
        else:
            recs = ["Continue monitoring"]
    elif scan_type == "URL":
        if threat_level == "HIGH":
            recs = ["Block domain immediately", "Alert security team"]
        else:
            recs = ["Continue monitoring"]
    elif scan_type == "SMS":
        if threat_level == "HIGH":
            recs = ["Avoid clicking links", "Report sender"]
        else:
            recs = ["No immediate action required"]
    elif scan_type == "Employee":
        if threat_level == "MEDIUM":
            recs = ["Review login patterns", "Verify employee activity"]
        else:
            recs = ["Continue monitoring"]
    elif scan_type == "TXT":
        if threat_level == "HIGH":
            recs = ["Investigate suspicious content"]
        else:
            recs = ["No immediate action required"]

    for rec in recs:
        story.append(Paragraph(f"&bull; {rec}", bullet_style))
        
    story.append(Spacer(1, 35))

    # SentraX Branding Footer
    story.append(Paragraph("Generated by SentraX AI Threat Intelligence Platform", footer_style))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
