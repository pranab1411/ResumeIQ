import re
from typing import Dict, Any, List, Optional
from modules.nlp_engine import nlp_engine
from modules.ats_calculator import ATSCalculator
from modules.mnc_ats_engine import TopMNCATSEngine
from utils.logger import logger

class LocalAIAgent:
    """
    Local Resume Intelligence & Optimization Engine for ResumeIQ.
    Operates locally on-device using spaCy NLP, Multi-Criteria Decision Analysis (MCDA),
    and rule-based heuristic templates without requiring external API keys or network calls.
    """
    def __init__(self):
        logger.info("Initialized Local Resume Intelligence Engine.")

    def is_available(self) -> bool:
        return True

    def analyze_resume(
        self,
        extracted_text: str,
        job_title: str = "",
        job_description: str = "",
        mode: str = "experienced"
    ) -> Dict[str, Any]:
        """
        Analyzes resume using NLP, Top MNC ATS Engines (Workday, Taleo, Greenhouse, Lever, iCIMS), and rule-based heuristics.
        """
        contact_info = nlp_engine.extract_contact_info(extracted_text)
        resume_skills = nlp_engine.extract_skills(extracted_text)

        if mode == "fresher":
            # Fresher mode: focus on technical skills, education, projects & contact completeness
            score, matched_skills, missing_skills = ATSCalculator.calculate_score(
                resume_skills,
                [],
                resume_text=extracted_text,
                contact_info=contact_info
            )
            category = ATSCalculator.get_score_category(score)
            
            mnc_eval = TopMNCATSEngine.evaluate_mnc_ats(resume_skills, [], extracted_text, job_description, contact_info)

            suggestions = [
                "Structure & Section Hierarchy: Place your Name, Contact Info (Email, Phone, LinkedIn, GitHub) at the top, followed immediately by Career Objective, Education, Academic/Personal Projects, and Technical Skills.",
                "Typography & Font Hierarchy: Use clean sans-serif fonts (Calibri, Arial, or Inter) with Name (20–24pt bold), Section Headers (14–16pt bold UPPERCASE), Body text (10–11pt regular).",
                "Attention-Grabbing Headlines: Use bold action-oriented project titles with live GitHub/Portfolio links to capture recruiter interest immediately.",
                "Visual Layout & Margins: Maintain 0.75-inch margins and uniform bullet line-spacing to present a well-balanced 1-page fresher resume."
            ]
            suggestions.extend(mnc_eval.get("insights", []))

            extracted_role = job_title or nlp_engine.extract_target_role(extracted_text, "Fresher / Entry-Level Role")

            return {
                "candidate_name": contact_info["name"],
                "target_role": extracted_role,
                "email": contact_info["email"],
                "phone": contact_info["phone"],
                "ats_score": score,
                "score_category": category,
                "matched_skills": matched_skills,
                "missing_skills": missing_skills,
                "suggestions": suggestions,
                "mnc_ats": mnc_eval
            }

        else:
            # Experienced mode: Full Job Description 4-Pillar ATS Matching across Top MNC Engines
            jd_skills = nlp_engine.extract_keywords_from_jd(job_description) if job_description else []
            score, matched, missing = ATSCalculator.calculate_score(
                resume_skills,
                jd_skills,
                resume_text=extracted_text,
                jd_text=job_description,
                contact_info=contact_info
            )
            category = ATSCalculator.get_score_category(score)
            
            mnc_eval = TopMNCATSEngine.evaluate_mnc_ats(resume_skills, jd_skills, extracted_text, job_description, contact_info)
            
            suggestions = ATSCalculator.generate_suggestions(score, matched, missing, contact_info, extracted_text, mode="experienced")
            for insight in mnc_eval.get("insights", []):
                if insight not in suggestions:
                    suggestions.append(insight)

            extracted_role = job_title or nlp_engine.extract_target_role(extracted_text, "Experienced Professional")

            return {
                "candidate_name": contact_info["name"],
                "target_role": extracted_role,
                "email": contact_info["email"],
                "phone": contact_info["phone"],
                "ats_score": score,
                "score_category": category,
                "matched_skills": matched,
                "missing_skills": missing,
                "suggestions": suggestions,
                "mnc_ats": mnc_eval
            }

local_ai_agent = LocalAIAgent()

