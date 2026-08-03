"""
Feature 8: Industry Benchmarking Module for ResumeIQ.
Provides ATS score benchmarks and percentile rankings per job category.
"""

from typing import Dict, Tuple

# Industry-average ATS score benchmarks by job category (Tech & Non-Tech Roles)
INDUSTRY_BENCHMARKS: Dict[str, Dict] = {
    # Tech Roles
    "software engineer": {"avg": 68.0, "top25": 82.0, "top10": 91.0, "label": "Software Engineering"},
    "data scientist": {"avg": 65.0, "top25": 79.0, "top10": 89.0, "label": "Data Science"},
    "product manager": {"avg": 60.0, "top25": 74.0, "top10": 85.0, "label": "Product Management"},
    "frontend developer": {"avg": 66.0, "top25": 80.0, "top10": 90.0, "label": "Frontend Development"},
    "backend developer": {"avg": 67.0, "top25": 81.0, "top10": 91.0, "label": "Backend Development"},
    "full stack developer": {"avg": 67.0, "top25": 81.0, "top10": 91.0, "label": "Full Stack Development"},
    "devops engineer": {"avg": 63.0, "top25": 77.0, "top10": 88.0, "label": "DevOps Engineering"},
    "site reliability engineer": {"avg": 65.0, "top25": 79.0, "top10": 89.0, "label": "Site Reliability (SRE)"},
    "machine learning engineer": {"avg": 64.0, "top25": 78.0, "top10": 89.0, "label": "ML Engineering"},
    "data engineer": {"avg": 66.0, "top25": 80.0, "top10": 90.0, "label": "Data Engineering"},
    "data analyst": {"avg": 62.0, "top25": 76.0, "top10": 87.0, "label": "Data Analytics"},
    "qa engineer": {"avg": 64.0, "top25": 78.0, "top10": 88.0, "label": "QA & Test Engineering"},
    "mobile developer": {"avg": 65.0, "top25": 79.0, "top10": 89.0, "label": "Mobile Development"},
    "ui ux designer": {"avg": 58.0, "top25": 72.0, "top10": 83.0, "label": "UI/UX Design"},
    "cloud architect": {"avg": 65.0, "top25": 79.0, "top10": 90.0, "label": "Cloud Architecture"},
    "cybersecurity analyst": {"avg": 62.0, "top25": 76.0, "top10": 87.0, "label": "Cybersecurity"},
    "embedded engineer": {"avg": 64.0, "top25": 78.0, "top10": 88.0, "label": "Embedded Systems"},
    "network engineer": {"avg": 61.0, "top25": 75.0, "top10": 86.0, "label": "Network Engineering"},
    "desktop support engineer": {"avg": 62.0, "top25": 76.0, "top10": 87.0, "label": "Desktop Support Engineering"},
    "it support engineer": {"avg": 63.0, "top25": 77.0, "top10": 88.0, "label": "IT Support Engineering"},
    "helpdesk technician": {"avg": 60.0, "top25": 74.0, "top10": 85.0, "label": "IT Helpdesk & Service Desk"},
    "system administrator": {"avg": 64.0, "top25": 78.0, "top10": 89.0, "label": "Systems Administration"},
    
    # Non-Tech Roles
    "digital marketer": {"avg": 60.0, "top25": 74.0, "top10": 85.0, "label": "Digital Marketing"},
    "marketing manager": {"avg": 61.0, "top25": 75.0, "top10": 86.0, "label": "Marketing Management"},
    "sales executive": {"avg": 58.0, "top25": 72.0, "top10": 84.0, "label": "Sales & Business Development"},
    "account manager": {"avg": 59.0, "top25": 73.0, "top10": 84.0, "label": "Account Management"},
    "project manager": {"avg": 59.0, "top25": 73.0, "top10": 84.0, "label": "Project Management"},
    "operations manager": {"avg": 60.0, "top25": 74.0, "top10": 85.0, "label": "Operations Management"},
    "business analyst": {"avg": 61.0, "top25": 75.0, "top10": 86.0, "label": "Business Analysis"},
    "financial analyst": {"avg": 63.0, "top25": 77.0, "top10": 88.0, "label": "Financial Analysis"},
    "accountant": {"avg": 62.0, "top25": 76.0, "top10": 87.0, "label": "Accounting & Finance"},
    "hr manager": {"avg": 58.0, "top25": 72.0, "top10": 83.0, "label": "Human Resources"},
    "talent acquisition": {"avg": 60.0, "top25": 74.0, "top10": 85.0, "label": "Talent Acquisition"},
    "customer success": {"avg": 59.0, "top25": 73.0, "top10": 84.0, "label": "Customer Success"},
    "content strategist": {"avg": 58.0, "top25": 72.0, "top10": 83.0, "label": "Content Strategy & Copywriting"},
    "graphic designer": {"avg": 56.0, "top25": 70.0, "top10": 81.0, "label": "Graphic Design"},
    "legal counsel": {"avg": 64.0, "top25": 78.0, "top10": 89.0, "label": "Legal & Compliance"},
    "supply chain": {"avg": 60.0, "top25": 74.0, "top10": 85.0, "label": "Supply Chain & Logistics"},
    
    "default": {"avg": 63.0, "top25": 77.0, "top10": 88.0, "label": "General Professional"},
}


class IndustryBenchmark:
    @staticmethod
    def get_benchmark(job_title: str) -> Dict:
        """Returns benchmark data for the closest matching job category."""
        title_lower = job_title.lower().strip() if job_title else ""
        if not title_lower:
            return INDUSTRY_BENCHMARKS["default"]

        # Pass 1: Check exact full-key substring match
        for key, data in INDUSTRY_BENCHMARKS.items():
            if key != "default" and key in title_lower:
                return data

        # Pass 2: Fallback to keyword word match
        for key, data in INDUSTRY_BENCHMARKS.items():
            if key != "default" and any(word in title_lower for word in key.split() if len(word) > 3):
                return data

        return INDUSTRY_BENCHMARKS["default"]

    @staticmethod
    def get_percentile_text(score: float, job_title: str = "") -> Tuple[str, str]:
        """
        Returns (percentile_label, description) for a given ATS score.
        E.g. ("Top 12%", "Above average for Software Engineers")
        """
        bench = IndustryBenchmark.get_benchmark(job_title)
        label = bench["label"]
        avg = bench["avg"]
        top25 = bench["top25"]
        top10 = bench["top10"]

        if score >= top10:
            return f"Top 10%", f"Exceptional! You're in the top 10% of {label} candidates."
        elif score >= top25:
            pct = int(10 + (top10 - score) / (top10 - top25) * 15)
            return f"Top {pct}%", f"Strong! You're in the top 25% of {label} candidates."
        elif score >= avg:
            pct = int(25 + (top25 - score) / (top25 - avg) * 25)
            return f"Top {pct}%", f"Above average for {label} roles. Industry average: {avg}%."
        else:
            gap = round(avg - score, 1)
            return f"Below Avg", f"Your score is {gap}% below the {label} industry average of {avg}%."

    @staticmethod
    def get_all_benchmarks() -> Dict[str, Dict]:
        return INDUSTRY_BENCHMARKS
