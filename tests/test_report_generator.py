import os
import unittest
from modules.report_generator import PDFReportGenerator
from modules.ats_calculator import ATSCalculator
from modules.ats_benchmark import ATSBenchmarkEngine

class TestPDFReportGenerator(unittest.TestCase):
    def setUp(self):
        self.output_dir = os.path.join(os.path.dirname(__file__), "test_outputs")
        os.makedirs(self.output_dir, exist_ok=True)

    def test_strong_experienced_resume_report(self):
        output_path = os.path.join(self.output_dir, "test_report_strong_experienced.pdf")
        resume_text = """
        John Doe
        Email: john.doe@email.com | Phone: +1-555-0199 | San Francisco, CA
        Senior Full Stack Engineer with 6+ years of experience in distributed cloud systems.
        
        EXPERIENCE:
        Staff Software Engineer at Tech Corp (2021 - Present)
        • Architected microservices with Python, FastAPI, and Docker, reducing API latency by 35%.
        • Led migration of PostgreSQL databases to AWS RDS, achieving 99.99% system uptime.
        • Developed frontend features using React, TypeScript, and TailwindCSS for 500,000+ active users.
        • Implemented CI/CD deployment pipelines using GitHub Actions and Kubernetes.
        
        EDUCATION:
        Bachelor of Science in Computer Science, State University, 2018
        
        SKILLS:
        Python, React, TypeScript, Docker, Kubernetes, AWS, PostgreSQL, FastAPI, Git, CI/CD
        """
        jd_text = """
        Looking for a Senior Software Engineer with expertise in Python, React, Docker, AWS, and PostgreSQL.
        Requires Bachelor's degree and 5+ years of software development experience.
        """
        matched_skills = ["Python", "React", "Docker", "AWS", "PostgreSQL", "Git", "TypeScript", "FastAPI", "Kubernetes"]
        missing_skills = []
        suggestions = [
            "Highlight specific AWS cloud services used (e.g. Lambda, S3, ECS).",
            "Include additional performance metrics for database query optimization."
        ]
        
        res = PDFReportGenerator.generate(
            output_path=output_path,
            candidate_name="John Doe",
            filename="John_Doe_Senior_SWE.pdf",
            job_title="Senior Software Engineer",
            ats_score=92.5,
            score_category="Excellent",
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            suggestions=suggestions,
            rqi=88.0,
            confidence_score=90.0,
            evaluation_mode="Experienced ATS Match",
            resume_text=resume_text,
            jd_text=jd_text,
            contact_info={"name": "John Doe", "email": "john.doe@email.com", "phone": "+1-555-0199"}
        )
        self.assertTrue(os.path.exists(output_path))
        self.assertGreater(os.path.getsize(output_path), 5000)

    def test_weaker_resume_with_missing_skills(self):
        output_path = os.path.join(self.output_dir, "test_report_weaker_missing_skills.pdf")
        resume_text = """
        Alex Smith
        Self-taught developer looking for software opportunities.
        Worked on basic web development projects using HTML and CSS.
        """
        jd_text = """
        Required Skills: Python, Django, PostgreSQL, Docker, AWS, React, Kubernetes.
        Experience: 3+ years required.
        """
        matched_skills = ["HTML", "CSS"]
        missing_skills = ["Python", "Django", "PostgreSQL", "Docker", "AWS", "React", "Kubernetes"]
        suggestions = [
            "Add a dedicated Skills section explicitly listing technical languages and frameworks.",
            "Incorporate quantifiable metrics into your project descriptions (e.g. user counts, efficiency gains).",
            "Include your contact email and phone number in the header for ATS parser detection.",
            "Acquire and document hands-on experience in missing target skills: Python, Docker, PostgreSQL."
        ]
        
        res = PDFReportGenerator.generate(
            output_path=output_path,
            candidate_name="Alex Smith",
            filename="Alex_Smith_Resume.docx",
            job_title="Full Stack Developer",
            ats_score=42.0,
            score_category="Needs Improvement",
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            suggestions=suggestions,
            rqi=45.0,
            confidence_score=38.0,
            evaluation_mode="Experienced ATS Match",
            resume_text=resume_text,
            jd_text=jd_text,
            contact_info={"name": "Alex Smith", "email": "Not Found", "phone": "Not Found"}
        )
        self.assertTrue(os.path.exists(output_path))
        self.assertGreater(os.path.getsize(output_path), 5000)

    def test_fresher_mode_report(self):
        output_path = os.path.join(self.output_dir, "test_report_fresher.pdf")
        resume_text = """
        Priya Sharma
        Email: priya.sharma@college.edu | Phone: +91-9876543210
        Computer Science Graduate (2024)
        
        EDUCATION:
        B.Tech in Computer Science and Engineering, National Institute of Technology (CGPA: 8.8/10)
        
        ACADEMIC PROJECTS:
        • ResumeIQ - AI Resume Analyzer: Built PyQt6 desktop application with spaCy NLP and SQLite.
        • E-Commerce Web Portal: Developed full stack web app using Python, Django, and SQLite.
        
        TECHNICAL SKILLS:
        Python, C++, Java, SQL, Git, HTML, CSS, JavaScript, Data Structures, Algorithms
        """
        matched_skills = ["Python", "C++", "Java", "SQL", "Git", "HTML", "CSS", "JavaScript"]
        suggestions = [
            "Add GitHub repository links for your academic projects.",
            "List relevant coursework such as Database Management Systems and Operating Systems.",
            "Highlight participation in coding contests, hackathons, or open-source contributions."
        ]
        
        res = PDFReportGenerator.generate(
            output_path=output_path,
            candidate_name="Priya Sharma",
            filename="Priya_Sharma_Resume.pdf",
            job_title="Software Development Engineer (Entry Level)",
            ats_score=85.0,
            score_category="Excellent",
            matched_skills=matched_skills,
            missing_skills=[],
            suggestions=suggestions,
            rqi=85.0,
            confidence_score=82.0,
            evaluation_mode="Fresher Evaluation",
            resume_text=resume_text,
            contact_info={"name": "Priya Sharma", "email": "priya.sharma@college.edu", "phone": "+91-9876543210"}
        )
        self.assertTrue(os.path.exists(output_path))
        self.assertGreater(os.path.getsize(output_path), 5000)

if __name__ == "__main__":
    unittest.main()
