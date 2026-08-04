"""
modules/parsers/html_parser.py
HTML resume parser using BeautifulSoup or html.parser.
"""

from utils.logger import logger

def parse_html(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        html_content = f.read()
        
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, "html.parser")
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        text = soup.get_text(separator="\n")
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        return "\n".join(chunk for chunk in chunks if chunk)
    except Exception as e:
        logger.warning(f"[HTMLParser] BeautifulSoup failed ({e}), using basic html.parser fallback")
        import html.parser
        class HTMLTextExtractor(html.parser.HTMLParser):
            def __init__(self):
                super().__init__()
                self.result = []
            def handle_data(self, data):
                d = data.strip()
                if d:
                    self.result.append(d)
        parser = HTMLTextExtractor()
        parser.feed(html_content)
        return "\n".join(parser.result)
