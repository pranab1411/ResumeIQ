import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from modules.ats_calculator import ATSCalculator
from utils.logger import logger

# Try registering TrueType font for clean vector star rendering in PDF
STAR_FONT_NAME = "Helvetica-Bold"
font_candidates = [
    "C:/Windows/Fonts/seguisym.ttf",
    "C:/Windows/Fonts/segoeui.ttf",
    "C:/Windows/Fonts/arial.ttf"
]
for font_path in font_candidates:
    if os.path.exists(font_path):
        try:
            pdfmetrics.registerFont(TTFont("SegoeUISym", font_path))
            STAR_FONT_NAME = "SegoeUISym"
            break
        except Exception as e:
            logger.warning(f"Could not register font {font_path}: {e}")

class PDFReportGenerator:
    @staticmethod
    def generate(
        output_path: str,
        candidate_name: str,
        filename: str,
        job_title: str,
        ats_score: float,
        score_category: str,
        matched_skills: list[str],
        missing_skills: list[str],
        suggestions: list[str],
        evaluation_mode: str = "Experienced Mode"
    ) -> str:
        """Generates a professional PDF evaluation report for a resume analysis."""
        dir_name = os.path.dirname(output_path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
        
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )
        
        styles = getSampleStyleSheet()
        
        # Color Palette
        PRIMARY_COLOR = colors.HexColor("#4F46E5") # Indigo
        SECONDARY_COLOR = colors.HexColor("#1E293B") # Dark Slate
        SUCCESS_COLOR = colors.HexColor("#059669")
        WARNING_COLOR = colors.HexColor("#D97706")
        DANGER_COLOR = colors.HexColor("#DC2626")
        
        score_color = SUCCESS_COLOR if ats_score >= 75 else (WARNING_COLOR if ats_score >= 50 else DANGER_COLOR)
        star_rating = ATSCalculator.get_star_rating(ats_score)

        # Custom Styles
        title_style = ParagraphStyle(
            'DocTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=22,
            leading=26,
            textColor=PRIMARY_COLOR
        )
        
        subtitle_style = ParagraphStyle(
            'SubTitle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            textColor=colors.HexColor("#64748B")
        )
        
        h2_style = ParagraphStyle(
            'Heading2',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=14,
            leading=18,
            textColor=SECONDARY_COLOR,
            spaceBefore=12,
            spaceAfter=6
        )
        
        body_style = ParagraphStyle(
            'BodyTextCustom',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#334155")
        )

        star_style = ParagraphStyle(
            'StarStyleCustom',
            parent=styles['Normal'],
            fontName=STAR_FONT_NAME,
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#D97706")
        )
        
        story = []
        
        # Header
        story.append(Paragraph(f"ResumeIQ — AI Evaluation Report ({evaluation_mode})", title_style))
        story.append(Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", subtitle_style))
        story.append(Spacer(1, 10))
        story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY_COLOR, spaceBefore=5, spaceAfter=15))
        
        is_fresher_mode = "fresher" in evaluation_mode.lower()
        score_label = "Presentation Grade:" if is_fresher_mode else "ATS Score:"

        # Candidate & File Info Table
        info_data = [
            [Paragraph("<b>Candidate Name:</b>", body_style), Paragraph(candidate_name, body_style),
             Paragraph("<b>Evaluation Mode:</b>", body_style), Paragraph(f"<b>{evaluation_mode}</b>", body_style)],
            [Paragraph("<b>File Name:</b>", body_style), Paragraph(filename, body_style),
             Paragraph(f"<b>{score_label}</b>", body_style), Paragraph(f"<font color='{score_color.hexval()}'><b>{ats_score}% ({score_category})</b></font>", body_style)],
            [Paragraph("<b>Star Rating:</b>", body_style), Paragraph(f"<b>{star_rating}</b>", star_style),
             Paragraph("<b>Target Role:</b>", body_style), Paragraph(job_title or "General Role", body_style)]
        ]
        info_table = Table(info_data, colWidths=[110, 160, 110, 160])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#F1F5F9")),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 15))
        
        if not is_fresher_mode:
            # Matched Skills Section
            story.append(Paragraph("Matched Skills Identified", h2_style))
            matched_text = ", ".join(matched_skills) if matched_skills else "No matching skills detected."
            story.append(Paragraph(f"<font color='#047857'><b>{matched_text}</b></font>", body_style))
            story.append(Spacer(1, 12))

            # Missing Skills Section
            story.append(Paragraph("Missing Skills (Recommended to Add)", h2_style))
            missing_text = ", ".join(missing_skills) if missing_skills else "None! Excellent coverage."
            story.append(Paragraph(f"<font color='#B45309'><b>{missing_text}</b></font>", body_style))
            story.append(Spacer(1, 15))
            
            # Matching Job Roles Section
            matching_roles = ATSCalculator.predict_matching_job_roles(matched_skills or [])
            if matching_roles:
                story.append(Paragraph("Matching Job Roles Aligned to Candidate Skills", h2_style))
                table_data = [[
                    Paragraph("<b>Job Role & Category</b>", body_style),
                    Paragraph("<b>Skill Alignment</b>", body_style),
                    Paragraph("<b>Matched Key Skills</b>", body_style)
                ]]
                for r in matching_roles[:4]:
                    r_title = f"<b>{r['role']}</b><br/><font color='#64748B' size=8>{r['category']}</font>"
                    m_score = r['match_pct']
                    m_color = "#047857" if m_score >= 70 else ("#D97706" if m_score >= 45 else "#DC2626")
                    r_score = f"<font color='{m_color}'><b>{m_score}% Match</b></font>"
                    r_skills = ", ".join(r['matched_skills'][:5]) if r['matched_skills'] else "General skill overlap"
                    table_data.append([
                        Paragraph(r_title, body_style),
                        Paragraph(r_score, body_style),
                        Paragraph(r_skills, body_style)
                    ])
                role_table = Table(table_data, colWidths=[160, 100, 280])
                role_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
                    ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                    ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                    ('PADDING', (0, 0), (-1, -1), 6),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]))
                story.append(role_table)
                story.append(Spacer(1, 15))

            # Suggestions Section
            story.append(Paragraph("Actionable Recommendations", h2_style))
        else:
            # Fresher Structural & Visual Review Header
            story.append(Paragraph("Fresher Resume Structure, Formatting & Attention-Grabber Recommendations", h2_style))

        for idx, sug in enumerate(suggestions, 1):
            story.append(Paragraph(f"<b>{idx}.</b> {sug}", body_style))
            story.append(Spacer(1, 4))

        story.append(Spacer(1, 15))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CBD5E1"), spaceBefore=10, spaceAfter=10))
        story.append(Paragraph("ResumeIQ AI Resume Analyzer • Portfolio Confidential", subtitle_style))
        
        doc.build(story)
        logger.info(f"Generated PDF report at: {output_path}")
        return output_path
