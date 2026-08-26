"""
modules/parser.py
Unified Document Parser Engine for ResumeIQ v2.0.
Supports PDF, DOCX, TXT, RTF, ODT, HTML, LinkedIn PDF Export, and Europass CV.
Outputs a structured ResumeData dataclass.
"""

import os
import re
from typing import Dict, Any, List, Optional
from utils.logger import logger
from modules.resume_data import ResumeData
from modules.parsers import detect_resume_format
from modules.parsers.pdf_parser import parse_pdf
from modules.parsers.docx_parser import parse_docx
from modules.parsers.txt_parser import parse_txt
from modules.parsers.rtf_parser import parse_rtf
from modules.parsers.odt_parser import parse_odt
from modules.parsers.html_parser import parse_html
from modules.parsers.linkedin_parser import parse_linkedin_pdf
from modules.parsers.europass_parser import parse_europass

class DocumentParser:
    @staticmethod
    def extract_text(file_path: str) -> str:
        """Extracts plain text from any supported resume file format."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found at path: {file_path}")
            
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == ".pdf":
            return parse_pdf(file_path)
        elif ext in [".docx", ".doc"]:
            return parse_docx(file_path)
        elif ext == ".txt":
            return parse_txt(file_path)
        elif ext == ".rtf":
            return parse_rtf(file_path)
        elif ext == ".odt":
            return parse_odt(file_path)
        elif ext in [".html", ".htm"]:
            return parse_html(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}. Supported formats: PDF, DOCX, TXT, RTF, ODT, HTML.")

    @classmethod
    def parse_to_resume_data(cls, file_path: str) -> ResumeData:
        """
        Parses resume file into a structured ResumeData dataclass.
        """
        raw_text = cls.extract_text(file_path)
        fmt, is_linkedin, is_europass = detect_resume_format(raw_text, file_path)
        
        # Use NLP Engine to extract fields if available
        try:
            from modules.nlp_engine import nlp_engine
            extracted_name = nlp_engine.extract_candidate_name(raw_text)
            extracted_role = nlp_engine.extract_target_role(raw_text)
            extracted_skills = nlp_engine.extract_skills(raw_text)
            extracted_contact = nlp_engine.extract_contact_info(raw_text)
        except Exception as e:
            logger.warning(f"[DocumentParser] NLP engine extraction fallback: {e}")
            extracted_name = "Name not confidently detected"
            extracted_role = "General Position"
            extracted_skills = []
            extracted_contact = {}
            
        # Parse extra fields via regex patterns
        email = extracted_contact.get("email", cls._extract_email(raw_text))
        phone = extracted_contact.get("phone", cls._extract_phone(raw_text))
        linkedin = extracted_contact.get("linkedin", cls._extract_linkedin(raw_text))
        github = extracted_contact.get("github", cls._extract_github(raw_text))
        portfolio = cls._extract_url_pattern(raw_text, r'https?://(?:www\.)?(?:portfolio|behance|dribbble|devpost)[^\s]+')
        website = cls._extract_url_pattern(raw_text, r'https?://[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,}(?:/[^\s]*)?')
        
        sections = cls._extract_sections(raw_text)
        
        return ResumeData(
            candidate_name=extracted_name,
            target_role=extracted_role,
            email=email,
            phone=phone,
            linkedin=linkedin,
            github=github,
            portfolio=portfolio,
            website=website,
            skills=extracted_skills,
            education=sections.get("education", []),
            experience=sections.get("experience", []),
            certifications=sections.get("certifications", []),
            projects=sections.get("projects", []),
            publications=sections.get("publications", []),
            awards=sections.get("awards", []),
            volunteer=sections.get("volunteer", []),
            interests=sections.get("interests", []),
            achievements=sections.get("achievements", []),
            languages=sections.get("languages", []),
            raw_text=raw_text,
            file_format=fmt,
            file_path=file_path,
            is_linkedin_export=is_linkedin,
            is_europass=is_europass
        )

    @staticmethod
    def _extract_email(text: str) -> str:
        m = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
        return m.group(0) if m else "Not Found"

    @staticmethod
    def _extract_phone(text: str) -> str:
        m = re.search(r'[\+\(]?\d[\d\s\-\(\)]{8,}\d', text)
        return m.group(0).strip() if m else "Not Found"

    @staticmethod
    def _extract_linkedin(text: str) -> str:
        m = re.search(r'(?:https?://)?(?:www\.)?linkedin\.com/in/[a-zA-Z0-9\-_]+', text, re.IGNORECASE)
        return m.group(0) if m else "Not Found"

    @staticmethod
    def _extract_github(text: str) -> str:
        m = re.search(r'(?:https?://)?(?:www\.)?github\.com/[a-zA-Z0-9\-_]+', text, re.IGNORECASE)
        return m.group(0) if m else "Not Found"

    @staticmethod
    def _extract_url_pattern(text: str, pattern: str) -> str:
        m = re.search(pattern, text, re.IGNORECASE)
        return m.group(0) if m else "Not Found"

    @staticmethod
    def _extract_sections(text: str) -> Dict[str, List[Any]]:
        """Splits raw text into common section buckets."""
        sections = {
            "education": [],
            "experience": [],
            "certifications": [],
            "projects": [],
            "publications": [],
            "awards": [],
            "volunteer": [],
            "interests": [],
            "achievements": [],
            "languages": []
        }
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        current_sec = None
        
        sec_headers = {
            "education": ["education", "academic qualification", "qualifications"],
            "experience": ["experience", "employment", "work history", "work experience", "professional experience"],
            "certifications": ["certifications", "licenses", "courses", "certificates"],
            "projects": ["projects", "personal projects", "academic projects"],
            "publications": ["publications", "research papers"],
            "awards": ["awards", "honors", "achievements", "accomplishments"],
            "volunteer": ["volunteer", "community involvement", "social work"],
            "interests": ["interests", "hobbies", "extra-curricular"],
            "languages": ["languages", "language proficiency"]
        }
        
        for line in lines:
            line_clean = line.lower().strip(":-#* ")
            matched_sec = None
            for sec_key, keywords in sec_headers.items():
                if any(line_clean == kw or line_clean.startswith(kw) for kw in keywords):
                    matched_sec = sec_key
                    break
            if matched_sec:
                current_sec = matched_sec
                continue
            if current_sec and line:
                if current_sec in ["education", "experience", "projects"]:
                    sections[current_sec].append({"content": line})
                else:
                    sections[current_sec].append(line)
                    
        return sections
