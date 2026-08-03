"""
Top MNC ATS Engine Registry & Multi-System Scoring Module for ResumeIQ.
Evaluates candidate resumes against real-world parsing rules used by top MNC ATS platforms:
- Workday ATS (Google, Meta, Adobe, Salesforce, IBM)
- Oracle Taleo ATS (Apple, Accenture, Deloitte, Bank of America)
- Greenhouse ATS (Stripe, Airbnb, Uber, GitHub)
- Lever ATS (Netflix, Spotify, Shopify, Lyft)
- iCIMS ATS (Amazon, Microsoft, FedEx, Target)
"""

import re
from typing import Dict, List, Any, Tuple
from utils.logger import logger
from modules.ats_calculator import ATSCalculator

class TopMNCATSEngine:
    """Multi-Engine Simulator for Top MNC Applicant Tracking Systems."""
    
    SYSTEMS = {
        "workday": {
            "name": "Workday ATS",
            "mncs": ["Google", "Meta", "Adobe", "Salesforce", "IBM"],
            "skill_weight": 0.45,
            "semantic_weight": 0.30,
            "hygiene_weight": 0.15,
            "exp_weight": 0.10,
            "description": "Strict structural hierarchy, exact role title alignment, and core technical skill coverage."
        },
        "taleo": {
            "name": "Oracle Taleo ATS",
            "mncs": ["Apple", "Accenture", "Deloitte", "Boeing", "Bank of America"],
            "skill_weight": 0.50,
            "semantic_weight": 0.15,
            "hygiene_weight": 0.15,
            "exp_weight": 0.20,
            "description": "Dense keyword frequency matching, hard skills priority, and strict experience year thresholds."
        },
        "greenhouse": {
            "name": "Greenhouse ATS",
            "mncs": ["Stripe", "Airbnb", "Uber", "GitHub", "DoorDash"],
            "skill_weight": 0.35,
            "semantic_weight": 0.25,
            "hygiene_weight": 0.30,
            "exp_weight": 0.10,
            "description": "STAR-method action statements, project impact metrics (%, $), and candidate scorecard evaluations."
        },
        "lever": {
            "name": "Lever ATS",
            "mncs": ["Netflix", "Spotify", "Shopify", "Lyft", "Atlassian"],
            "skill_weight": 0.35,
            "semantic_weight": 0.35,
            "hygiene_weight": 0.15,
            "exp_weight": 0.15,
            "description": "Semantic NLP contextual matching, technical skill clusters, and holistic candidate profile building."
        },
        "icims": {
            "name": "iCIMS / Jobvite ATS",
            "mncs": ["Amazon", "Microsoft", "FedEx", "Target", "Comcast"],
            "skill_weight": 0.45,
            "semantic_weight": 0.20,
            "hygiene_weight": 0.20,
            "exp_weight": 0.15,
            "description": "Hard keyword knockout rules, contact information validation, and title proximity matching."
        }
    }

    @classmethod
    def evaluate_mnc_ats(
        cls,
        resume_skills: List[str],
        job_skills: List[str],
        resume_text: str = "",
        jd_text: str = "",
        contact_info: Dict[str, str] = None
    ) -> Dict[str, Any]:
        """
        Evaluates resume across all 5 Top MNC ATS Platforms.
        Returns detailed scores, company breakdown, global MNC average, and MNC-specific feedback.
        """
        if not resume_text and not resume_skills:
            return {
                "mnc_average": 0.0,
                "system_scores": {},
                "insights": []
            }

        # Calculate base 4-Pillar metrics
        skill_score, matched_skills, missing_skills = ATSCalculator.calculate_score(resume_skills, job_skills, resume_text, jd_text, contact_info)
        
        # Skill Match %
        req_normalized = {ATSCalculator._normalize_skill(s): s for s in job_skills} if job_skills else {}
        res_normalized = {ATSCalculator._normalize_skill(s): s for s in resume_skills} if resume_skills else {}
        matched_count = sum(1 for k in req_normalized if k in res_normalized)
        skill_pct = (matched_count / len(req_normalized) * 100.0) if req_normalized else (100.0 if len(resume_skills) >= 5 else len(resume_skills)*20.0)

        # Semantic TF-IDF %
        semantic_pct = ATSCalculator.calculate_tf_idf_similarity(resume_text, jd_text) if resume_text and jd_text else skill_pct

        # Hygiene & Impact %
        hygiene_pct = ATSCalculator.calculate_hygiene_score(resume_text, contact_info) if resume_text else 80.0

        # Experience & Degree Alignment %
        exp_pct = ATSCalculator.calculate_experience_score(resume_text, jd_text) if resume_text else 80.0

        system_scores = {}
        total_score = 0.0

        for key, sys_info in cls.SYSTEMS.items():
            w_skill = sys_info["skill_weight"]
            w_sem = sys_info["semantic_weight"]
            w_hyg = sys_info["hygiene_weight"]
            w_exp = sys_info["exp_weight"]

            calc_score = (w_skill * skill_pct) + (w_sem * semantic_pct) + (w_hyg * hygiene_pct) + (w_exp * exp_pct)
            calc_score = round(min(100.0, max(0.0, calc_score)), 1)
            
            category = ATSCalculator.get_score_category(calc_score)
            stars = ATSCalculator.get_star_rating_gui(calc_score)

            system_scores[key] = {
                "name": sys_info["name"],
                "mncs": sys_info["mncs"],
                "score": calc_score,
                "category": category,
                "stars": stars,
                "description": sys_info["description"]
            }
            total_score += calc_score

        mnc_avg = round(total_score / len(cls.SYSTEMS), 1)

        # Generate MNC Specific Feedback Insights
        insights = []
        if missing_skills:
            insights.append(f"🏢 Taleo & Workday Warning: Missing critical keywords: {', '.join(missing_skills[:4])}.")
        if hygiene_pct < 70.0:
            insights.append("🏢 Greenhouse Alert: Add quantified metrics (e.g. '%', '$', team sizes) to score higher on candidate scorecards.")
        if semantic_pct < 60.0:
            insights.append("🏢 Lever & Workday Alert: Increase industry terminology density to match MNC job description context.")
        if contact_info and (contact_info.get("email") == "Not Found" or contact_info.get("phone") == "Not Found"):
            insights.append("🏢 iCIMS Knockout Warning: Contact details (Email/Phone) could not be parsed clearly.")

        logger.info(f"[MNC ATS ENGINE] Evaluated {len(cls.SYSTEMS)} Top MNC Systems. Global MNC Average: {mnc_avg}%")

        return {
            "mnc_average": mnc_avg,
            "system_scores": system_scores,
            "insights": insights,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills
        }
