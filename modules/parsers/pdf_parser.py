"""
modules/parsers/pdf_parser.py
PDF parser with pdfplumber and OCR fallback for scanned/image PDFs.
"""

import os
import pdfplumber
from utils.logger import logger

def parse_pdf(file_path: str) -> str:
    """Extracts plain text from a PDF file using pdfplumber with OCR fallback."""
    text_content = []
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_content.append(page_text)
        
        full_text = "\n".join(text_content).strip()
        
        # If pdfplumber returns empty or very little text, attempt OCR
        if len(full_text) < 50:
            logger.info(f"[PDFParser] Low text count ({len(full_text)} chars). Attempting OCR fallback on {file_path}")
            ocr_text = _ocr_fallback(file_path)
            if ocr_text and len(ocr_text) > len(full_text):
                return ocr_text
                
        return full_text
    except Exception as e:
        logger.error(f"[PDFParser] Error parsing PDF {file_path}: {e}")
        # Try OCR as emergency fallback
        ocr_text = _ocr_fallback(file_path)
        if ocr_text:
            return ocr_text
        raise Exception(f"Failed to parse PDF file: {e}")

def _ocr_fallback(file_path: str) -> str:
    """OCR fallback for scanned or image-based PDFs."""
    try:
        import pytesseract
        from PIL import Image
        with pdfplumber.open(file_path) as pdf:
            ocr_pages = []
            for i, page in enumerate(pdf.pages):
                try:
                    img = page.to_image(resolution=300).original
                    txt = pytesseract.image_to_string(img)
                    if txt:
                        ocr_pages.append(txt)
                except Exception as page_err:
                    logger.warning(f"[PDFParser OCR] Page {i} failed: {page_err}")
            return "\n".join(ocr_pages).strip()
    except ImportError:
        logger.warning("[PDFParser OCR] pytesseract or PIL not installed. OCR unavailable.")
        return ""
    except Exception as e:
        logger.warning(f"[PDFParser OCR] OCR failed on {file_path}: {e}")
        return ""
