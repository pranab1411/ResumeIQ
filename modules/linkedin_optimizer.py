"""
Feature 13: LinkedIn Profile Optimizer for ResumeIQ.
Analyzes LinkedIn section text and provides ATS-friendly optimization tips.
"""

import re
from typing import Dict, List
from modules.nlp_engine import nlp_engine
from modules.ats_calculator import ATSCalculator
from utils.logger import logger

class LinkedInOptimizer:
    """Analyzes LinkedIn profile sections and scores them for ATS visibility."""

    ACTION_VERBS = [
        "led", "built", "developed", "designed", "managed", "created",
        "architected", "optimized", "scaled", "launched", "delivered",
        "implemented", "improved", "reduced", "increased", "spearheaded",
        "engineered", "collaborated", "mentored", "automated"
    ]

    HEADLINE_KEYWORDS = [
        "engineer", "developer", "scientist", "analyst", "manager",
        "architect", "designer", "consultant", "specialist", "lead"
    ]

    @staticmethod
    def score_headline(headline: str) -> Dict:
        """Scores a LinkedIn headline for ATS friendliness."""
        score = 0
        tips = []
        if not headline:
            return {"score": 0, "tips": ["Add a compelling LinkedIn headline with your job title and top 2 skills."]}

        text_lower = headline.lower()
        if any(kw in text_lower for kw in LinkedInOptimizer.HEADLINE_KEYWORDS):
            score += 30
        else:
            tips.append("Include your exact job title (e.g., 'Senior Python Engineer') in the headline.")

        if "|" in headline or "•" in headline or "-" in headline:
            score += 20
        else:
            tips.append("Use '|' or '•' to separate title, skills, and value prop. E.g., 'Python Dev | AWS | 5 YOE'.")

        if len(headline) >= 80:
            score += 30
            tips.append("Good length! Keep it near the 220-character LinkedIn limit for maximum visibility.")
        elif len(headline) >= 50:
            score += 20
            tips.append("Expand headline to 80+ characters to maximize keyword surface area.")
        else:
            tips.append("Headline is too short. Use all 220 characters to add role, skills, and value.")

        score += 20
        return {"score": min(score, 100), "tips": tips if tips else ["Headline looks strong!"]}

    @staticmethod
    def score_about(about: str) -> Dict:
        """Scores the LinkedIn About section."""
        score = 0
        tips = []
        if not about:
            return {"score": 0, "tips": ["Write a 3-5 paragraph About section summarizing experience, skills, and achievements."]}

        words = about.split()
        if len(words) >= 200:
            score += 25
        elif len(words) >= 100:
            score += 15
            tips.append("Expand About to 200+ words for better LinkedIn SEO visibility.")
        else:
            tips.append("About section is too brief. Aim for 200–300 words covering skills, experience, and goals.")

        text_lower = about.lower()
        verbs_found = sum(1 for v in LinkedInOptimizer.ACTION_VERBS if v in text_lower)
        if verbs_found >= 5:
            score += 25
        elif verbs_found >= 2:
            score += 15
            tips.append("Add more action verbs (Led, Built, Delivered) to make the section impactful.")
        else:
            tips.append("Use strong action verbs: 'Led', 'Built', 'Delivered', 'Optimized'.")

        metrics = re.findall(r'\d+%|\$\d+|\d+\+?\s*(years|users|projects|teams)', text_lower)
        if len(metrics) >= 2:
            score += 25
        elif len(metrics) >= 1:
            score += 15
            tips.append("Add more quantified achievements (e.g., 'Reduced latency by 40%').")
        else:
            tips.append("Quantify your impact with numbers: %, $, headcount, or timelines.")

        score += 25
        return {"score": min(score, 100), "tips": tips if tips else ["About section looks strong!"]}

    @staticmethod
    def score_skills(skills_text: str, job_title: str = "") -> Dict:
        """Scores the LinkedIn Skills section."""
        score = 0
        tips = []
        if not skills_text:
            return {"score": 0, "tips": ["Add at least 10 relevant skills to maximize keyword matching."]}

        extracted = nlp_engine.extract_skills(skills_text)
        skill_count = len(extracted)

        if skill_count >= 10:
            score += 50
        elif skill_count >= 5:
            score += 30
            tips.append(f"Add more skills. You have {skill_count}, aim for 10–50 for maximum ATS coverage.")
        else:
            score += 10
            tips.append(f"Only {skill_count} skills detected. LinkedIn allows up to 50 skills — use them all.")

        score += 50
        return {
            "score": min(score, 100),
            "detected_skills": extracted,
            "tips": tips if tips else ["Skills section looks well-populated!"]
        }

    @classmethod
    def analyze_full_profile(cls, headline: str, about: str, skills: str, job_title: str = "") -> Dict:
        """Runs full LinkedIn profile analysis and returns composite score + tips per section."""
        h = cls.score_headline(headline)
        a = cls.score_about(about)
        s = cls.score_skills(skills, job_title)

        composite = round((h["score"] * 0.30) + (a["score"] * 0.40) + (s["score"] * 0.30), 1)
        stars = ATSCalculator.get_star_rating_gui(composite)
        category = ATSCalculator.get_score_category(composite)

        logger.info(f"[LinkedIn Optimizer] Composite Score: {composite}% (H:{h['score']} A:{a['score']} S:{s['score']})")
        return {
            "composite_score": composite,
            "stars": stars,
            "category": category,
            "headline": h,
            "about": a,
            "skills": s
        }
