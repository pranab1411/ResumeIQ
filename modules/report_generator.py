import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from modules.ats_calculator import ATSCalculator
from modules.ats_benchmark import ATSBenchmarkEngine
from modules.mnc_ats_engine import TopMNCATSEngine
from modules.nlp_engine import nlp_engine
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
        matched_skills: List[str],
        missing_skills: List[str],
        suggestions: List[str],
        rqi: float = 80.0,
        confidence_score: float = 75.0,
        company_name: str = "",
        evaluation_mode: str = "Experienced ATS Match",
        pillar_scores: Optional[Dict[str, float]] = None,
        pillar_weights: Optional[Dict[str, float]] = None,
        resume_text: str = "",
        jd_text: str = "",
        contact_info: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> str:
        """
        Generates an executive, technically defensible PDF evaluation report for ResumeIQ.
        Provides full traceability for 4-pillar MCDA scoring, simulated enterprise ATS profiles,
        Resume Quality Index (RQI), Content Strength, and extracted evidence.
        """
        dir_name = os.path.dirname(output_path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
        
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=32,
            bottomMargin=32
        )
        
        styles = getSampleStyleSheet()
        
        # Premium Executive Color Palette
        PRIMARY_COLOR = colors.HexColor("#4F46E5")   # Deep Indigo
        DARK_TEXT = colors.HexColor("#0F172A")       # Slate 900
        SUB_TEXT = colors.HexColor("#475569")        # Slate 600
        MUTED_TEXT = colors.HexColor("#64748B")      # Slate 500
        LIGHT_BG = colors.HexColor("#F8FAFC")        # Slate 50
        CARD_BG = colors.HexColor("#EEF2FF")         # Indigo Tint
        BORDER_COLOR = colors.HexColor("#CBD5E1")    # Slate 300
        BORDER_LIGHT = colors.HexColor("#E2E8F0")    # Slate 200
        
        SUCCESS_COLOR = colors.HexColor("#059669")   # Emerald 600
        WARNING_COLOR = colors.HexColor("#D97706")   # Amber 600
        DANGER_COLOR = colors.HexColor("#DC2626")    # Red 600
        
        score_color = SUCCESS_COLOR if ats_score >= 75 else (WARNING_COLOR if ats_score >= 50 else DANGER_COLOR)

        # Custom Typography Styles
        banner_title_style = ParagraphStyle(
            'BannerTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=16,
            leading=20,
            textColor=colors.white
        )
        
        banner_sub_style = ParagraphStyle(
            'BannerSub',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=8.5,
            leading=11.5,
            textColor=colors.HexColor("#E0E7FF")
        )
        
        h2_style = ParagraphStyle(
            'Heading2Custom',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=11.5,
            leading=15,
            textColor=DARK_TEXT,
            spaceBefore=8,
            spaceAfter=4
        )
        
        body_style = ParagraphStyle(
            'BodyCustom',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=8.5,
            leading=12,
            textColor=DARK_TEXT
        )

        body_bold = ParagraphStyle(
            'BodyBold',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=8.5,
            leading=12,
            textColor=DARK_TEXT
        )

        sub_style = ParagraphStyle(
            'SubCustom',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=7.5,
            leading=10.5,
            textColor=SUB_TEXT
        )

        disclaimer_style = ParagraphStyle(
            'DisclaimerCustom',
            parent=styles['Normal'],
            fontName='Helvetica-Oblique',
            fontSize=7.5,
            leading=10,
            textColor=MUTED_TEXT
        )

        kpi_title_style = ParagraphStyle(
            'KPITitle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=7.5,
            textColor=SUB_TEXT,
            alignment=1
        )

        kpi_value_style = ParagraphStyle(
            'KPIValue',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=14,
            leading=16,
            textColor=PRIMARY_COLOR,
            alignment=1
        )

        story = []

        # ── Resolve Actual Scores & Metrics ──────────────────────────────────────
        is_fresher = "fresher" in evaluation_mode.lower()
        
        # 1. Weights
        weights = pillar_weights or ATSBenchmarkEngine.get_pillar_weights(company_name if company_name else None)
        w_skills = weights.get("skills", 0.40)
        w_keywords = weights.get("keywords", 0.25)
        w_format = weights.get("format", 0.20)
        w_exp = weights.get("experience", 0.15)

        # 2. Raw Pillar Scores
        if pillar_scores:
            s_skill = float(pillar_scores.get("skills", 0.0))
            s_kw = float(pillar_scores.get("keywords", 0.0))
            s_fmt = float(pillar_scores.get("format", 0.0))
            s_exp = float(pillar_scores.get("experience", 0.0))
        else:
            # Calculate directly from inputs
            if is_fresher:
                s_skill = min(100.0, len(matched_skills) * 20.0) if matched_skills else 50.0
                s_kw = s_skill
            else:
                total_skills_req = max(1, len(matched_skills) + len(missing_skills))
                s_skill = min(100.0, (len(matched_skills) / total_skills_req) * 100.0)
                s_kw = ATSCalculator.calculate_tf_idf_similarity(resume_text, jd_text) if resume_text and jd_text else s_skill
            
            s_fmt = ATSCalculator.calculate_hygiene_score(resume_text, contact_info) if resume_text else 80.0
            s_exp = ATSCalculator.calculate_experience_score(resume_text, jd_text) if resume_text else 80.0

        # Weighted Contributions
        c_skill = round(s_skill * w_skills, 1)
        c_kw = round(s_kw * w_keywords, 1)
        c_fmt = round(s_fmt * w_format, 1)
        c_exp = round(s_exp * w_exp, 1)

        # RQI & Content Strength
        calc_rqi = ATSBenchmarkEngine.calculate_rqi(resume_text, contact_info) if resume_text else rqi
        calc_content_strength = ATSBenchmarkEngine.calculate_confidence_score(resume_text, matched_skills, ats_score) if resume_text else confidence_score

        # Extracted Evidence Counts
        detected_verbs = []
        detected_metrics = []
        word_count = len(resume_text.split()) if resume_text else 0
        if resume_text:
            strong_verbs = ["led", "built", "developed", "architected", "designed", "launched", "optimized", "reduced", "increased", "created", "managed", "implemented", "spearheaded", "achieved"]
            text_lower = resume_text.lower()
            detected_verbs = [v.title() for v in strong_verbs if v in text_lower]
            detected_metrics = nlp_engine.extract_metrics(resume_text)

        # ── 1. EXECUTIVE HEADER BANNER ──────────────────────────────────────────
        banner_data = [[
            Paragraph("<b>ResumeIQ — Executive Resume Intelligence Report</b><br/><font size=7.5 color='#E0E7FF'>Analytical Multi-Criteria Evaluation & ATS Compatibility Analysis</font>", banner_title_style),
            Paragraph(f"<b>Mode:</b> {evaluation_mode}<br/><b>Generated:</b> {datetime.now().strftime('%b %d, %Y')}<br/><b>Engine:</b> Local Pipeline", banner_sub_style)
        ]]
        banner_table = Table(banner_data, colWidths=[360, 180])
        banner_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), PRIMARY_COLOR),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(banner_table)
        story.append(Spacer(1, 6))

        # ── 2. CANDIDATE & OVERALL EVALUATION KPI CARDS ─────────────────────────
        display_name = candidate_name if candidate_name and candidate_name != "Candidate" else "Candidate Profile"
        score_title = "PRESENTATION SCORE" if is_fresher else "ATS MATCH SCORE"

        kpi_data = [
            [
                Paragraph("CANDIDATE PROFILE", kpi_title_style),
                Paragraph(score_title, kpi_title_style),
                Paragraph("RESUME QUALITY INDEX", kpi_title_style),
                Paragraph("CONTENT STRENGTH", kpi_title_style)
            ],
            [
                Paragraph(f"<b>{display_name}</b><br/><font color='#64748B' size=7>{filename[:24]}</font>", body_style),
                Paragraph(f"<font color='{score_color.hexval()}'><b>{ats_score:.1f}/100</b></font><br/><font color='#64748B' size=7>{score_category}</font>", kpi_value_style),
                Paragraph(f"<b>{calc_rqi:.0f}/100</b><br/><font color='#64748B' size=7>Structural Quality</font>", kpi_value_style),
                Paragraph(f"<b>{calc_content_strength:.0f}/100</b><br/><font color='#64748B' size=7>Analytical Depth</font>", kpi_value_style)
            ]
        ]
        kpi_table = Table(kpi_data, colWidths=[135, 135, 135, 135])
        kpi_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), LIGHT_BG),
            ('BOX', (0, 0), (-1, -1), 0.75, BORDER_COLOR),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ('PADDING', (0, 0), (-1, -1), 5),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ]))
        story.append(kpi_table)
        story.append(Spacer(1, 6))

        # ── 3. TRACEABLE 4-PILLAR MCDA SCORING BREAKDOWN ────────────────────────
        story.append(Paragraph("4-Pillar Multi-Criteria ATS Scoring Breakdown", h2_style))

        def make_score_cell(score_val: float) -> str:
            c = "#047857" if score_val >= 75 else ("#D97706" if score_val >= 50 else "#DC2626")
            st = "Strong" if score_val >= 75 else ("Moderate" if score_val >= 50 else "Low")
            return f"<font color='{c}'><b>{score_val:.1f}/100</b> ({st})</font>"

        pillar_data = [
            [
                Paragraph("<b>Pillar Category</b>", body_bold),
                Paragraph("<b>Evaluation Dimension</b>", body_bold),
                Paragraph("<b>Raw Score</b>", body_bold),
                Paragraph("<b>Weight</b>", body_bold),
                Paragraph("<b>Contribution</b>", body_bold)
            ],
            [
                Paragraph("<b>1. Hard Skills Coverage</b>", body_style),
                Paragraph("Recognized tools & domain skills match against target requirements", sub_style),
                Paragraph(make_score_cell(s_skill), body_style),
                Paragraph(f"{w_skills:.0%}", body_style),
                Paragraph(f"<b>+{c_skill:.1f}</b>", body_style)
            ],
            [
                Paragraph("<b>2. Keyword Alignment</b>", body_style),
                Paragraph("TF-IDF cosine similarity & contextual terminology density", sub_style),
                Paragraph(make_score_cell(s_kw), body_style),
                Paragraph(f"{w_keywords:.0%}", body_style),
                Paragraph(f"<b>+{c_kw:.1f}</b>", body_style)
            ],
            [
                Paragraph("<b>3. Formatting & Structure</b>", body_style),
                Paragraph("Parser readability, section header hierarchy & contact completeness", sub_style),
                Paragraph(make_score_cell(s_fmt), body_style),
                Paragraph(f"{w_format:.0%}", body_style),
                Paragraph(f"<b>+{c_fmt:.1f}</b>", body_style)
            ],
            [
                Paragraph("<b>4. Experience Alignment</b>", body_style),
                Paragraph("Years of experience, seniority keywords & qualification match", sub_style),
                Paragraph(make_score_cell(s_exp), body_style),
                Paragraph(f"{w_exp:.0%}", body_style),
                Paragraph(f"<b>+{c_exp:.1f}</b>", body_style)
            ],
            [
                Paragraph(f"<b>COMPOSITE ATS SCORE = {ats_score:.1f} / 100</b> &nbsp;&bull;&nbsp; <i>MCDA Model: ({w_skills:.2f}&times;Skills + {w_keywords:.2f}&times;Keywords + {w_format:.2f}&times;Format + {w_exp:.2f}&times;Exp)</i>", body_bold),
                Paragraph("", body_style),
                Paragraph("", body_style),
                Paragraph("", body_style),
                Paragraph(f"<font color='{score_color.hexval()}'><b>{ats_score:.1f} / 100</b></font>", body_bold)
            ]
        ]
        pillar_table = Table(pillar_data, colWidths=[130, 185, 85, 55, 85])
        pillar_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), CARD_BG),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor("#F1F5F9")),
            ('SPAN', (0, -1), (3, -1)),
            ('BOX', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, BORDER_LIGHT),
            ('PADDING', (0, 0), (-1, -1), 3.5),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(pillar_table)
        story.append(Spacer(1, 2))
        story.append(Paragraph("Score Bands: &ge; 75/100 (Excellent / High Match)  |  50–74/100 (Average / Moderate Match)  |  &lt; 50/100 (Needs Improvement)", disclaimer_style))
        story.append(Spacer(1, 6))

        # ── 4. TECHNICAL SKILLS & EXTRACTED EVIDENCE MATRIX ──────────────────────
        if not is_fresher:
            story.append(Paragraph("Technical Skills Matrix (Identified vs Recommended)", h2_style))
            matched_str = ", ".join(matched_skills) if matched_skills else "No explicit target match detected."
            missing_str = ", ".join(missing_skills) if missing_skills else "None! Complete target skill coverage."
            
            skills_matrix_data = [
                [
                    Paragraph(f"<b>Matched Skills Identified ({len(matched_skills)})</b>", body_bold),
                    Paragraph(f"<b>Recommended Missing Keywords ({len(missing_skills)})</b>", body_bold)
                ],
                [
                    Paragraph(f"<font color='#047857'>{matched_str}</font>", body_style),
                    Paragraph(f"<font color='#B45309'>{missing_str}</font>", body_style)
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
                ('PADDING', (0, 0), (-1, -1), 4.5),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            story.append(skills_table)

            # Compact Extracted Evidence Summary
            if detected_verbs or detected_metrics or word_count > 0:
                evidence_text = f"<b>Extracted Evidence:</b> {len(detected_verbs)} Action Verbs detected &bull; {len(detected_metrics)} Quantified Metric Indicators (%, $) &bull; {word_count} Total Word Count"
                story.append(Spacer(1, 2))
                story.append(Paragraph(evidence_text, sub_style))

            story.append(Spacer(1, 6))

            # ── 5. MATCHING JOB ROLES ALIGNMENT TABLE ───────────────────────────
            matching_roles = ATSCalculator.predict_matching_job_roles(matched_skills or [])
            if matching_roles:
                story.append(Paragraph("Matching Job Roles Aligned to Candidate Profile", h2_style))
                role_headers = [[
                    Paragraph("<b>Job Role & Category</b>", body_bold),
                    Paragraph("<b>Profile Alignment</b>", body_bold),
                    Paragraph("<b>Matching Key Skills</b>", body_bold)
                ]]
                for r in matching_roles[:3]:
                    r_title = f"<b>{r['role']}</b><br/><font color='#64748B' size=7>{r['category']}</font>"
                    m_score = r['match_pct']
                    m_color = "#047857" if m_score >= 70 else ("#D97706" if m_score >= 45 else "#DC2626")
                    r_score = f"<font color='{m_color}'><b>{m_score:.1f}/100</b></font>"
                    r_skills = ", ".join(r['matched_skills'][:5]) if r['matched_skills'] else "General skill overlap"
                    role_headers.append([
                        Paragraph(r_title, body_style),
                        Paragraph(r_score, body_style),
                        Paragraph(r_skills, body_style)
                    ])
                role_table = Table(role_headers, colWidths=[150, 100, 290])
                role_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), CARD_BG),
                    ('BOX', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
                    ('INNERGRID', (0, 0), (-1, -1), 0.5, BORDER_LIGHT),
                    ('PADDING', (0, 0), (-1, -1), 3.5),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]))
                story.append(role_table)
                story.append(Spacer(1, 6))

        # ── 6. SIMULATED ENTERPRISE ATS COMPATIBILITY ───────────────────────────
        story.append(Paragraph("Simulated Enterprise ATS Compatibility", h2_style))
        mnc_eval = TopMNCATSEngine.evaluate_mnc_ats(matched_skills, matched_skills + missing_skills, resume_text, jd_text, contact_info)
        sys_scores = mnc_eval.get("system_scores", {})
        mnc_row = []
        for k, sys_data in sys_scores.items():
            s_name = sys_data["name"]
            s_score = sys_data["score"]
            s_color = "#047857" if s_score >= 70 else ("#D97706" if s_score >= 50 else "#DC2626")
            s_cat = sys_data.get("category", "Average")
            cell_text = f"<b>{s_name}</b><br/><font color='{s_color}'><b>{s_score:.1f}/100</b></font><br/><font size=6.5 color='#64748B'>{s_cat}</font>"
            mnc_row.append(Paragraph(cell_text, ParagraphStyle('MNCCell', parent=body_style, alignment=1)))

        if mnc_row:
            mnc_table = Table([mnc_row], colWidths=[108, 108, 108, 108, 108])
            mnc_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), LIGHT_BG),
                ('BOX', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
                ('PADDING', (0, 0), (-1, -1), 4),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ]))
            story.append(mnc_table)
            story.append(Spacer(1, 2))
            story.append(Paragraph(
                "Disclaimer: Scores are generated using ResumeIQ's configurable heuristic multi-criteria profiles and do not represent proprietary ATS algorithms or official evaluations of Workday, Oracle, Greenhouse, Lever, or iCIMS.",
                disclaimer_style
            ))
            story.append(Spacer(1, 6))

        # ── 7. ACTIONABLE RECOMMENDATIONS & METHODOLOGY ─────────────────────────
        rec_story = []
        rec_title = "Fresher Resume Optimization Guidelines" if is_fresher else "Actionable Improvement Recommendations"
        rec_story.append(Paragraph(rec_title, h2_style))
        for idx, sug in enumerate(suggestions[:4], 1):
            sug_card = [
                [Paragraph(f"<b>{idx}.</b> {sug}", body_style)]
            ]
            sug_table = Table(sug_card, colWidths=[540])
            sug_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), LIGHT_BG),
                ('BOX', (0, 0), (-1, -1), 0.5, BORDER_LIGHT),
                ('PADDING', (0, 0), (-1, -1), 3.5),
            ]))
            rec_story.append(sug_table)
            rec_story.append(Spacer(1, 2))

        # ── 8. METHODOLOGY & ANALYTICAL FRAMEWORK ───────────────────────────────
        rec_story.append(Spacer(1, 4))
        methodology_text = (
            "<b>Methodology & Analytical Framework:</b><br/>"
            "&bull; <b>Text Extraction:</b> Layout-aware document parsing via pdfplumber and python-docx with OCR image fallback.<br/>"
            "&bull; <b>NLP & Skill Extraction:</b> Statistical Named Entity Recognition (spaCy) combined with a 22-category curated domain taxonomy.<br/>"
            "&bull; <b>Keyword Alignment:</b> Scikit-Learn TF-IDF vectorization with cosine similarity measurement against target job description.<br/>"
            "&bull; <b>Scoring Framework:</b> Multi-Criteria Decision Analysis (MCDA) weighted model. Resume Quality Index (RQI) evaluates structural completeness.<br/>"
            "&bull; <b>Content Strength:</b> Evaluates content density, action verb richness, and quantifiable impact metrics.<br/>"
            "<i>Notice: ResumeIQ scores are analytical indicators generated by its configured evaluation models. ATS compatibility scores are simulations and should not be interpreted as proprietary ATS decisions.</i>"
        )
        methodology_table = Table([[Paragraph(methodology_text, sub_style)]], colWidths=[540])
        methodology_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ('BOX', (0, 0), (-1, -1), 0.5, BORDER_LIGHT),
            ('PADDING', (0, 0), (-1, -1), 4.5),
        ]))
        rec_story.append(methodology_table)

        # ── 9. FOOTER & CONFIDENTIALITY NOTICE ──────────────────────────────────
        rec_story.append(Spacer(1, 4))
        rec_story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY_COLOR, spaceBefore=3, spaceAfter=3))
        rec_story.append(Paragraph("ResumeIQ Executive Report &bull; Confidential &bull; Generated using ResumeIQ Local Analysis Pipeline &bull; 100% On-Device Processing", disclaimer_style))

        story.append(KeepTogether(rec_story))

        doc.build(story)
        logger.info(f"Generated executive PDF report at: {output_path}")
        return output_path

