"""
modules/parsers package
Resume parsing engines for multiple file formats and templates.
"""

from typing import Dict, Any, Tuple
import os
import re
from utils.logger import logger

def detect_resume_format(text: str, file_path: str) -> Tuple[str, bool, bool]:
    """
    Detects format type, is_linkedin_export, is_europass.
    """
    ext = os.path.splitext(file_path)[1].lower()
    text_lower = text.lower()
    
    is_linkedin = "linkedin" in text_lower and ("contact" in text_lower or "top skills" in text_lower or "summary" in text_lower)
    is_europass = "europass" in text_lower or "curriculum vitae" in text_lower and "personal information" in text_lower
    
    fmt = ext.lstrip(".")
    if is_linkedin:
        fmt = "linkedin_pdf"
    elif is_europass:
        fmt = "europass"
        
    return fmt, is_linkedin, is_europass
