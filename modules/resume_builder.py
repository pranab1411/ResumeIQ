import os
from typing import Dict, Any, List
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from utils.logger import logger

from modules.template_engine import template_registry

def hex_to_rgb(hex_str: str) -> RGBColor:
    hex_str = hex_str.lstrip('#')
    if len(hex_str) == 6:
        r = int(hex_str[0:2], 16)
        g = int(hex_str[2:4], 16)
        b = int(hex_str[4:6], 16)
        return RGBColor(r, g, b)
    return RGBColor(79, 70, 229)

class DocxResumeGenerator:
    @staticmethod
    def generate_docx(data: Dict[str, Any], output_path: str, template_id: int = 1) -> str:
        """
        Generates a clean, professional ATS-friendly Microsoft Word resume (.docx)
        formatted according to any of the 1,000 top industry resume templates.
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        doc = Document()

        template = template_registry.get_template_by_id(template_id) or template_registry.get_template_by_id(1)
        font_name = template.get("font_family", "Calibri")
        primary_hex = template.get("primary_color", "#4F46E5")
        
        PRIMARY_COLOR = hex_to_rgb(primary_hex)
        DARK_TEXT = RGBColor(30, 41, 59)       # Slate (#1E293B)
        MUTED_TEXT = RGBColor(100, 116, 139)   # Muted (#64748B)

        header_align = WD_ALIGN_PARAGRAPH.CENTER if template.get("header_align") == "center" else WD_ALIGN_PARAGRAPH.LEFT

        # Page Setup: 0.75 inch margins
        sections = doc.sections
        for section in sections:
            section.top_margin = Inches(0.75)
            section.bottom_margin = Inches(0.75)
            section.left_margin = Inches(0.75)
            section.right_margin = Inches(0.75)

        # 1. CANDIDATE NAME (HEADER)
        name = data.get("candidate_name", "CANDIDATE NAME").upper()
        p_name = doc.add_paragraph()
        p_name.alignment = header_align
        run_name = p_name.add_run(name)
        run_name.font.name = font_name
        run_name.font.size = Pt(22)
        run_name.font.bold = True
        run_name.font.color.rgb = PRIMARY_COLOR

        # 2. CONTACT INFO LINE
        email = data.get("email", "")
        phone = data.get("phone", "")
        linkedin = data.get("linkedin", "linkedin.com/in/profile")
        github = data.get("github", "github.com/profile")

        contact_parts = [p for p in [phone, email, linkedin, github] if p and p != "Not Found"]
        contact_str = "  |  ".join(contact_parts) if contact_parts else "Email | Phone | LinkedIn | GitHub"

        p_contact = doc.add_paragraph()
        p_contact.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run_contact = p_contact.add_run(contact_str)
        run_contact.font.name = font_name
        run_contact.font.size = Pt(9.5)
        run_contact.font.color.rgb = MUTED_TEXT
        p_contact.paragraph_format.space_after = Pt(14)

        def add_heading(text: str):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(12)
            p.paragraph_format.space_after = Pt(4)
            run = p.add_run(text.upper())
            run.font.name = font_name
            run.font.size = Pt(13)
            run.font.bold = True
            run.font.color.rgb = PRIMARY_COLOR
            return p

        def add_bullet(bold_prefix: str, text: str):
            p = doc.add_paragraph(style='List Bullet')
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = 1.15
            
            if bold_prefix:
                run_b = p.add_run(bold_prefix + " ")
                run_b.font.name = font_name
                run_b.font.size = Pt(10.5)
                run_b.font.bold = True
                run_b.font.color.rgb = DARK_TEXT

            run_t = p.add_run(text)
            run_t.font.name = font_name
            run_t.font.size = Pt(10.5)
            run_t.font.color.rgb = DARK_TEXT
            return p

        # 3. PROFESSIONAL SUMMARY / CAREER OBJECTIVE
        summary = data.get("summary") or data.get("objective", "")
        if summary:
            is_fresher = data.get("mode") == "fresher"
            add_heading("CAREER OBJECTIVE" if is_fresher else "PROFESSIONAL SUMMARY")
            p_sum = doc.add_paragraph()
            p_sum.paragraph_format.space_after = Pt(8)
            p_sum.paragraph_format.line_spacing = 1.15
            run_sum = p_sum.add_run(summary)
            run_sum.font.name = "Calibri"
            run_sum.font.size = Pt(10.5)
            run_sum.font.color.rgb = DARK_TEXT

        # 4. TECHNICAL SKILLS
        skills = data.get("skills", {})
        if isinstance(skills, dict) and skills:
            add_heading("TECHNICAL SKILLS")
            for category, skill_list in skills.items():
                if isinstance(skill_list, list):
                    skill_str = ", ".join(skill_list)
                else:
                    skill_str = str(skill_list)
                add_bullet(f"{category}:", skill_str)
        elif isinstance(skills, list) and skills:
            add_heading("TECHNICAL SKILLS")
            add_bullet("Core Competencies:", ", ".join(skills))

        # 5. PROFESSIONAL EXPERIENCE / PROJECTS
        experience = data.get("experience", [])
        if experience:
            add_heading("WORK EXPERIENCE")
            for item in experience:
                title = item.get("title", "Role Title")
                company = item.get("company", "Company Name")
                dates = item.get("dates", "Dates")
                
                p_exp = doc.add_paragraph()
                p_exp.paragraph_format.space_before = Pt(6)
                p_exp.paragraph_format.space_after = Pt(2)
                
                run_t = p_exp.add_run(f"{title} — {company}")
                run_t.font.name = "Calibri"
                run_t.font.size = Pt(11)
                run_t.font.bold = True
                run_t.font.color.rgb = DARK_TEXT

                if dates:
                    run_d = p_exp.add_run(f" ({dates})")
                    run_d.font.name = "Calibri"
                    run_d.font.size = Pt(10)
                    run_d.font.italic = True
                    run_d.font.color.rgb = MUTED_TEXT

                for bullet in item.get("bullets", []):
                    add_bullet("", bullet)

        # 6. PROJECTS (Fresher or Featured)
        projects = data.get("projects", [])
        if projects:
            add_heading("KEY PROJECTS")
            for proj in projects:
                pname = proj.get("name", "Project Title")
                tech = proj.get("tech_stack", "")
                link = proj.get("link", "")

                p_proj = doc.add_paragraph()
                p_proj.paragraph_format.space_before = Pt(6)
                p_proj.paragraph_format.space_after = Pt(2)

                run_p = p_proj.add_run(pname)
                run_p.font.name = "Calibri"
                run_p.font.size = Pt(11)
                run_p.font.bold = True
                run_p.font.color.rgb = DARK_TEXT

                if tech:
                    run_tech = p_proj.add_run(f" | {tech}")
                    run_tech.font.name = "Calibri"
                    run_tech.font.size = Pt(10)
                    run_tech.font.italic = True
                    run_tech.font.color.rgb = MUTED_TEXT

                if link:
                    run_l = p_proj.add_run(f" [{link}]")
                    run_l.font.name = "Calibri"
                    run_l.font.size = Pt(9.5)
                    run_l.font.color.rgb = PRIMARY_COLOR

                for bullet in proj.get("bullets", []):
                    add_bullet("", bullet)

        # 7. EDUCATION
        education = data.get("education", [])
        if education:
            add_heading("EDUCATION")
            for edu in education:
                degree = edu.get("degree", "Degree")
                institution = edu.get("institution", "University")
                year = edu.get("year", "")
                gpa = edu.get("gpa", "")

                p_edu = doc.add_paragraph()
                p_edu.paragraph_format.space_before = Pt(4)
                p_edu.paragraph_format.space_after = Pt(2)

                run_ed = p_edu.add_run(f"{degree} — {institution}")
                run_ed.font.name = "Calibri"
                run_ed.font.size = Pt(10.5)
                run_ed.font.bold = True
                run_ed.font.color.rgb = DARK_TEXT

                extra = []
                if year: extra.append(f"Graduation: {year}")
                if gpa: extra.append(f"GPA/Score: {gpa}")
                if extra:
                    run_ext = p_edu.add_run(f" ({' | '.join(extra)})")
                    run_ext.font.name = "Calibri"
                    run_ext.font.size = Pt(10)
                    run_ext.font.color.rgb = MUTED_TEXT

        # 8. CERTIFICATIONS
        certs = data.get("certifications", [])
        if certs:
            add_heading("CERTIFICATIONS & ACHIEVEMENTS")
            for cert in certs:
                add_bullet("•", cert)

        doc.save(output_path)
        logger.info(f"Generated optimized Word resume at: {output_path}")
        return output_path
