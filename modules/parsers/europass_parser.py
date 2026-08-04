"""
modules/parsers/europass_parser.py
Specialist parser for Europass CV format resumes.
Extracts standard Europass sections (Personal Information, Work Experience, Education and Training, Personal Skills).
"""

import re
from typing import Dict, Any
from utils.logger import logger

def parse_europass(text: str) -> Dict[str, Any]:
    """
    Parses Europass CV structure into candidate data.
    """
    result = {
        "is_europass": True,
        "sections_found": []
    }
    
    sections = [
        "PERSONAL INFORMATION", "WORK EXPERIENCE", "EDUCATION AND TRAINING",
        "PERSONAL SKILLS", "MOTHER TONGUE", "OTHER LANGUAGES",
        "DIGITAL SKILLS", "ADDITIONAL INFORMATION"
    ]
    
    text_upper = text.upper()
    for sec in sections:
        if sec in text_upper:
            result["sections_found"].append(sec)
            
    return result
