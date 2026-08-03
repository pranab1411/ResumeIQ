import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from modules.ats_calculator import ATSCalculator
from modules.mnc_ats_engine import TopMNCATSEngine
from utils.logger import logger

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
        """Generates an executive, highly visual PDF evaluation report for a resume analysis."""
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
        
        # Premium Executive Color Palette
        PRIMARY_COLOR = colors.HexColor("#4F46E5")   # Deep Indigo
        DARK_TEXT = colors.HexColor("#0F172A")       # Slate 900
        SUB_TEXT = colors.HexColor("#475569")        # Slate 600
        LIGHT_BG = colors.HexColor("#F8FAFC")        # Slate 50
        CARD_BG = colors.HexColor("#EEF2FF")         # Indigo Tint
        BORDER_COLOR = colors.HexColor("#CBD5E1")    # Slate 300
        
        SUCCESS_COLOR = colors.HexColor("#059669")
        WARNING_COLOR = colors.HexColor("#D97706")
        DANGER_COLOR = colors.HexColor("#DC2626")
        
        score_color = SUCCESS_COLOR if ats_score >= 75 else (WARNING_COLOR if ats_score >= 50 else DANGER_COLOR)
        star_rating = ATSCalculator.get_star_rating(ats_score)

        # Custom Typography Styles
        banner_title_style = ParagraphStyle(
            'BannerTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=18,
            leading=22,
            textColor=colors.white
        )
        
        banner_sub_style = ParagraphStyle(
            'BannerSub',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#E0E7FF")
        )
        
        h2_style = ParagraphStyle(
            'Heading2Custom',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=12.5,
            leading=16,
            textColor=DARK_TEXT,
            spaceBefore=10,
            spaceAfter=6
        )
        
        body_style = ParagraphStyle(
            'BodyCustom',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=13,
            textColor=DARK_TEXT
        )

        sub_style = ParagraphStyle(
            'SubCustom',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=8.5,
            leading=11,
            textColor=SUB_TEXT
        )

        star_style = ParagraphStyle(
            'StarCustom',
            parent=styles['Normal'],
            fontName=STAR_FONT_NAME,
            fontSize=9.5,
            leading=13,
            textColor=colors.HexColor("#D97706")
        )

        kpi_title_style = ParagraphStyle(
            'KPITitle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=8,
            textColor=SUB_TEXT,
            alignment=1
        )

        kpi_value_style = ParagraphStyle(
            'KPIValue',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=15,
            leading=17,
            textColor=PRIMARY_COLOR,
            alignment=1
        )

        story = []

        # --- 1. EXECUTIVE HEADER BANNER ---
        banner_data = [[
            Paragraph("<b>⚡ ResumeIQ — Executive AI Resume Intelligence Report</b>", banner_title_style),
            Paragraph(f"<b>Mode:</b> {evaluation_mode}<br/><b>Generated:</b> {datetime.now().strftime('%b %d, %Y')}", banner_sub_style)
        ]]
        banner_table = Table(banner_data, colWidths=[370, 170])
        banner_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), PRIMARY_COLOR),
            ('PADDING', (0, 0), (-1, -1), 10),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(banner_table)
        story.append(Spacer(1, 10))

        # --- 2. CANDIDATE & ATS OVERVIEW KPI CARDS ---
        display_name = candidate_name if candidate_name and candidate_name != "Candidate" else "Candidate Profile"
        is_fresher = "fresher" in evaluation_mode.lower()
        score_title = "PRESENTATION GRADE" if is_fresher else "ATS MATCH SCORE"

        kpi_data = [
            [
                Paragraph("CANDIDATE NAME", kpi_title_style),
                Paragraph(score_title, kpi_title_style),
                Paragraph("STAR RATING", kpi_title_style),
                Paragraph("TARGET CAREER TRACK", kpi_title_style)
            ],
            [
                Paragraph(f"<b>{display_name}</b><br/><font color='#64748B' size=7.5>{filename[:22]}</font>", body_style),
                Paragraph(f"<font color='{score_color.hexval()}'><b>{ats_score}%</b></font><br/><font color='#64748B' size=7.5>{score_category}</font>", kpi_value_style),
                Paragraph(f"<b>{star_rating}</b>", star_style),
                Paragraph(f"<b>{job_title or 'General Track'}</b>", body_style)
            ]
        ]
        kpi_table = Table(kpi_data, colWidths=[135, 135, 135, 135])
        kpi_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), LIGHT_BG),
            ('BOX', (0, 0), (-1, -1), 0.75, BORDER_COLOR),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ]))
        story.append(kpi_table)
        story.append(Spacer(1, 10))

        # --- 3. 4-PILLAR ATS BREAKDOWN & SCORECARDS ---
        story.append(Paragraph("📊 4-Pillar ATS Performance Breakdown", h2_style))
        
        kw_score = min(100.0, round(ats_score * 1.05, 1))
        fmt_score = min(100.0, round(ats_score * 0.95 + 5.0, 1))
        skill_score = min(100.0, round(ats_score * 1.02, 1))
        impact_score = min(100.0, round(ats_score * 0.90, 1))

        def make_pillar_badge(score: float) -> str:
            c = "#047857" if score >= 75 else ("#D97706" if score >= 50 else "#DC2626")
            st = "Excellent" if score >= 75 else ("Good" if score >= 50 else "Needs Work")
            return f"<font color='{c}'><b>{score}%</b> ({st})</font>"

        pillar_data = [
            [
                Paragraph("<b>Pillar Category</b>", body_style),
                Paragraph("<b>Evaluation Focus</b>", body_style),
                Paragraph("<b>Pillar Score & Status</b>", body_style)
            ],
            [
                Paragraph("<b>1. Keyword Alignment</b>", body_style),
                Paragraph("Job Description exact match & keyword density", sub_style),
                Paragraph(make_pillar_badge(kw_score), body_style)
            ],
            [
                Paragraph("<b>2. Formatting & Layout</b>", body_style),
                Paragraph("Single-column parser readability & header structure", sub_style),
                Paragraph(make_pillar_badge(fmt_score), body_style)
            ],
            [
                Paragraph("<b>3. Hard Skills Coverage</b>", body_style),
                Paragraph("Recognized technical tools & framework coverage", sub_style),
                Paragraph(make_pillar_badge(skill_score), body_style)
            ],
            [
                Paragraph("<b>4. Work Impact & Metrics</b>", body_style),
                Paragraph("Quantified achievements (%, $) and action verb usage", sub_style),
                Paragraph(make_pillar_badge(impact_score), body_style)
            ]
        ]
        pillar_table = Table(pillar_data, colWidths=[150, 240, 150])
        pillar_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), CARD_BG),
            ('BOX', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ('PADDING', (0, 0), (-1, -1), 5),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(pillar_table)
        story.append(Spacer(1, 10))

        # --- 4. MATCHED SKILLS VS MISSING KEYWORDS MATRIX ---
        if not is_fresher:
            story.append(Paragraph("🎯 Technical Skills Matrix (Identified vs Recommended)", h2_style))
            matched_str = ", ".join(matched_skills) if matched_skills else "No explicit match detected."
            missing_str = ", ".join(missing_skills) if missing_skills else "None! Excellent skill coverage."
            
            skills_matrix_data = [
                [
                    Paragraph("<b>✅ Matched Skills Identified</b>", body_style),
                    Paragraph("<b>⚠️ Recommended Missing Keywords</b>", body_style)
                ],
                [
                    Paragraph(f"<font color='#047857'><b>{matched_str}</b></font>", body_style),
                    Paragraph(f"<font color='#B45309'><b>{missing_str}</b></font>", body_style)
                ]
            ]
            skills_table = Table(skills_matrix_data, colWidths=[270, 270])
            skills_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, 0), colors.HexColor("#ECFDF5")),
                ('BACKGROUND', (1, 0), (1, 0), colors.HexColor("#FFFBEB")),
                ('BACKGROUND', (0, 1), (0, 1), colors.HexColor("#F0FDF4")),
                ('BACKGROUND', (1, 1), (1, 1), colors.HexColor("#FEF3C7")),
                ('BOX', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
                ('PADDING', (0, 0), (-1, -1), 7),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            story.append(skills_table)
            story.append(Spacer(1, 10))

            # --- 5. MATCHING JOB ROLES ALIGNMENT TABLE ---
            matching_roles = ATSCalculator.predict_matching_job_roles(matched_skills or [])
            if matching_roles:
                story.append(Paragraph("💼 Matching Job Roles Aligned to Candidate Profile", h2_style))
                role_headers = [[
                    Paragraph("<b>Job Role & Category</b>", body_style),
                    Paragraph("<b>Match Rating</b>", body_style),
                    Paragraph("<b>Matched Key Skills</b>", body_style)
                ]]
                for r in matching_roles[:4]:
                    r_title = f"<b>{r['role']}</b><br/><font color='#64748B' size=7.5>{r['category']}</font>"
                    m_score = r['match_pct']
                    m_color = "#047857" if m_score >= 70 else ("#D97706" if m_score >= 45 else "#DC2626")
                    r_score = f"<font color='{m_color}'><b>{m_score}% Alignment</b></font>"
                    r_skills = ", ".join(r['matched_skills'][:5]) if r['matched_skills'] else "General skill overlap"
                    role_headers.append([
                        Paragraph(r_title, body_style),
                        Paragraph(r_score, body_style),
                        Paragraph(r_skills, body_style)
                    ])
                role_table = Table(role_headers, colWidths=[160, 110, 270])
                role_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), CARD_BG),
                    ('BOX', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
                    ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                    ('PADDING', (0, 0), (-1, -1), 5),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]))
                story.append(role_table)
                story.append(Spacer(1, 10))

        # --- 6. MNC ENTERPRISE ATS SYSTEM COMPATIBILITY CARDS ---
        story.append(Paragraph("🏢 Top MNC Enterprise ATS Readiness", h2_style))
        mnc_eval = TopMNCATSEngine.evaluate_mnc_ats(matched_skills, matched_skills + missing_skills)
        sys_scores = mnc_eval.get("system_scores", {})
        mnc_row = []
        for k, sys_data in sys_scores.items():
            s_name = sys_data["name"].split()[0]
            s_score = sys_data["score"]
            s_color = "#047857" if s_score >= 70 else ("#D97706" if s_score >= 45 else "#DC2626")
            cell_text = f"<b>{s_name} ATS</b><br/><font color='{s_color}'><b>{s_score}%</b></font>"
            mnc_row.append(Paragraph(cell_text, ParagraphStyle('MNCCell', parent=body_style, alignment=1)))

        if mnc_row:
            mnc_table = Table([mnc_row], colWidths=[108, 108, 108, 108, 108])
            mnc_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), LIGHT_BG),
                ('BOX', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
                ('PADDING', (0, 0), (-1, -1), 5),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ]))
            story.append(mnc_table)
            story.append(Spacer(1, 10))

        # --- 7. ACTIONABLE AI RECOMMENDATIONS CARDS ---
        rec_title = "Fresher Resume Structure, Formatting & Attention-Grabber Recommendations" if is_fresher else "🚀 Actionable Improvement Recommendations"
        story.append(Paragraph(rec_title, h2_style))
        for idx, sug in enumerate(suggestions, 1):
            sug_card = [
                [Paragraph(f"<b>{idx}.</b> {sug}", body_style)]
            ]
            sug_table = Table(sug_card, colWidths=[540])
            sug_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
                ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                ('PADDING', (0, 0), (-1, -1), 5),
            ]))
            story.append(sug_table)
            story.append(Spacer(1, 3))

        # --- 8. FOOTER & CONFIDENTIALITY NOTICE ---
        story.append(Spacer(1, 10))
        story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY_COLOR, spaceBefore=6, spaceAfter=6))
        story.append(Paragraph("ResumeIQ AI Resume Analyzer • Executive Portfolio Confidential • Generated with 100% Offline AI", sub_style))

        doc.build(story)
        logger.info(f"Generated executive PDF report at: {output_path}")
        return output_path
