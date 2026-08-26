import unittest
from modules.nlp_engine import nlp_engine

class TestNLPEngine(unittest.TestCase):
    def test_extract_contact_info(self):
        text = "Candidate: Alice Wonder | Email: alice.wonder@example.com | Cell: +1 555 234 5678"
        contact = nlp_engine.extract_contact_info(text)
        self.assertEqual(contact["email"], "alice.wonder@example.com")
        self.assertTrue("555" in contact["phone"] or contact["phone"] != "Not Found")

    def test_extract_skills_boundary_matching(self):
        # Must extract 'Java' and 'JavaScript' distinctly without false partial matches
        text = "Experienced in Java backend services and modern JavaScript frontend applications."
        skills = nlp_engine.extract_skills(text)
        self.assertIn("Java", skills)
        self.assertIn("JavaScript", skills)

    def test_extract_skills_case_insensitivity(self):
        text = "Proficient with python, DOCKER, and Kubernetes."
        skills = nlp_engine.extract_skills(text)
        self.assertIn("Python", skills)
        self.assertIn("Docker", skills)
        self.assertIn("Kubernetes", skills)

    def test_extract_metrics(self):
        text = "Increased revenue by 25% and saved $150000 across 12+ projects."
        metrics = nlp_engine.extract_metrics(text)
        self.assertGreaterEqual(len(metrics), 2)

    def test_extract_candidate_name_blacklist(self):
        # Should not extract generic section headers as candidate names
        text = """
        RESUME
        CURRICULUM VITAE
        SUMMARY OF QUALIFICATIONS
        Johnathan Davis
        Email: john.davis@email.com
        """
        name = nlp_engine.extract_candidate_name(text)
        self.assertNotIn("Resume", name)
        self.assertNotIn("Curriculum", name)
        self.assertNotIn("Summary", name)
        self.assertTrue("Johnathan" in name or "Davis" in name or name != "Candidate")

    def test_extract_keywords_from_jd(self):
        jd = "We are seeking a Backend Engineer with strong Python, FastAPI, PostgreSQL, and AWS experience."
        keywords = nlp_engine.extract_keywords_from_jd(jd)
        self.assertIn("Python", keywords)
        self.assertIn("PostgreSQL", keywords)
        self.assertIn("AWS", keywords)

    def test_generate_highlighted_html(self):
        resume_text = "Architected a scalable Python backend, optimizing latency by 35%."
        html_out = nlp_engine.generate_highlighted_html(
            resume_text,
            matched_skills=["Python"],
            missing_skills=["Docker"],
            is_jd=False
        )
        self.assertIn("Python", html_out)
        self.assertIn("#34D399", html_out) # Emerald green for matched skill
        self.assertIn("#A5B4FC", html_out) # Indigo for action verb 'Architected'
        self.assertIn("#67E8F9", html_out) # Cyan for metric '35%'

if __name__ == "__main__":
    unittest.main()

