import unittest
from modules.ats_calculator import ATSCalculator

class TestATSCalculator(unittest.TestCase):
    def test_skill_normalization(self):
        self.assertEqual(ATSCalculator._normalize_skill("React.js"), "react")
        self.assertEqual(ATSCalculator._normalize_skill("ReactJS"), "react")
        self.assertEqual(ATSCalculator._normalize_skill("K8s"), "kubernetes")
        self.assertEqual(ATSCalculator._normalize_skill("TS"), "typescript")
        self.assertEqual(ATSCalculator._normalize_skill("CPP"), "c++")

    def test_calculate_score_exact_match(self):
        resume_skills = ["Python", "Docker", "AWS", "SQL"]
        job_skills = ["Python", "Docker", "AWS", "SQL"]
        resume_text = "Experienced Senior Python Developer with 5+ years of experience with Docker, AWS, and SQL. Holds Bachelor of Science in Computer Science."
        jd_text = "Looking for Senior Python Developer with 5+ years of experience with Docker, AWS, and SQL. Requires BS in Computer Science."
        contact_info = {"name": "Test User", "email": "test@example.com", "phone": "+1-555-0100"}

        score, matched, missing = ATSCalculator.calculate_score(
            resume_skills, job_skills, resume_text, jd_text, contact_info
        )
        self.assertGreaterEqual(score, 75.0)
        self.assertEqual(len(missing), 0)
        self.assertEqual(len(matched), 4)

    def test_calculate_score_missing_skills(self):
        resume_skills = ["HTML", "CSS"]
        job_skills = ["Python", "Docker", "Kubernetes", "AWS"]
        score, matched, missing = ATSCalculator.calculate_score(
            resume_skills, job_skills, "Basic web developer.", "Looking for cloud engineer."
        )
        self.assertLess(score, 60.0)
        self.assertEqual(len(matched), 0)
        self.assertEqual(len(missing), 4)

    def test_score_category(self):
        self.assertEqual(ATSCalculator.get_score_category(90.0), "Excellent")
        self.assertEqual(ATSCalculator.get_score_category(76.0), "Excellent")
        self.assertEqual(ATSCalculator.get_score_category(60.0), "Average")
        self.assertEqual(ATSCalculator.get_score_category(40.0), "Needs Improvement")

    def test_star_rating(self):
        self.assertIn("★★★★★", ATSCalculator.get_star_rating(100.0))
        self.assertIn("☆☆☆☆☆", ATSCalculator.get_star_rating(0.0))

    def test_predict_matching_job_roles(self):
        skills = ["Python", "Pandas", "NumPy", "Scikit-Learn", "Machine Learning", "SQL"]
        roles = ATSCalculator.predict_matching_job_roles(skills)
        self.assertTrue(len(roles) > 0)
        top_role = roles[0]["role"]
        self.assertIn(top_role, ["Data Scientist", "Machine Learning Engineer", "Python Developer", "Data Analyst"])

    def test_hygiene_score_with_contact(self):
        contact_complete = {"name": "Jane Doe", "email": "jane@doe.com", "phone": "1234567890"}
        text = """
        EXPERIENCE
        Led team of 5 engineers. Reduced latency by 40%. Built 12 new APIs.
        EDUCATION
        B.S. in Software Engineering
        SKILLS
        Python, Go, Docker
        """
        score = ATSCalculator.calculate_hygiene_score(text, contact_complete)
        self.assertGreaterEqual(score, 70.0)

    def test_suggestions_generation(self):
        missing = ["Docker", "Kubernetes"]
        suggestions = ATSCalculator.generate_suggestions(
            45.0,
            ["Python"],
            missing,
            {"email": "test@test.com", "phone": "1234567890"},
            "Short resume text",
            mode="experienced"
        )
        self.assertTrue(any("Docker" in s or "skills" in s.lower() for s in suggestions))

if __name__ == "__main__":
    unittest.main()
