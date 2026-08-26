import os
import unittest
import tempfile
from modules.parser import DocumentParser

class TestDocumentParser(unittest.TestCase):
    def test_txt_parsing(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
            f.write("Sample Resume Content\nSkills: Python, SQL, Git\nExperience: 4 years")
            temp_path = f.name

        try:
            text = DocumentParser.extract_text(temp_path)
            self.assertIn("Sample Resume Content", text)
            self.assertIn("Python", text)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_nonexistent_file(self):
        with self.assertRaises(FileNotFoundError):
            DocumentParser.extract_text("non_existent_file_12345.pdf")

    def test_unsupported_extension(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".xyz", delete=False) as f:
            f.write("Some text")
            temp_path = f.name

        try:
            with self.assertRaises(ValueError):
                DocumentParser.extract_text(temp_path)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

if __name__ == "__main__":
    unittest.main()
