"""
modules/ai_copilot.py
AI Resume Copilot Engine for ResumeIQ v2.0.
Context-aware assistant supporting intents: improve resume, explain ATS, rewrite section,
suggest skills/certs/projects. Uses Gemini API with Ollama local LLM fallback.
"""

from typing import Dict, Any, List, Optional
from utils.logger import logger
from utils.gemini_client import gemini_generate, gemini_available

class AICopilot:
    INTENTS = [
        "improve_resume",
        "explain_ats",
        "rewrite_section",
        "suggest_skills",
        "suggest_certifications",
        "suggest_projects"
    ]

    @classmethod
    def chat(
        cls,
        user_message: str,
        resume_context: Optional[Dict[str, Any]] = None,
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Processes user chat message with context awareness.
        """
        context_str = ""
        if resume_context:
            context_str = (
                f"\n--- Candidate Context ---\n"
                f"Candidate Name: {resume_context.get('candidate_name', 'Candidate')}\n"
                f"Target Job Title: {resume_context.get('job_title', 'Software Engineer')}\n"
                f"ATS Score: {resume_context.get('ats_score', 0)}%\n"
                f"Matched Skills: {', '.join(resume_context.get('matched_skills', [])[:8])}\n"
                f"Missing Skills: {', '.join(resume_context.get('missing_skills', [])[:5])}\n"
            )

        prompt = (
            f"You are ResumeIQ AI Copilot, an expert career coach and ATS optimization specialist.\n"
            f"{context_str}\n"
            f"User Question: {user_message}\n\n"
            f"Provide a helpful, direct, and actionable response."
        )

        # 1. Try Gemini API primary
        if gemini_available():
            try:
                reply = gemini_generate(prompt, temperature=0.7, timeout=12)
                return {"reply": reply, "provider": "Gemini AI", "success": True}
            except Exception as e:
                logger.warning(f"[AICopilot] Gemini AI failed ({e}), trying Ollama fallback...")

        # 2. Try Ollama Local Fallback
        ollama_reply = cls._ollama_fallback(prompt)
        if ollama_reply:
            return {"reply": ollama_reply, "provider": "Ollama Local LLM", "success": True}

        # 3. Rule-based fallback
        fallback = cls._rule_based_fallback(user_message, resume_context)
        return {"reply": fallback, "provider": "Rule Engine", "success": True}

    @staticmethod
    def _ollama_fallback(prompt: str) -> Optional[str]:
        try:
            import urllib.request
            import json
            url = "http://localhost:11434/api/generate"
            payload = {"model": "llama3", "prompt": prompt, "stream": False}
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                return res.get("response", "").strip()
        except Exception:
            return None

    @staticmethod
    def _rule_based_fallback(message: str, context: Optional[Dict]) -> str:
        msg_lower = message.lower()
        if "score" in msg_lower or "ats" in msg_lower:
            return "Your ATS score is calculated based on 4 key pillars: Skill Match (40%), TF-IDF Keyword Density (25%), Hygiene & Formatting (20%), and Experience Alignment (15%)."
        elif "skill" in msg_lower:
            return "To boost your resume match, consider adding in-demand technical tools like Docker, Kubernetes, AWS, and TypeScript into your projects and work experience bullet points."
        else:
            return "I am ResumeIQ Copilot! Ask me how to improve your bullet points, explain your ATS score, or suggest projects for your target role."
