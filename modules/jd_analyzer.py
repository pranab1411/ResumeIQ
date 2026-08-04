"""
modules/jd_analyzer.py
Job Description Analyzer Engine for ResumeIQ v2.0.
Extracts required/preferred skills, responsibilities, seniority level,
education/exp requirements, industry detection, company type, ATS predictions,
and AI recommendations via Gemini.
"""

import json
import os
import re
from typing import Dict, Any, List, Optional
from utils.logger import logger
from utils.gemini_client import gemini_generate, gemini_available
from modules.nlp_engine import nlp_engine

_INDUSTRY_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "industry_profiles.json")

def _load_industry_profiles() -> Dict:
    try:
        if os.path.exists(_INDUSTRY_PATH):
            with open(_INDUSTRY_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        logger.warning(f"[JDAnalyzer] Failed to load industry_profiles.json: {e}")
    return {}

_INDUSTRIES = _load_industry_profiles()

class JDAnalyzer:
    @classmethod
    def analyze_jd(cls, jd_text: str, resume_skills: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Performs comprehensive Job Description analysis.
        """
        if not jd_text or not jd_text.strip():
            return cls._empty_result()

        text_lower = jd_text.lower()

        # 1. Skill Extraction
        all_skills = nlp_engine.extract_skills(jd_text)
        required_skills = []
        preferred_skills = []

        # Split skills into required vs preferred based on context
        for s in all_skills:
            pos = text_lower.find(s.lower())
            if pos != -1:
                context = text_lower[max(0, pos-50):min(len(text_lower), pos+50)]
                if any(kw in context for kw in ["plus", "preferred", "nice to have", "bonus", "optional"]):
                    preferred_skills.append(s)
                else:
                    required_skills.append(s)
            else:
                required_skills.append(s)

        if not required_skills:
            required_skills = all_skills

        # 2. Industry Detection
        industry = cls._detect_industry(jd_text)

        # 3. Company Type Classification
        company_type = cls._detect_company_type(jd_text)

        # 4. Seniority Level Detection
        seniority = cls._detect_seniority(jd_text)

        # 5. Education & Experience Requirements
        education_req = cls._detect_education_req(jd_text)
        exp_years_req = cls._detect_experience_req(jd_text)

        # 6. Responsibilities Extraction
        responsibilities = cls._extract_responsibilities(jd_text)

        # 7. Keyword Density Calculation
        keyword_density = cls._calculate_keyword_density(jd_text, all_skills)

        # 8. Resume Coverage & Skill Matching (if resume_skills provided)
        matched_skills = []
        missing_skills = []
        coverage_score = 0.0

        if resume_skills:
            res_norm = {nlp_engine.known_skills_flat.get(s.lower(), s.lower()): s for s in resume_skills}
            for req in required_skills:
                norm_req = nlp_engine.known_skills_flat.get(req.lower(), req.lower())
                if norm_req in res_norm or req in resume_skills:
                    matched_skills.append(req)
                else:
                    missing_skills.append(req)

            total_req = len(required_skills) if required_skills else 1
            coverage_score = round((len(matched_skills) / total_req) * 100.0, 1)

        # 9. AI Recommendations via Gemini (if available)
        ai_recommendations = cls._generate_ai_recommendations(jd_text, required_skills, missing_skills)

        return {
            "required_skills": required_skills,
            "preferred_skills": preferred_skills,
            "all_extracted_skills": all_skills,
            "industry": industry,
            "company_type": company_type,
            "seniority_level": seniority,
            "education_requirement": education_req,
            "experience_years_requirement": exp_years_req,
            "responsibilities": responsibilities,
            "keyword_density": keyword_density,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "coverage_score": coverage_score,
            "ai_recommendations": ai_recommendations,
        }

    @staticmethod
    def _detect_industry(jd_text: str) -> str:
        text_lower = jd_text.lower()
        scores = {}
        for ind, data in _INDUSTRIES.items():
            score = 0
            for skill in data.get("common_skills", []):
                if skill.lower() in text_lower:
                    score += 2
            scores[ind] = score

        best = max(scores, key=scores.get) if scores else "General"
        return best if scores.get(best, 0) > 0 else "General"

    @staticmethod
    def _detect_company_type(jd_text: str) -> str:
        text_lower = jd_text.lower()
        if any(k in text_lower for k in ["fortune 500", "multinational", "mnc", "global enterprise"]):
            return "MNC Enterprise"
        elif any(k in text_lower for k in ["startup", "early stage", "fast-paced startup", "series a", "seed"]):
            return "Startup"
        elif any(k in text_lower for k in ["mid-market", "growing company", "mid-sized"]):
            return "Mid-Market"
        else:
            return "Enterprise"

    @staticmethod
    def _detect_seniority(jd_text: str) -> str:
        text_lower = jd_text.lower()
        if any(k in text_lower for k in ["principal", "director", "head of", "vp", "chief"]):
            return "Executive / Lead"
        elif any(k in text_lower for k in ["senior", "sr.", "lead", "staff"]):
            return "Senior"
        elif any(k in text_lower for k in ["junior", "jr.", "entry level", "fresher", "intern", "associate"]):
            return "Junior / Entry"
        else:
            return "Mid-Level"

    @staticmethod
    def _detect_education_req(jd_text: str) -> str:
        text_lower = jd_text.lower()
        if "phd" in text_lower or "doctorate" in text_lower:
            return "Ph.D. / Doctorate Required"
        elif any(k in text_lower for k in ["master", "m.tech", "m.s.", "mba"]):
            return "Master's Degree Preferred"
        elif any(k in text_lower for k in ["bachelor", "b.tech", "b.s.", "degree in computer science", "engineering degree"]):
            return "Bachelor's Degree Required"
        else:
            return "Bachelor's Degree or Equivalent Experience"

    @staticmethod
    def _detect_experience_req(jd_text: str) -> str:
        m = re.search(r'(\d+)\+?\s*(?:-\s*\d+)?\s*years?', jd_text, re.IGNORECASE)
        if m:
            return f"{m.group(1)}+ Years Required"
        return "1-3 Years Experience"

    @staticmethod
    def _extract_responsibilities(jd_text: str) -> List[str]:
        lines = [line.strip("•*- ") for line in jd_text.split("\n") if line.strip()]
        resp = []
        capture = False
        for line in lines:
            if any(k in line.lower() for k in ["responsibilities", "duties", "what you will do", "role overview"]):
                capture = True
                continue
            if capture:
                if any(k in line.lower() for k in ["requirements", "qualifications", "skills", "benefits", "about us"]):
                    break
                if len(line) > 15:
                    resp.append(line)
        return resp[:8]

    @staticmethod
    def _calculate_keyword_density(jd_text: str, skills: List[str]) -> List[Dict[str, Any]]:
        words = re.findall(r'\w+', jd_text.lower())
        total_words = max(1, len(words))
        density = []
        for s in skills:
            count = len(re.findall(r'\b' + re.escape(s.lower()) + r'\b', jd_text.lower()))
            pct = round((count / total_words) * 100.0, 2)
            density.append({"keyword": s, "count": count, "density_pct": pct})
        density.sort(key=lambda x: x["count"], reverse=True)
        return density[:10]

    @staticmethod
    def _generate_ai_recommendations(jd_text: str, required_skills: List[str], missing_skills: List[str]) -> List[str]:
        if gemini_available():
            try:
                prompt = (
                    f"Analyze this Job Description and provide 3 short actionable resume optimization suggestions.\n"
                    f"Required Skills: {', '.join(required_skills[:8])}\n"
                    f"Missing Skills in Resume: {', '.join(missing_skills[:5])}\n"
                    f"Return ONLY 3 bullet points, no extra preamble."
                )
                raw = gemini_generate(prompt, timeout=8)
                bullets = [line.strip("•*- 123456789.") for line in raw.split("\n") if line.strip()]
                if bullets:
                    return bullets[:3]
            except Exception as e:
                logger.warning(f"[JDAnalyzer] Gemini AI recommendation fallback: {e}")

        # Fallback rule-based recommendations
        recs = []
        if missing_skills:
            recs.append(f"Incorporate missing core skills: {', '.join(missing_skills[:3])} into your experience bullet points.")
        recs.append("Highlight quantifiable impact (%, $, project scale) matching the role's primary responsibilities.")
        recs.append("Ensure your summary section explicitly mentions the target job title.")
        return recs

    @staticmethod
    def _empty_result() -> Dict[str, Any]:
        return {
            "required_skills": [],
            "preferred_skills": [],
            "all_extracted_skills": [],
            "industry": "General",
            "company_type": "Enterprise",
            "seniority_level": "Mid-Level",
            "education_requirement": "Not Specified",
            "experience_years_requirement": "Not Specified",
            "responsibilities": [],
            "keyword_density": [],
            "matched_skills": [],
            "missing_skills": [],
            "coverage_score": 0.0,
            "ai_recommendations": []
        }
