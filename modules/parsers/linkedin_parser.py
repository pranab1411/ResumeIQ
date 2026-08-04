"""
modules/parsers/linkedin_parser.py
Specialist parser for LinkedIn PDF exports.
Extracts structured sections like Contact, Top Skills, Summary, Experience, Education.
"""

import re
from typing import Dict, Any, List
from utils.logger import logger

def parse_linkedin_pdf(text: str) -> Dict[str, Any]:
    """
    Parses raw text extracted from a LinkedIn PDF export into structured fields.
    """
    result = {
        "candidate_name": "",
        "headline": "",
        "contact": {},
        "top_skills": [],
        "summary": "",
        "experience": [],
        "education": []
    }
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    if not lines:
        return result
        
    # LinkedIn PDF format typically has Contact, Top Skills sidebar, then Name, Headline, Summary, Experience
    name_found = False
    in_section = ""
    
    for i, line in enumerate(lines):
        if line.lower() == "contact" or "linkedin.com/in/" in line.lower():
            in_section = "contact"
            continue
        elif line.lower() == "top skills":
            in_section = "skills"
            continue
        elif line.lower() == "summary":
            in_section = "summary"
            continue
        elif line.lower() == "experience":
            in_section = "experience"
            continue
        elif line.lower() == "education":
            in_section = "education"
            continue
            
        if not name_found and not in_section and not line.startswith("Page ") and "@" not in line:
            result["candidate_name"] = line
            name_found = True
            continue
            
        if in_section == "skills":
            result["top_skills"].append(line)
        elif in_section == "summary":
            result["summary"] += line + " "
            
    result["summary"] = result["summary"].strip()
    return result
