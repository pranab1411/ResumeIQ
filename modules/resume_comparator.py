"""
modules/resume_comparator.py
Resume Comparator Engine for ResumeIQ v2.0.
Performs side-by-side diff comparison between Version A and Version B of a resume.
"""

from typing import Dict, Any, List
from modules.ats_calculator import ATSCalculator

class ResumeComparator:
    @classmethod
    def compare_resumes(
        cls,
        resume_a: Dict[str, Any],
        resume_b: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compares Resume A vs Resume B and calculates diff metrics.
        """
        score_a = resume_a.get("ats_score", 0.0)
        score_b = resume_b.get("ats_score", 0.0)
        delta_score = round(score_b - score_a, 1)

        skills_a = set(resume_a.get("skills", []))
        skills_b = set(resume_b.get("skills", []))

        added_skills = list(skills_b - skills_a)
        removed_skills = list(skills_a - skills_b)
        common_skills = list(skills_a.intersection(skills_b))

        text_a = resume_a.get("raw_text", "")
        text_b = resume_b.get("raw_text", "")
        word_count_a = len(text_a.split())
        word_count_b = len(text_b.split())
        delta_words = word_count_b - word_count_a

        return {
            "version_a_title": resume_a.get("filename", "Version A"),
            "version_b_title": resume_b.get("filename", "Version B"),
            "score_a": score_a,
            "score_b": score_b,
            "delta_score": delta_score,
            "improvement_pct": f"+{delta_score}%" if delta_score >= 0 else f"{delta_score}%",
            "added_skills": added_skills,
            "removed_skills": removed_skills,
            "common_skills": common_skills,
            "word_count_a": word_count_a,
            "word_count_b": word_count_b,
            "delta_words": delta_words
        }
