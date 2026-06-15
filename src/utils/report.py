from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime


def generate_pdf(url, result, recommendation, filename="threat_report.pdf"):
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("<b>SentraX AI Threat Report</b>", styles["Title"]))
    story.append(Spacer(1, 20))

    story.append(Paragraph(f"<b>URL:</b> {url}", styles["Normal"]))
    story.append(Paragraph(f"<b>Threat Label:</b> {result['label']}", styles["Normal"]))
    story.append(Paragraph(f"<b>Risk Score:</b> {result['score']}/100", styles["Normal"]))
    story.append(Paragraph(f"<b>Recommendation:</b> {recommendation}", styles["Normal"]))
    story.append(
        Paragraph(
            f"<b>Timestamp:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            styles["Normal"]
        )
    )

    story.append(Spacer(1, 20))
    story.append(Paragraph("<b>Analysis Reasons:</b>", styles["Heading2"]))

    if result["reasons"]:
        for reason in result["reasons"]:
            story.append(Paragraph(f"• {reason}", styles["Normal"]))
    else:
        story.append(Paragraph("No suspicious indicators found", styles["Normal"]))

    doc.build(story)
    return filename