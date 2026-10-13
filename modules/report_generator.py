"""
report_generator.py - Generates Downloadable PDF and CSV Analysis Reports
Utilizes ReportLab for PDF reports and standard CSV module for structured tabular data.
"""

import io
import csv
from typing import Dict, Any, List
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable
)


class ReportGenerator:
    """Generates PDF and CSV audit reports from analysis results."""

    def __init__(self):
        pass

    def generate_pdf_report(
        self,
        candidate_name: str,
        job_title: str,
        ats_results: Dict[str, Any],
        match_results: Dict[str, Any],
        recommendations: List[Dict[str, Any]]
    ) -> bytes:
        """
        Build a high-quality PDF report summarizing the ATS compatibility scan.
        Returns the raw PDF bytes.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40
        )

        styles = getSampleStyleSheet()

        # Custom styles
        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=26,
            textColor=colors.HexColor("#0F172A")
        )
        subtitle_style = ParagraphStyle(
            "DocSubTitle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=11,
            leading=15,
            textColor=colors.HexColor("#64748B")
        )
        h2_style = ParagraphStyle(
            "SectionH2",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=17,
            textColor=colors.HexColor("#1E293B"),
            spaceBefore=12,
            spaceAfter=6
        )
        body_style = ParagraphStyle(
            "BodyDark",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#334155")
        )
        score_style = ParagraphStyle(
            "ScoreBig",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=28,
            leading=32,
            alignment=1,  # Center
            textColor=colors.HexColor("#4F46E5")
        )
        table_header = ParagraphStyle(
            "TableHeader",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=9,
            leading=11,
            textColor=colors.white
        )

        story = []

        # 1. Header
        story.append(Paragraph("AI Resume Analyzer – ATS Compatibility Audit", title_style))
        cand_str = candidate_name if candidate_name else "Candidate Resume"
        job_str = job_title if job_title else "Target Job Position"
        story.append(Paragraph(f"<b>Candidate:</b> {cand_str} &nbsp;|&nbsp; <b>Target Role:</b> {job_str}", subtitle_style))
        story.append(Spacer(1, 10))
        story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#4F46E5"), spaceAfter=15))

        # 2. Score Banner
        overall_score = ats_results.get("overall_score", 0)
        rating_label = ats_results.get("rating", {}).get("label", "Compatibility Match")
        score_text = f"{overall_score} / 100"

        score_data = [
            [
                Paragraph("<b>ATS Compatibility Score</b>", subtitle_style),
                Paragraph(f"<b>Rating:</b> {rating_label}", subtitle_style)
            ],
            [
                Paragraph(score_text, score_style),
                Paragraph(ats_results.get("rating", {}).get("summary", ""), body_style)
            ]
        ]
        score_table = Table(score_data, colWidths=[200, 330])
        score_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F1F5F9")),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('PADDING', (0, 0), (-1, -1), 10),
        ]))
        story.append(score_table)
        story.append(Spacer(1, 15))

        # 3. Component Breakdown Table
        story.append(Paragraph("Pillar Breakdown & Scoring Formula", h2_style))
        breakdown_rows = [
            [
                Paragraph("<b>Component</b>", table_header),
                Paragraph("<b>Raw Score</b>", table_header),
                Paragraph("<b>Weight</b>", table_header),
                Paragraph("<b>Weighted Value</b>", table_header)
            ]
        ]

        for k, v in ats_results.get("breakdown", {}).items():
            breakdown_rows.append([
                Paragraph(v.get("name", k), body_style),
                Paragraph(f"{v.get('raw_score', 0)}%", body_style),
                Paragraph(f"{v.get('weight', 0)}%", body_style),
                Paragraph(f"+{v.get('weighted_score', 0)} pts", body_style)
            ])

        b_table = Table(breakdown_rows, colWidths=[200, 100, 100, 130])
        b_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#4F46E5")),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ]))
        story.append(b_table)
        story.append(Spacer(1, 15))

        # 4. Skill Gap Overview
        story.append(Paragraph("Skills Analysis", h2_style))
        matched_str = ", ".join(match_results.get("matched_skills", [])) or "None identified"
        missing_str = ", ".join(match_results.get("missing_skills", [])) or "None (100% matched)"

        skill_summary_data = [
            [Paragraph("<b>Status</b>", table_header), Paragraph("<b>Skills Identified</b>", table_header)],
            [
                Paragraph(f"<font color='#059669'><b>Matched ({len(match_results.get('matched_skills', []))})</b></font>", body_style),
                Paragraph(matched_str, body_style)
            ],
            [
                Paragraph(f"<font color='#DC2626'><b>Missing ({len(match_results.get('missing_skills', []))})</b></font>", body_style),
                Paragraph(missing_str, body_style)
            ]
        ]
        s_table = Table(skill_summary_data, colWidths=[120, 410])
        s_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E293B")),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ('PADDING', (0, 0), (-1, -1), 7),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(s_table)
        story.append(Spacer(1, 15))

        # 5. Top Priority Action Items
        story.append(Paragraph("Priority Action Checklist", h2_style))
        rec_rows = [
            [Paragraph("<b>Priority</b>", table_header), Paragraph("<b>Recommendation & Actionable Step</b>", table_header)]
        ]

        for rec in recommendations[:5]:
            p_color = "#DC2626" if rec["priority"] == "High" else "#D97706" if rec["priority"] == "Medium" else "#059669"
            rec_content = f"<b>{rec['title']}</b><br/>{rec['description']}<br/><i>Action:</i> {rec['action']}"
            rec_rows.append([
                Paragraph(f"<font color='{p_color}'><b>{rec['priority']}</b></font>", body_style),
                Paragraph(rec_content, body_style)
            ])

        if len(rec_rows) > 1:
            r_table = Table(rec_rows, colWidths=[90, 440])
            r_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#334155")),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ('PADDING', (0, 0), (-1, -1), 6),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
            ]))
            story.append(r_table)

        # 6. Disclaimer
        story.append(Spacer(1, 15))
        disclaimer_style = ParagraphStyle(
            "Disc",
            parent=styles["Normal"],
            fontName="Helvetica-Oblique",
            fontSize=7.5,
            leading=10,
            textColor=colors.HexColor("#94A3B8")
        )
        story.append(Paragraph(ats_results.get("disclaimer", ""), disclaimer_style))

        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes

    def generate_csv_report(
        self,
        match_results: Dict[str, Any],
        recommendations: List[Dict[str, Any]]
    ) -> str:
        """Generate CSV string containing skills breakdown and recommendations."""
        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow(["Section", "Item / Skill", "Status", "Details"])

        # Matched skills
        for skill in match_results.get("matched_skills", []):
            writer.writerow(["Skill Matching", skill, "Matched", "Found in both resume and job description"])

        # Missing skills
        for skill in match_results.get("missing_skills", []):
            writer.writerow(["Skill Matching", skill, "Missing", "Required in job description but not detected in resume"])

        # Additional skills
        for skill in match_results.get("additional_skills", []):
            writer.writerow(["Skill Matching", skill, "Additional", "Present in resume; not explicitly requested in JD"])

        # Recommendations
        for rec in recommendations:
            writer.writerow(["Action Item", rec.get("title", ""), rec.get("priority", ""), rec.get("action", "")])

        return output.getvalue()
