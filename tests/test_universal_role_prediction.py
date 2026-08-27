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

    def test_field_specific_asset_recommendations(self):
        # Tech resume without GitHub link
        tech_sug = ATSCalculator.generate_suggestions(
            score=70.0, matched_skills=["Python"], missing_skills=[], contact_info={},
            resume_text="Software engineer with 4 years experience building web applications using Python."
        )
        self.assertTrue(any("GitHub" in s for s in tech_sug))

        # Design resume without Behance/Figma link
        design_sug = ATSCalculator.generate_suggestions(
            score=70.0, matched_skills=["UI/UX"], missing_skills=[], contact_info={},
            resume_text="UI/UX Designer creating wireframes and user prototypes."
        )
        self.assertTrue(any("Behance" in s or "Portfolio" in s for s in design_sug))

        # Healthcare resume without medical license
        health_sug = ATSCalculator.generate_suggestions(
            score=70.0, matched_skills=["Patient Care"], missing_skills=[], contact_info={},
            resume_text="Nurse working in hospital ICU providing patient care."
        )
        self.assertTrue(any("Licensure" in s or "Medical" in s for s in health_sug))

    def test_automatic_seniority_detection(self):
        from modules.nlp_engine import nlp_engine

        fresher_text = "Graduate student looking for entry-level Software Developer role. Academic projects in Python and Java."
        fresher_res = nlp_engine.detect_candidate_seniority(fresher_text)
        self.assertTrue(fresher_res["is_fresher"])
        self.assertEqual(fresher_res["label"], "Fresher / Entry-Level Candidate")

        exp_text = "Senior Software Engineer with 5+ years of experience building scalable microservices in Python."
        exp_res = nlp_engine.detect_candidate_seniority(exp_text)
        self.assertFalse(exp_res["is_fresher"])
        self.assertIn("5.0 Yrs Exp", exp_res["label"])

    def test_akash_chourasiya_civil_engineer_seniority(self):
        from modules.nlp_engine import nlp_engine
        akash_text = """
        AKASH CHOURASIYA
        Sanand, Gujarat, India | +91 7869881221 | Email: Chourasiya.akash29@gmail.com
        Qualified with MTech. in Construction Management and B.E. in Civil Engineering, having 11 years of experience in Government Industrial, Commercial, Residential and Infrastructure Projects.
        June'2025 to Present, AGRATAS ENERGY SOLUTIONS (TATA Group), Specialist – Civil.
        Jan'2023 to May'2025, Jacobs Solutions, CSA Lead – Civil, Senior Field Engineer.
        Feb'2020 to Jan'2023, NTPC LTD. Utility Powertech Ltd, Junior Engineer Civil.
        March '2018 to Jan'2020, VARSMA Engineers Group, Site Engineer Civil.
        Oct '2015 to Feb'2018, NTPC LTD. Utility Powertech Ltd, Junior Engineer Civil.
        Training: Tendering & Contract Management | BBS, QS and Billing | AutoCAD | Primavera P6 | MSP
        """
        res = nlp_engine.detect_candidate_seniority(akash_text)
        self.assertFalse(res["is_fresher"])
        self.assertEqual(res["experience_years"], 11.0)
        self.assertIn("11.0 Yrs Exp", res["label"])

    def test_pranab_chourasiya_it_support_name_and_role(self):
        from modules.nlp_engine import nlp_engine
        pranab_text = """
        PRANAB
        CHOURASIYA
        Phone: 9630956249 | Email: pranabchourasiya876@gmail.com
        About Me: A driven and technically adept Computer Applications graduate... passion lies in IT support, system administration, and cybersecurity where I have experience with Active Directory.
        Work experience:
        ITSupport Engineer
        Vistar Technology, Vijay Nagar, Jabalpur Jan2025-Jun2025
        Education: Bachelor of Computer Applications (BCA)
        Hobbies: PC building & troubleshooting
        Skills: PC Hardware, Technical Support, Active Directory, Cybersecurity Basics
        """
        extracted_name = nlp_engine.extract_candidate_name(pranab_text)
        self.assertEqual(extracted_name, "Pranab Chourasiya")

        extracted_role = nlp_engine.extract_target_role(pranab_text)
        self.assertEqual(extracted_role, "IT Support Engineer")

if __name__ == "__main__":
    unittest.main()
