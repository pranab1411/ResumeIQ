"""
modules/job_recommender.py
Job Recommendation Engine for ResumeIQ v2.0.
Predicts top matching job roles, calculates match %, missing skills,
and attaches salary ranges & career growth potential.
"""

import json
import os
from typing import Dict, Any, List
from utils.logger import logger
from modules.ats_calculator import ATSCalculator, ROLE_SKILL_PROFILES

_SALARY_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "salary_data.json")

def _load_salary_data() -> Dict[str, Any]:
    try:
        if os.path.exists(_SALARY_PATH):
            with open(_SALARY_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        logger.warning(f"[JobRecommender] Could not load salary_data.json: {e}")
    return {}

_SALARY_DATA = _load_salary_data()

class JobRecommender:
    @classmethod
    def recommend_jobs(cls, extracted_skills: List[str], top_n: int = 6) -> List[Dict[str, Any]]:
        """
        Recommends top matching job roles based on skills.
        Returns list of dicts with role, match_pct, missing_skills, salary, growth.
        """
        predictions = ATSCalculator.predict_matching_job_roles(extracted_skills, top_n=top_n)
        recommendations = []

        cand_norm = {ATSCalculator._normalize_skill(s) for s in extracted_skills}

        for item in predictions:
            role_name = item["role"]
            profile = ROLE_SKILL_PROFILES.get(role_name, {})
            role_skills = profile.get("skills", [])

            missing = []
            for s in role_skills:
                norm_s = ATSCalculator._normalize_skill(s)
                if norm_s not in cand_norm:
                    missing.append(s)

            salary = _SALARY_DATA.get(role_name, {
                "mid_salary": "$85,000 - $120,000",
                "growth_potential": "High (12% YoY)",
                "top_locations": ["Remote", "Major Metro Areas"]
            })

            recommendations.append({
                "role": role_name,
                "category": item["category"],
                "match_pct": item["match_pct"],
                "matched_skills": item["matched_skills"],
                "missing_skills": missing[:5],
                "mid_salary": salary.get("mid_salary", "$85,000 - $120,000"),
                "entry_salary": salary.get("entry_salary", "$60,000 - $80,000"),
                "senior_salary": salary.get("senior_salary", "$130,000+"),
                "growth_potential": salary.get("growth_potential", "High (12% YoY)"),
                "top_locations": salary.get("top_locations", ["Remote"])
            })

        return recommendations
