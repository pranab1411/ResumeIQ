"""
modules/linkedin_optimizer.py
LinkedIn Profile Optimizer Engine for ResumeIQ v2.0.
Analyzes LinkedIn profile sections (Headline, About, Skills, Experience, Banner),
scores profile strength, and generates AI-optimized Headlines, About sections,
and Experience bullet points via Gemini.
"""

import re
from typing import Dict, List, Any, Optional
from modules.nlp_engine import nlp_engine
from modules.ats_calculator import ATSCalculator
from utils.logger import logger
from utils.gemini_client import gemini_generate, gemini_available

class LinkedInOptimizer:
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

    @classmethod
    def analyze_full_profile(
        cls,
        headline: str,
        about: str,
        skills: str,
        experience: str = "",
        job_title: str = ""
    ) -> Dict[str, Any]:
        """
        Runs complete v2.0 LinkedIn profile analysis & AI generation.
        """
        h_res = cls.score_headline(headline)
        a_res = cls.score_about(about)
        s_res = cls.score_skills(skills, job_title)
        e_res = cls.score_experience(experience)
        b_res = cls.recommend_banner(job_title)

        composite = round(
            (h_res["score"] * 0.25) +
            (a_res["score"] * 0.35) +
            (s_res["score"] * 0.25) +
            (e_res["score"] * 0.15),
            1
        )
        stars = ATSCalculator.get_star_rating_gui(composite)
        category = ATSCalculator.get_score_category(composite)

        # AI Optimizations via Gemini
        ai_headline = cls.generate_ai_headline(headline, job_title, skills)
        ai_about = cls.generate_ai_about(about, job_title, skills)
        ai_experience = cls.generate_ai_experience(experience, job_title)

        return {
            "composite_score": composite,
            "stars": stars,
            "category": category,
            "headline": h_res,
            "about": a_res,
            "skills": s_res,
            "experience": e_res,
            "banner": b_res,
            "ai_suggestions": {
                "optimized_headline": ai_headline,
                "optimized_about": ai_about,
                "optimized_experience": ai_experience
            }
        }

    @staticmethod
    def score_headline(headline: str) -> Dict[str, Any]:
        score = 0
        tips = []
        if not headline:
            return {"score": 0, "tips": ["Add a compelling headline containing your target job title and key skills."]}

        text_lower = headline.lower()
        if any(kw in text_lower for kw in LinkedInOptimizer.HEADLINE_KEYWORDS):
            score += 30
        else:
            tips.append("Include your exact target job title (e.g. 'Senior Full Stack Developer').")

        if "|" in headline or "•" in headline or "-" in headline:
            score += 20
        else:
            tips.append("Use separators '|' or '•' between title, key skills, and value statement.")

        if len(headline) >= 80:
            score += 30
        elif len(headline) >= 40:
            score += 20
            tips.append("Expand headline to 80+ characters to cover more searchable recruiter keywords.")
        else:
            tips.append("Headline is too short. Use up to 220 characters to maximize reach.")

        score += 20
        return {"score": min(score, 100), "tips": tips or ["Headline is strong!"]}

    @staticmethod
    def score_about(about: str) -> Dict[str, Any]:
        score = 0
        tips = []
        if not about:
            return {"score": 0, "tips": ["Write a 200–300 word About section summarizing your career, core skills, and achievements."]}

        words = about.split()
        if len(words) >= 200:
            score += 35
        elif len(words) >= 100:
            score += 20
            tips.append("Expand your About section to 200+ words to boost profile ranking.")
        else:
            tips.append("About section is too short. Aim for 200–300 words.")

        text_lower = about.lower()
        verbs_found = sum(1 for v in LinkedInOptimizer.ACTION_VERBS if v in text_lower)
        if verbs_found >= 4:
            score += 35
        else:
            tips.append("Add strong action verbs (e.g. 'Engineered', 'Spearheaded', 'Optimized').")

        metrics = re.findall(r'\d+%|\$\d+|\d+\+', text_lower)
        if len(metrics) >= 2:
            score += 30
        else:
            tips.append("Include quantified results (e.g. 'boosted traffic by 40%').")

        return {"score": min(score, 100), "tips": tips or ["About section looks great!"]}

    @staticmethod
    def score_skills(skills_text: str, job_title: str = "") -> Dict[str, Any]:
        extracted = nlp_engine.extract_skills(skills_text)
        count = len(extracted)
        score = min(100, count * 10)
        tips = []
        if count < 10:
            tips.append(f"Only {count} skills detected. LinkedIn allows 50 skills — add at least 10–15 core skills.")
        return {"score": score, "detected_skills": extracted, "count": count, "tips": tips or ["Skills section is well-populated."]}

    @staticmethod
    def score_experience(experience_text: str) -> Dict[str, Any]:
        if not experience_text:
            return {"score": 50, "tips": ["Detail your achievements under each experience entry."]}
        words = len(experience_text.split())
        score = min(100, words // 2)
        return {"score": max(50, score), "tips": ["Use STAR method bullet points under each job position."]}

    @staticmethod
    def recommend_banner(job_title: str) -> Dict[str, Any]:
        return {
            "title": f"Custom {job_title or 'Tech'} Header Banner",
            "dimensions": "1584 x 396 px",
            "theme_recommendation": "Modern gradient with tech stack icons and professional tagline.",
            "color_palettes": ["Navy Blue & Electric Indigo", "Slate Dark & Cyan Accent", "Deep Purple & Emerald"]
        }

    # ── AI Generators ───────────────────────────────────────────────────────
    @classmethod
    def generate_ai_headline(cls, headline: str, job_title: str, skills: str) -> str:
        if gemini_available():
            try:
                prompt = (
                    f"Create 1 high-impact LinkedIn headline (under 220 chars) for:\n"
                    f"Role: {job_title or 'Software Engineer'}\n"
                    f"Skills/Input: {skills or headline}\n"
                    f"Format: Job Title | Core Tech Stack | Value Proposition\n"
                    f"Return ONLY the headline text."
                )
                return gemini_generate(prompt, temperature=0.7, timeout=8)
            except Exception as e:
                logger.warning(f"[LinkedInOptimizer] AI headline fallback: {e}")

        clean_title = job_title or "Software Engineer"
        clean_skills = skills[:40] if skills else "Python | React | Cloud"
        return f"{clean_title} | {clean_skills} | Building High-Performance Solutions"

    @classmethod
    def generate_ai_about(cls, about: str, job_title: str, skills: str) -> str:
        if gemini_available():
            try:
                prompt = (
                    f"Write a 3-paragraph professional LinkedIn 'About' section for a {job_title or 'Professional'}.\n"
                    f"Existing Info: {about or skills}\n"
                    f"Include: Career overview, Core Technical & Soft Skills, Call to Action.\n"
                    f"Return ONLY the formatted text."
                )
                return gemini_generate(prompt, temperature=0.7, timeout=10)
            except Exception as e:
                logger.warning(f"[LinkedInOptimizer] AI about fallback: {e}")

        clean_title = job_title or "Professional"
        return (
            f"I am a passionate {clean_title} dedicated to building scalable, high-impact solutions. "
            f"With expertise across modern technologies and frameworks, I specialize in transforming complex business challenges into elegant technical architectures.\n\n"
            f"Core Competencies: {skills or 'Problem Solving, Technical Architecture, Team Leadership'}\n\n"
            f"Feel free to connect or reach out via email to discuss new opportunities or collaborations!"
        )

    @classmethod
    def generate_ai_experience(cls, experience: str, job_title: str) -> List[str]:
        if gemini_available():
            try:
                prompt = (
                    f"Generate 3 high-impact LinkedIn experience bullet points in STAR format for a {job_title or 'Engineer'}.\n"
                    f"Existing experience context: {experience}\n"
                    f"Return ONLY 3 bullet points starting with action verbs."
                )
                raw = gemini_generate(prompt, temperature=0.7, timeout=8)
                return [line.strip("•*- 123456789.") for line in raw.split("\n") if line.strip()][:3]
            except Exception as e:
                logger.warning(f"[LinkedInOptimizer] AI experience fallback: {e}")

        return [
            f"Spearheaded core system development for {job_title or 'key products'}, delivering 25% performance improvement.",
            "Engineered scalable backend/frontend features using industry best practices and automated CI/CD pipelines.",
            "Collaborated with cross-functional teams to resolve critical production bottlenecks and accelerate release cycles."
        ]
