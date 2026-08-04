"""
modules/cover_letter_generator.py
Cover Letter Generator Engine for ResumeIQ v2.0.
Supports 6 cover letter types (Generic, Company-Specific, Job-Specific,
Internship, Fresher, Experienced Professional) with AI tone matching via Gemini.
Exports to PDF and DOCX formats.
"""

import os
import re
from datetime import datetime
from typing import Dict, Any, List, Optional
from utils.logger import logger
from utils.paths import get_data_path
from utils.gemini_client import gemini_generate, gemini_available

class CoverLetterGenerator:
    TYPES = [
        "Generic",
        "Company-Specific",
        "Job-Specific",
        "Internship",
        "Fresher",
        "Experienced Professional"
    ]

    @classmethod
    def generate(
        cls,
        candidate_name: str,
        email: str,
        phone: str,
        job_title: str,
        company_name: str,
        matched_skills: List[str],
        suggestions: List[str],
        resume_text: str = "",
        output_dir: Optional[str] = None,
        letter_type: str = "Job-Specific",
        output_format: str = "docx"
    ) -> Dict[str, Any]:
        """
        Generates a tailored cover letter (DOCX or PDF).
        """
        if not output_dir:
            output_dir = get_data_path("reports")
        os.makedirs(output_dir, exist_ok=True)

        clean_company = company_name.strip() if company_name else "your organization"
        top_skills_str = ", ".join(matched_skills[:5]) if matched_skills else "key technical skills"

        # Generate text via Gemini AI or template fallback
        text = cls._generate_text(
            candidate_name=candidate_name,
            email=email,
            phone=phone,
            job_title=job_title,
            company_name=clean_company,
            top_skills_str=top_skills_str,
            resume_text=resume_text,
            letter_type=letter_type
        )

        safe_name = re.sub(r'[^\w]', '_', candidate_name)
        safe_job = re.sub(r'[^\w]', '_', job_title)[:20]

        if output_format.lower() == "pdf":
            out_path = os.path.join(output_dir, f"CoverLetter_{safe_name}_{safe_job}.pdf")
            return cls._export_pdf(text, out_path, candidate_name)
        else:
            out_path = os.path.join(output_dir, f"CoverLetter_{safe_name}_{safe_job}.docx")
            return cls._export_docx(text, out_path)

    @classmethod
    def _generate_text(
        cls,
        candidate_name: str,
        email: str,
        phone: str,
        job_title: str,
        company_name: str,
        top_skills_str: str,
        resume_text: str,
        letter_type: str
    ) -> str:
        date_str = datetime.now().strftime("%B %d, %Y")

        if gemini_available():
            try:
                prompt = (
                    f"Write a professional {letter_type} cover letter for:\n"
                    f"Candidate Name: {candidate_name}\n"
                    f"Target Position: {job_title}\n"
                    f"Target Company: {company_name}\n"
                    f"Key Skills: {top_skills_str}\n"
                    f"Format: Include header with Name, Email ({email}), Phone ({phone}), Date ({date_str}), and Salutation 'Dear Hiring Manager,'.\n"
                    f"Keep it concise, compelling, and structured in 3-4 paragraphs."
                )
                return gemini_generate(prompt, temperature=0.7, timeout=12)
            except Exception as e:
                logger.warning(f"[CoverLetterGenerator] Gemini text generation fallback: {e}")

        # Fallback template
        return f"""{candidate_name}
{email} | {phone}

{date_str}

Hiring Manager
{company_name}

Dear Hiring Manager,

I am writing to express my strong interest in the {job_title} position at {company_name}. With my background and proven expertise in {top_skills_str}, I am confident in my ability to make an immediate impact on your team as a {letter_type.lower()} candidate.

Throughout my technical experience, I have consistently applied modern industry practices to build scalable, high-performance solutions. My approach combines technical excellence with a strong drive to achieve business objectives.

I am particularly excited about the work {company_name} is doing and would welcome the opportunity to discuss how my skill set aligns with your team's goals. Thank you for your time and consideration.

Sincerely,

{candidate_name}
"""

    @staticmethod
    def _export_docx(text: str, out_path: str) -> Dict[str, Any]:
        try:
            from docx import Document
            from docx.shared import Pt
            doc = Document()
            style = doc.styles["Normal"]
            style.font.name = "Calibri"
            style.font.size = Pt(11)

            for line in text.split("\n"):
                para = doc.add_paragraph(line)
                para.paragraph_format.space_after = Pt(0)

            doc.save(out_path)
            logger.info(f"[Cover Letter] Exported DOCX: {out_path}")
            return {"success": True, "path": out_path, "text": text, "format": "docx"}
        except Exception as e:
            logger.error(f"[Cover Letter] DOCX export error: {e}")
            return {"success": False, "path": "", "text": text, "error": str(e)}

    @staticmethod
    def _export_pdf(text: str, out_path: str, candidate_name: str) -> Dict[str, Any]:
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib import colors

            doc = SimpleDocTemplate(out_path, pagesize=letter, rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54)
            styles = getSampleStyleSheet()
            p_style = ParagraphStyle('CoverText', parent=styles['Normal'], fontName='Helvetica', fontSize=10.5, leading=14, textColor=colors.HexColor('#0F172A'))

            story = []
            for line in text.split("\n"):
                if line.strip():
                    story.append(Paragraph(line.replace("&", "&amp;"), p_style))
                else:
                    story.append(Spacer(1, 6))

            doc.build(story)
            logger.info(f"[Cover Letter] Exported PDF: {out_path}")
            return {"success": True, "path": out_path, "text": text, "format": "pdf"}
        except Exception as e:
            logger.error(f"[Cover Letter] PDF export error: {e}")
            return {"success": False, "path": "", "text": text, "error": str(e)}
