"""
modules/parsers/rtf_parser.py
RTF parser using striprtf with regex fallback.
"""

import re
from utils.logger import logger

def parse_rtf(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        raw = f.read()
        
    try:
        from striprtf.striprtf import rtf_to_text
        return rtf_to_text(raw).strip()
    except Exception as e:
        logger.warning(f"[RTFParser] striprtf failed or not installed ({e}), using regex fallback")
        # Basic RTF control word stripping fallback
        clean = re.sub(r'\\[a-z0-9]+\b', '', raw)
        clean = re.sub(r'[{}]', '', clean)
        return clean.strip()
