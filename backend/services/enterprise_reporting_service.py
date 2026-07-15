"""
SentraX AI Backend — services/enterprise_reporting_service.py
Enterprise Reporting Service generating executive summaries (Top threats, SOC metrics, activity logs) in CSV, JSON, and PDF formats.
"""

from typing import Dict, Any, List
import io
import csv
import json
from database import get_connection

# Conditional imports for ReportLab to construct the PDF
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


class EnterpriseReportingService:
    """
    Service class producing enterprise cyber threat intelligence reports
    collating data from scan history, alerts, and active cases.
    """

    @staticmethod
    def get_reporting_data() -> Dict[str, Any]:
        """Collects structured activity summaries for the threat reports."""
        data = {
            "top_threats": [],
            "soc_metrics": {
                "total_scans": 0,
                "total_alerts": 0,
                "open_cases": 0,
                "critical_threats": 0
            },
            "activity_summary": {
                "daily_scans": 0,
                "weekly_scans": 0,
                "monthly_scans": 0
            }
        }

        try:
            with get_connection() as conn:
                cursor = conn.cursor()

                # Top threats list
                cursor.execute("""
                    SELECT label, COUNT(*) as cnt 
                    FROM scan_history 
                    WHERE threat_level != 'LOW'
                    GROUP BY label 
                    ORDER BY cnt DESC 
                    LIMIT 5
                """)
                for row in cursor.fetchall():
                    data["top_threats"].append({"threat": row[0], "count": row[1]})

                # SOC metrics counts
                cursor.execute("SELECT COUNT(*) FROM scan_history")
                data["soc_metrics"]["total_scans"] = cursor.fetchone()[0] or 0

                cursor.execute("SELECT COUNT(*) FROM alerts")
                data["soc_metrics"]["total_alerts"] = cursor.fetchone()[0] or 0

                cursor.execute("SELECT COUNT(*) FROM soc_cases WHERE status = 'Open' or status = 'Investigating'")
                data["soc_metrics"]["open_cases"] = cursor.fetchone()[0] or 0

                cursor.execute("SELECT COUNT(*) FROM scan_history WHERE threat_level = 'HIGH'")
                data["soc_metrics"]["critical_threats"] = cursor.fetchone()[0] or 0

                # Activity counts (simulate or pull days)
                cursor.execute("SELECT COUNT(*) FROM scan_history WHERE date(timestamp) = date('now')")
                data["activity_summary"]["daily_scans"] = cursor.fetchone()[0] or 0

                cursor.execute("SELECT COUNT(*) FROM scan_history WHERE date(timestamp) >= date('now', '-7 days')")
                data["activity_summary"]["weekly_scans"] = cursor.fetchone()[0] or 0

                cursor.execute("SELECT COUNT(*) FROM scan_history WHERE date(timestamp) >= date('now', '-30 days')")
                data["activity_summary"]["monthly_scans"] = cursor.fetchone()[0] or 0

        except Exception as e:
            print(f"Error compiling reporting metrics: {e}")

        return data

    @classmethod
    def generate_json_report(cls) -> str:
        """Produce reporting data formatted as a JSON string."""
        return json.dumps(cls.get_reporting_data(), indent=2)

    @classmethod
    def generate_csv_report(cls) -> str:
        """Produce SOC metrics formatted as a CSV string."""
        output = io.StringIO()
        writer = csv.writer(output)
        
        rep_data = cls.get_reporting_data()
        
        writer.writerow(["=== SENTRAX AI - ENTERPRISE SOC STATUS REPORT ==="])
        writer.writerow([])
        
        # SOC Metrics section
        writer.writerow(["SOC KPI Metrics"])
        writer.writerow(["Metric", "Count"])
        for k, v in rep_data["soc_metrics"].items():
            writer.writerow([k.replace("_", " ").title(), v])
        
        writer.writerow([])
        # Activity Summary
        writer.writerow(["Activity Summary"])
        writer.writerow(["Timeframe", "Scan Count"])
        for k, v in rep_data["activity_summary"].items():
            writer.writerow([k.replace("_", " ").title(), v])

        writer.writerow([])
        # Top Threats
        writer.writerow(["Top Threat Vectors"])
        writer.writerow(["Threat Label", "Incident Count"])
        for item in rep_data["top_threats"]:
            writer.writerow([item["threat"], item["count"]])

        return output.getvalue()

    @classmethod
    def generate_pdf_report(cls) -> io.BytesIO:
        """Construct a formatted Executive PDF SOC report using ReportLab."""
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
            fontSize=22,
            textColor=colors.HexColor("#00f0ff"),
            spaceAfter=15,
            alignment=1  # Centered
        )
        
        section_style = ParagraphStyle(
            'SectionStyle',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=13,
            textColor=colors.HexColor("#8be8ff"),
            spaceBefore=12,
            spaceAfter=6
        )

        body_style = ParagraphStyle(
            'BodyStyle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            textColor=colors.white,
            spaceAfter=5
        )

        story = []
        rep_data = cls.get_reporting_data()
        
        # Title
        story.append(Paragraph("<b>SENTRAX AI - EXECUTIVE SOC STATUS REPORT</b>", title_style))
        story.append(Spacer(1, 10))
        
        # Metadata
        story.append(Paragraph("<b>Document Classification:</b> CONFIDENTIAL // INTERNAL SOC", body_style))
        story.append(Spacer(1, 15))
        
        # SOC KPI table
        story.append(Paragraph("SOC KPI Indicators", section_style))
        kpi_table_data = [["Indicator KPI Parameter", "Incident Logs Count"]]
        for k, v in rep_data["soc_metrics"].items():
            kpi_table_data.append([k.replace("_", " ").title(), str(v)])
            
        t_kpi = Table(kpi_table_data, colWidths=[200, 150])
        t_kpi.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#061224")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor("#00f0ff")),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#1e293b")),
            ('BACKGROUND', (0,1), (-1,-1), colors.HexColor("#020617")),
            ('TEXTCOLOR', (0,1), (-1,-1), colors.white),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('PADDING', (0,0), (-1,-1), 5),
        ]))
        story.append(t_kpi)
        story.append(Spacer(1, 15))
        
        # Timeframe Activity
        story.append(Paragraph("Historical Activity Logs Summary", section_style))
        act_table_data = [["Timeframe Interval", "Total Scans Analyzed"]]
        for k, v in rep_data["activity_summary"].items():
            act_table_data.append([k.replace("_", " ").title(), str(v)])
            
        t_act = Table(act_table_data, colWidths=[200, 150])
        t_act.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#061224")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor("#00f0ff")),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#1e293b")),
            ('BACKGROUND', (0,1), (-1,-1), colors.HexColor("#020617")),
            ('TEXTCOLOR', (0,1), (-1,-1), colors.white),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('PADDING', (0,0), (-1,-1), 5),
        ]))
        story.append(t_act)
        story.append(Spacer(1, 15))

        # Top Threats list
        story.append(Paragraph("Identified Threat Vectors", section_style))
        threat_table_data = [["Threat Classification Label", "Total Incident Count"]]
        for item in rep_data["top_threats"]:
            threat_table_data.append([item["threat"], str(item["count"])])
            
        t_thr = Table(threat_table_data, colWidths=[200, 150])
        t_thr.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#061224")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor("#00f0ff")),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#1e293b")),
            ('BACKGROUND', (0,1), (-1,-1), colors.HexColor("#020617")),
            ('TEXTCOLOR', (0,1), (-1,-1), colors.white),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('PADDING', (0,0), (-1,-1), 5),
        ]))
        story.append(t_thr)

        doc.build(story)
        buffer.seek(0)
        return buffer
