"""
modules/ats_benchmark.py
ATS Benchmark Engine for ResumeIQ v2.0
Provides industry benchmarks, company ATS profiles, percentile ranking,
and ATS pass probability calculations.
"""

import json
import os
import math
from typing import Dict, Any, Optional
from utils.logger import logger

_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "ats_config.json")

def _load_config() -> Dict:
    try:
        with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.warning(f"[ATSBenchmark] Could not load ats_config.json: {e}")
        return {}

_CFG = _load_config()


class ATSBenchmarkEngine:
    """
    Provides ATS benchmarking, percentile ranking, pass probability,
    and company-specific ATS simulation.
    """

    # ── Pillar Weights ──────────────────────────────────────────────────────
    @staticmethod
    def get_pillar_weights(company: Optional[str] = None) -> Dict[str, float]:
        """Return pillar weights, optionally overridden by company profile."""
        defaults = _CFG.get("pillar_weights", {
            "skills": 0.40, "keywords": 0.25, "format": 0.20, "experience": 0.15
        })
        if company:
            profile = _CFG.get("company_ats_profiles", {}).get(company, {})
            override = profile.get("weight_override")
            if override:
                return override
        return defaults

    # ── Industry Benchmark ──────────────────────────────────────────────────
    @staticmethod
    def get_industry_benchmark(industry: str = "General") -> Dict[str, Any]:
        """Return benchmark data for an industry."""
        benchmarks = _CFG.get("industry_benchmarks", {})
        return benchmarks.get(industry, benchmarks.get("General", {
            "avg_score": 62, "pass_threshold": 60, "top_percentile": 80
        }))

    @staticmethod
    def get_all_industries() -> list:
        return list(_CFG.get("industry_benchmarks", {}).keys())

    # ── Company ATS Profile ─────────────────────────────────────────────────
    @staticmethod
    def get_company_profile(company: str) -> Optional[Dict[str, Any]]:
        return _CFG.get("company_ats_profiles", {}).get(company)

    @staticmethod
    def get_all_companies() -> list:
        return list(_CFG.get("company_ats_profiles", {}).keys())

    # ── Percentile Ranking ──────────────────────────────────────────────────
    @staticmethod
    def get_percentile(score: float) -> int:
        """
        Return approximate resume ranking percentile (0–100) based on
        the score distribution curve in ats_config.json.
        """
        dist = _CFG.get("score_distribution", [
            10, 18, 28, 38, 47, 55, 62, 68, 74, 79, 83, 87, 90, 93, 95, 97, 98, 99, 99, 100
        ])
        # dist[i] = % of resumes scoring <= (i+1)*5 points
        bucket = min(int(score / 5), len(dist) - 1)
        return dist[bucket]

    @staticmethod
    def get_percentile_label(percentile: int) -> str:
        if percentile >= 90:
            return "Top 10%"
        elif percentile >= 75:
            return "Top 25%"
        elif percentile >= 50:
            return "Top 50%"
        elif percentile >= 25:
            return "Bottom 50%"
        else:
            return "Bottom 25%"

    # ── ATS Pass Probability ────────────────────────────────────────────────
    @staticmethod
    def get_pass_probability(
        score: float,
        industry: str = "General",
        company: Optional[str] = None
    ) -> float:
        """
        Returns ATS pass probability (0–100%) using a logistic curve
        centered at the industry/company pass threshold.
        """
        if company:
            profile = ATSBenchmarkEngine.get_company_profile(company)
            threshold = profile.get("min_pass_score", 65) if profile else 65
        else:
            benchmark = ATSBenchmarkEngine.get_industry_benchmark(industry)
            threshold = benchmark.get("pass_threshold", 60)

        # Logistic sigmoid: P = 1 / (1 + e^(-k*(score - threshold)))
        k = 0.12  # steepness
        prob = 1.0 / (1.0 + math.exp(-k * (score - threshold)))
        return round(prob * 100.0, 1)

    # ── Resume Quality Index (RQI) ──────────────────────────────────────────
    @staticmethod
    def calculate_rqi(resume_text: str, contact_info: Dict = None) -> float:
        """
        Resume Quality Index (0–100): measures structural completeness.
        Sections, contact info, length, links, sections order.
        """
        if not resume_text:
            return 0.0
        score = 0.0
        text_lower = resume_text.lower()

        # 1. Essential sections (40 pts)
        essential = {
            "contact": any(k in text_lower for k in ["email", "phone", "mobile", "@"]),
            "education": any(k in text_lower for k in ["education", "degree", "university", "college", "b.tech", "bachelor"]),
            "experience": any(k in text_lower for k in ["experience", "employment", "work history", "worked at"]),
            "skills": any(k in text_lower for k in ["skills", "technologies", "tools", "competencies"]),
        }
        score += sum(10.0 for v in essential.values() if v)

        # 2. Optional enhancement sections (20 pts)
        optional = ["projects", "certifications", "achievements", "awards", "publications", "volunteer", "interests"]
        found_opt = sum(1 for s in optional if s in text_lower)
        score += min(20.0, found_opt * 5.0)

        # 3. Contact completeness (20 pts)
        if contact_info:
            if contact_info.get("email", "Not Found") != "Not Found":
                score += 7.0
            if contact_info.get("phone", "Not Found") != "Not Found":
                score += 7.0
            if contact_info.get("linkedin", "Not Found") != "Not Found":
                score += 6.0
        else:
            import re
            if re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', resume_text):
                score += 7.0
            if re.search(r'[\+\(]?\d[\d\s\-\(\)]{8,}', resume_text):
                score += 7.0
            if "linkedin.com" in text_lower:
                score += 6.0

        # 4. Document length adequacy (20 pts)
        words = len(resume_text.split())
        if words >= 400:
            score += 20.0
        elif words >= 200:
            score += 10.0
        elif words >= 100:
            score += 5.0

        return round(min(100.0, score), 1)

    # ── Resume Confidence Score ─────────────────────────────────────────────
    @staticmethod
    def calculate_confidence_score(
        resume_text: str,
        matched_skills: list,
        ats_score: float
    ) -> float:
        """
        Resume Confidence Score (0–100): how confident we are the resume
        will perform well in real ATS systems.
        Combines: ATS score reliability + skill evidence + content richness.
        """
        if not resume_text:
            return 0.0
        import re
        text_lower = resume_text.lower()
        score = 0.0

        # Component 1: ATS score weight (40%)
        score += ats_score * 0.40

        # Component 2: Matched skills density (30%)
        skill_conf = min(100.0, len(matched_skills) * 8.0)
        score += skill_conf * 0.30

        # Component 3: Action verb richness (15%)
        strong_verbs = ["led", "built", "developed", "architected", "designed", "launched",
                        "optimized", "reduced", "increased", "created", "managed", "delivered",
                        "implemented", "spearheaded", "achieved", "generated", "automated"]
        verbs_found = sum(1 for v in strong_verbs if v in text_lower)
        verb_score = min(100.0, verbs_found * 10.0)
        score += verb_score * 0.15

        # Component 4: Quantified impact metrics (15%)
        metrics = re.findall(r'\b\d+[\%\+]|\$\d+|\d+\s+(?:users|clients|projects|systems|teams?)\b', text_lower)
        metric_score = min(100.0, len(metrics) * 15.0)
        score += metric_score * 0.15

        return round(min(100.0, score), 1)

    # ── Resume Readiness Score ──────────────────────────────────────────────
    @staticmethod
    def calculate_readiness_score(
        ats_score: float,
        rqi: float,
        confidence: float
    ) -> float:
        """
        Resume Readiness Score: composite of ATS, RQI, and Confidence.
        """
        readiness = (ats_score * 0.50) + (rqi * 0.25) + (confidence * 0.25)
        return round(min(100.0, readiness), 1)

    # ── Optimization Checklist ──────────────────────────────────────────────
    @staticmethod
    def generate_optimization_checklist(
        resume_text: str,
        matched_skills: list,
        missing_skills: list,
        contact_info: Dict = None,
        industry: str = "General",
        company: Optional[str] = None
    ) -> list:
        """
        Returns a list of checklist dicts with status (pass/fail/warn) and message.
        """
        import re
        text_lower = resume_text.lower() if resume_text else ""
        checklist = []

        def item(label, passed, message, priority="medium"):
            return {"label": label, "passed": passed, "message": message, "priority": priority}

        # Contact
        has_email = bool(re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', resume_text or ""))
        has_phone = bool(re.search(r'[\+\(]?\d[\d\s\-\(\)]{8,}', resume_text or ""))
        has_linkedin = "linkedin.com" in text_lower
        checklist.append(item("Email Address Present", has_email, "Add a professional email address." if not has_email else "Email found.", "high"))
        checklist.append(item("Phone Number Present", has_phone, "Add a contact phone number." if not has_phone else "Phone found.", "high"))
        checklist.append(item("LinkedIn Profile Linked", has_linkedin, "Add your LinkedIn profile URL." if not has_linkedin else "LinkedIn found.", "medium"))

        # Sections
        has_skills_section = any(k in text_lower for k in ["skills", "technologies", "competencies"])
        has_exp_section = any(k in text_lower for k in ["experience", "employment", "work history"])
        has_edu_section = any(k in text_lower for k in ["education", "degree", "university"])
        has_proj_section = any(k in text_lower for k in ["projects", "portfolio"])
        checklist.append(item("Skills Section Present", has_skills_section, "Add a dedicated Skills section." if not has_skills_section else "Skills section found.", "high"))
        checklist.append(item("Experience Section Present", has_exp_section, "Add a Work Experience section." if not has_exp_section else "Experience section found.", "high"))
        checklist.append(item("Education Section Present", has_edu_section, "Add an Education section." if not has_edu_section else "Education section found.", "high"))
        checklist.append(item("Projects Section Present", has_proj_section, "Add a Projects section to showcase your work." if not has_proj_section else "Projects section found.", "medium"))

        # Content quality
        action_verbs = ["led", "built", "developed", "implemented", "created", "managed", "optimized", "designed", "launched", "achieved"]
        has_verbs = any(v in text_lower for v in action_verbs)
        checklist.append(item("Action Verbs Used", has_verbs, "Use strong action verbs like 'Led', 'Built', 'Developed'." if not has_verbs else "Action verbs found.", "medium"))

        has_metrics = bool(re.search(r'\b\d+[\%\+]|\$\d+|\d+\s+(?:users|clients|projects)', text_lower))
        checklist.append(item("Quantified Achievements", has_metrics, "Add measurable results (e.g., 'Improved performance by 30%')." if not has_metrics else "Quantified achievements found.", "high"))

        # Skills coverage
        skill_coverage = (len(matched_skills) / max(1, len(matched_skills) + len(missing_skills))) * 100
        has_good_coverage = skill_coverage >= 60
        checklist.append(item(
            f"Skill Coverage ≥ 60% ({skill_coverage:.0f}%)",
            has_good_coverage,
            f"Add missing skills: {', '.join(missing_skills[:4])}." if missing_skills else "Excellent skill coverage.",
            "high"
        ))

        # Word count
        word_count = len((resume_text or "").split())
        has_good_length = word_count >= 300
        checklist.append(item(
            f"Resume Length Adequate ({word_count} words)",
            has_good_length,
            "Resume is too short. Aim for 400–700 words for experienced roles." if not has_good_length else "Good resume length.",
            "medium"
        ))

        # Company-specific
        if company:
            profile = ATSBenchmarkEngine.get_company_profile(company)
            if profile:
                boost_kw = profile.get("boost_keywords", [])
                found_boost = [kw for kw in boost_kw if kw.lower() in text_lower]
                has_company_kw = len(found_boost) >= 2
                checklist.append(item(
                    f"{company} ATS Keywords",
                    has_company_kw,
                    f"Add {company}-preferred keywords: {', '.join(boost_kw[:4])}." if not has_company_kw else f"{company} keywords found: {', '.join(found_boost[:3])}.",
                    "high"
                ))

        return checklist

    # ── Company ATS Score Simulation ────────────────────────────────────────
    @staticmethod
    def simulate_company_ats(
        base_score: float,
        resume_text: str,
        matched_skills: list,
        company: str
    ) -> Dict[str, Any]:
        """
        Simulate how a specific company's ATS would score this resume.
        Returns adjusted score, pass/fail, and company-specific feedback.
        """
        profile = ATSBenchmarkEngine.get_company_profile(company)
        if not profile:
            return {"company": company, "score": base_score, "passed": base_score >= 65, "feedback": []}

        text_lower = (resume_text or "").lower()
        boost_kw = profile.get("boost_keywords", [])
        found_boost = [kw for kw in boost_kw if kw.lower() in text_lower]
        boost_factor = (len(found_boost) / max(1, len(boost_kw))) * 15.0  # up to +15 pts

        weights = profile.get("weight_override", ATSBenchmarkEngine.get_pillar_weights())
        # Recalculate with company weights (simplified)
        skill_score = min(100.0, len(matched_skills) * 8.0)
        company_score = round(min(100.0, base_score * 0.85 + boost_factor + (skill_score * weights["skills"] * 0.15)), 1)

        threshold = profile.get("min_pass_score", 65)
        passed = company_score >= threshold

        feedback = []
        missing_boost = [kw for kw in boost_kw if kw.lower() not in text_lower]
        if missing_boost:
            feedback.append(f"Add {company}-preferred keywords: {', '.join(missing_boost[:3])}")
        if not passed:
            feedback.append(f"Score {company_score:.0f}% is below {company}'s minimum threshold of {threshold}%")
        else:
            feedback.append(f"Score {company_score:.0f}% meets {company}'s ATS requirements ✓")

        return {
            "company": company,
            "score": company_score,
            "passed": passed,
            "threshold": threshold,
            "keyword_boost": round(boost_factor, 1),
            "found_keywords": found_boost,
            "feedback": feedback
        }

    # ── Full ATS Analysis Result ────────────────────────────────────────────
    @staticmethod
    def build_full_analysis(
        ats_score: float,
        pillar_scores: Dict[str, float],
        resume_text: str,
        matched_skills: list,
        missing_skills: list,
        contact_info: Dict = None,
        industry: str = "General",
        company: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Builds the complete v2.0 ATS analysis result dictionary.
        """
        rqi = ATSBenchmarkEngine.calculate_rqi(resume_text, contact_info)
        confidence = ATSBenchmarkEngine.calculate_confidence_score(resume_text, matched_skills, ats_score)
        readiness = ATSBenchmarkEngine.calculate_readiness_score(ats_score, rqi, confidence)
        percentile = ATSBenchmarkEngine.get_percentile(ats_score)
        pass_prob = ATSBenchmarkEngine.get_pass_probability(ats_score, industry, company)
        benchmark = ATSBenchmarkEngine.get_industry_benchmark(industry)
        checklist = ATSBenchmarkEngine.generate_optimization_checklist(
            resume_text, matched_skills, missing_skills, contact_info, industry, company
        )
        company_sim = ATSBenchmarkEngine.simulate_company_ats(ats_score, resume_text, matched_skills, company) if company else None

        return {
            "ats_score": ats_score,
            "pillar_scores": pillar_scores,
            "rqi": rqi,
            "confidence_score": confidence,
            "readiness_score": readiness,
            "percentile": percentile,
            "percentile_label": ATSBenchmarkEngine.get_percentile_label(percentile),
            "pass_probability": pass_prob,
            "industry": industry,
            "industry_avg": benchmark.get("avg_score", 62),
            "industry_threshold": benchmark.get("pass_threshold", 60),
            "company_simulation": company_sim,
            "optimization_checklist": checklist,
            "checklist_pass_count": sum(1 for c in checklist if c["passed"]),
            "checklist_total": len(checklist),
        }
