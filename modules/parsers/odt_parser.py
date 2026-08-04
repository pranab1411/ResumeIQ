"""
modules/parsers/odt_parser.py
OpenDocument Text (ODT) parser using odfpy or zipfile content.xml extraction.
"""

import zipfile
import xml.etree.ElementTree as ET
from utils.logger import logger

def parse_odt(file_path: str) -> str:
    try:
        from odf.opendocument import load
        from odf.text import P
        doc = load(file_path)
        paragraphs = [p.text for p in doc.getElementsByType(P) if p.text]
        return "\n".join(paragraphs).strip()
    except Exception as e:
        logger.warning(f"[ODTParser] odfpy load failed ({e}), using zip/xml extraction fallback")
        return _extract_odt_zip(file_path)

def _extract_odt_zip(file_path: str) -> str:
    try:
        with zipfile.ZipFile(file_path, 'r') as z:
            content_xml = z.read('content.xml')
            root = ET.fromstring(content_xml)
            texts = []
            for elem in root.iter():
                if elem.text and elem.text.strip():
                    texts.append(elem.text.strip())
            return "\n".join(texts).strip()
    except Exception as err:
        logger.error(f"[ODTParser] ZIP fallback failed for {file_path}: {err}")
        raise Exception(f"Failed to parse ODT file: {err}")
