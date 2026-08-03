"""
Feature 14: Cover Letter Generator for ResumeIQ.
Auto-generates professional, ATS-friendly cover letters as .docx files.
"""

import os
from typing import Dict
from utils.logger import logger
from utils.paths import get_data_path

COVER_LETTER_TEMPLATE = """{candidate_name}
{email} | {phone}

{date}

Hiring Manager
{company_name}

Dear Hiring Manager,

I am writing to express my strong interest in the {job_title} position at {company_name}. With {years_experience} of professional experience and a proven track record of {top_achievement}, I am confident in my ability to make an immediate and lasting contribution to your team.

Throughout my career, I have developed expertise in {top_skills}. I have consistently leveraged these skills to deliver measurable results, including {quantified_result}.

What particularly excites me about {company_name} is the opportunity to work on {value_proposition}. I thrive in collaborative, fast-paced environments and am passionate about building solutions that create real business value.

I would welcome the opportunity to discuss how my background aligns with your team's goals. Thank you for your time and consideration.

Sincerely,
{candidate_name}
"""

class CoverLetterGenerator:
    """Generates tailored cover letters from resume analysis data."""

    @staticmethod
    def generate(
        candidate_name: str,
        email: str,
        phone: str,
        job_title: str,
        company_name: str,
        matched_skills: list,
        suggestions: list,
        resume_text: str = "",
        output_dir: str = None
    ) -> Dict:
        """
        Generates a .docx cover letter from resume data.
        Returns {"success": bool, "path": str, "text": str}
        """
        import re
        from datetime import datetime

        if not output_dir:
            output_dir = get_data_path("reports")
        os.makedirs(output_dir, exist_ok=True)

        # Extract years of experience from resume text
        years_experience = "several years"
        if resume_text:
            matches = re.findall(r'(\d+)\+?\s*years?', resume_text.lower())
            if matches:
                max_years = max(int(m) for m in matches if m.isdigit())
                years_experience = f"{max_years}+ years"

        # Build dynamic content
        top_skills = ", ".join(matched_skills[:4]) if matched_skills else "relevant technical skills"
        top_achievement = "delivering high-quality software solutions ahead of schedule"
        quantified_result = "improved system performance by 30% and reduced operational costs"
        value_proposition = "cutting-edge technology challenges and innovation"

        # Scan resume for achievements
        if resume_text:
            metrics = re.findall(r'\d+%|\$[\d,]+|\d+x', resume_text)
            if metrics:
                quantified_result = f"achievements such as {', '.join(metrics[:2])}"

        date_str = datetime.now().strftime("%B %d, %Y")
        clean_company = company_name.strip() if company_name else "your organization"

        text = COVER_LETTER_TEMPLATE.format(
            candidate_name=candidate_name,
            email=email,
            phone=phone,
            date=date_str,
            company_name=clean_company,
            job_title=job_title,
            years_experience=years_experience,
            top_achievement=top_achievement,
            top_skills=top_skills,
            quantified_result=quantified_result,
            value_proposition=value_proposition
        )

        # Write to .docx
        try:
            from docx import Document
            from docx.shared import Pt
            from docx.enum.text import WD_ALIGN_PARAGRAPH

            doc = Document()
            style = doc.styles["Normal"]
            style.font.name = "Calibri"
            style.font.size = Pt(11)

            for line in text.split("\n"):
                para = doc.add_paragraph(line)
                para.paragraph_format.space_after = Pt(0)

            safe_name = re.sub(r'[^\w]', '_', candidate_name)
            safe_job = re.sub(r'[^\w]', '_', job_title)[:20]
            filename = f"CoverLetter_{safe_name}_{safe_job}.docx"
            out_path = os.path.join(output_dir, filename)
            doc.save(out_path)

            logger.info(f"[Cover Letter] Generated: {out_path}")
            return {"success": True, "path": out_path, "text": text}

        except Exception as e:
            logger.error(f"[Cover Letter] Error generating docx: {e}")
            # Return plain text as fallback
            filename = f"CoverLetter_{candidate_name}.txt"
            out_path = os.path.join(output_dir, filename)
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(text)
            return {"success": True, "path": out_path, "text": text}
