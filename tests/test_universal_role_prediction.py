import unittest
from modules.ats_calculator import ATSCalculator

class TestUniversalRolePrediction(unittest.TestCase):
    def test_nursing_role_prediction(self):
        skills = ["Patient Care", "EHR/EMR", "Triage", "Vital Signs", "CPR", "HIPAA Compliance"]
        roles = ATSCalculator.predict_matching_job_roles(skills, top_n=3)
        self.assertGreater(len(roles), 0)
        self.assertIn("Nurse", roles[0]["role"])
        self.assertEqual(roles[0]["category"], "Healthcare & Nursing")

    def test_civil_engineering_role_prediction(self):
        skills = ["AutoCAD", "Revit", "Civil 3D", "Structural Analysis", "Surveying", "Concrete Technology"]
        roles = ATSCalculator.predict_matching_job_roles(skills, top_n=3)
        self.assertGreater(len(roles), 0)
        self.assertIn("Civil", roles[0]["role"])
        self.assertEqual(roles[0]["category"], "Civil & Structural Engineering")

    def test_finance_role_prediction(self):
        skills = ["Financial Modeling", "Financial Analysis", "Corporate Finance", "Valuation", "Risk Assessment", "Financial Reporting"]
        roles = ATSCalculator.predict_matching_job_roles(skills, top_n=3)
        self.assertGreater(len(roles), 0)
        self.assertIn("Financial", roles[0]["role"])
        self.assertEqual(roles[0]["category"], "Finance & Banking")

    def test_teaching_role_prediction(self):
        skills = ["Lesson Planning", "Classroom Management", "Curriculum Development", "Student Assessment", "EdTech"]
        roles = ATSCalculator.predict_matching_job_roles(skills, top_n=3)
        self.assertGreater(len(roles), 0)
        self.assertIn("Teacher", roles[0]["role"])
        self.assertEqual(roles[0]["category"], "Education & Teaching")

    def test_supply_chain_role_prediction(self):
        skills = ["Supply Chain Optimization", "Inventory Management", "Procurement", "Warehouse Management", "ERP", "SAP S/4HANA"]
        roles = ATSCalculator.predict_matching_job_roles(skills, top_n=3)
        self.assertGreater(len(roles), 0)
        self.assertIn("Supply Chain", roles[0]["role"])
        self.assertEqual(roles[0]["category"], "Supply Chain & Logistics")

    def test_software_role_prediction(self):
        skills = ["Python", "React", "Node.js", "SQL", "Docker", "REST APIs"]
        roles = ATSCalculator.predict_matching_job_roles(skills, top_n=3)
        self.assertGreater(len(roles), 0)
        self.assertIn("Full Stack Developer", roles[0]["role"])
    def test_holistic_profile_role_prediction(self):
        skills = ["Patient Care", "EHR/EMR", "Triage", "Vital Signs"]
        edu = ["Bachelor of Science in Nursing (BSN)"]
        positions = ["Staff Nurse", "Junior Clinical Specialist"]
        roles = ATSCalculator.predict_matching_job_roles(
            extracted_skills=skills,
            top_n=3,
            resume_text="Worked 3 years as Staff Nurse in Hospital ICU performing triage and patient assessment.",
            education_info=edu,
            previous_positions=positions,
            work_experience_years=3.2
        )
        self.assertGreater(len(roles), 0)
        self.assertTrue(any("Nurse" in r["role"] for r in roles))

if __name__ == "__main__":
    unittest.main()
