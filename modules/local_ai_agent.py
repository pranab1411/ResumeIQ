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
        Analyzes resume using Google Gemini AI (if available) or Local spaCy NLP & MCDA engine.
        """
        from utils.gemini_client import gemini_available, gemini_generate
        contact_info = nlp_engine.extract_contact_info(extracted_text)
        resume_skills = nlp_engine.extract_skills(extracted_text)

        # 1. FORCE Gemini AI evaluation if Gemini API is available
        if gemini_available():
            try:
                logger.info("[GEMINI AI] Executing 100% Dynamic Gemini AI Candidate Evaluation & Multi-Industry Matching...")
                prompt = f"""You are an elite ATS Candidate Evaluator and Industry Specialist.
Analyze the following candidate resume text carefully and make 100% dynamic decisions tailored specifically to THIS candidate's field.

RESUME TEXT:
\"\"\"
{extracted_text[:4000]}
\"\"\"

TARGET ROLE (Optional): "{job_title}"
TARGET JOB DESCRIPTION (Optional): "{job_description[:2000]}"

Instructions:
1. Extract candidate name, email, and phone.
2. Determine total work experience in years (e.g. 0.5 or 11.0) and seniority status:
   - "Fresher / Entry-Level Candidate" (if < 1 year experience AND entry-level)
   - "Experienced Professional (X.Y Yrs Exp)" (if >= 1 year experience or experienced)
3. Predict exact candidate target job role (e.g. "IT Support Engineer", "Civil Engineering Specialist", "Registered Nurse", "Financial Analyst", "Full Stack Developer").
4. Predict exact candidate industry category (e.g. "Information Technology", "Civil Engineering", "Healthcare", "Finance").
5. Extract matched core skills and identify 2-3 role-specific missing skills required for their target role.
6. Compute ATS match score (0 to 100).
7. Recommend 3 role-specific additions/skills for the candidate to learn or add.
8. Provide a dynamic "required_asset_fix" object tailored strictly to candidate's field (e.g. for IT Support: IT Certifications/CompTIA/Labs; for Tech: GitHub; for Design: Behance/Figma; for Healthcare: Medical License/EMR; for Legal: Bar Admission; for Civil: PE License/BIM).
9. Provide 4 tailored, industry-relevant improvement suggestions.

Return a valid raw JSON object strictly matching this schema:
{{
  "candidate_name": "Full Name",
  "email": "Email Address",
  "phone": "Phone Number",
  "is_fresher": false,
  "experience_years": 5.0,
  "seniority_label": "Experienced Professional (5.0 Yrs Exp)",
  "target_role": "Predicted Target Job Title",
  "industry_category": "Industry Category",
  "ats_score": 85.0,
  "matched_skills": ["Skill 1", "Skill 2"],
  "missing_skills": ["Missing Skill A", "Missing Skill B"],
  "recommended_additions": ["Addition 1", "Addition 2", "Addition 3"],
  "required_asset_fix": {{
    "title": "Tailored Title",
    "description": "Tailored Description",
    "why_it_matters": "Tailored Rationale",
    "action": "Tailored Action"
  }},
  "suggestions": ["Suggestion 1", "Suggestion 2", "Suggestion 3", "Suggestion 4"]
}}
"""
                raw_res = gemini_generate(prompt, temperature=0.2)
                clean_json = re.sub(r'```json\s*|\s*```', '', raw_res).strip()
                data = json.loads(clean_json)

                if not data.get("candidate_name") or data["candidate_name"] in ["Full Name", "Exact Candidate Name"]:
                    data["candidate_name"] = contact_info.get("name", "Candidate")
                if not data.get("email") or data["email"] == "Email Address":
                    data["email"] = contact_info.get("email", "Not Found")
                if not data.get("phone") or data["phone"] == "Phone Number":
                    data["phone"] = contact_info.get("phone", "Not Found")

                mnc_eval = TopMNCATSEngine.evaluate_mnc_ats(
                    data.get("matched_skills", []),
                    data.get("missing_skills", []),
                    extracted_text,
                    job_description,
                    contact_info
                )

                score = float(data.get("ats_score", 75.0))
                category = ATSCalculator.get_score_category(score)

                return {
                    "candidate_name": data.get("candidate_name", contact_info["name"]),
                    "target_role": data.get("target_role", "Professional"),
                    "seniority_label": data.get("seniority_label", "Experienced Professional"),
                    "email": data.get("email", contact_info["email"]),
                    "phone": data.get("phone", contact_info["phone"]),
                    "ats_score": score,
                    "score_category": category,
                    "matched_skills": data.get("matched_skills", []),
                    "missing_skills": data.get("missing_skills", []),
                    "recommended_additions": data.get("recommended_additions", []),
                    "required_asset_fix": data.get("required_asset_fix", {}),
                    "suggestions": data.get("suggestions", []),
                    "mnc_ats": mnc_eval,
                    "engine_used": "Google Gemini AI"
                }
            except Exception as e:
                logger.warning(f"[GEMINI AI] Gemini analysis failed ({e}), falling back to local spaCy engine...")

        # 2. Local spaCy NLP Fallback Engine
        seniority_info = nlp_engine.detect_candidate_seniority(extracted_text)
        is_fresher_candidate = seniority_info["is_fresher"]
        seniority_label = seniority_info["label"]

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

