"""
modules/parsers/txt_parser.py
Plain text parser.
"""

def parse_txt(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read().strip()
