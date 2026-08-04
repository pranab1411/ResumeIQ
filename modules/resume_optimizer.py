"""
modules/resume_optimizer.py
AI Resume Optimizer Engine for ResumeIQ v2.0.
Rewrites professional summaries in multiple tones, converts experience bullets to STAR format,
injects metrics, suggests action verbs, and offers 4 rewrite levels (Basic, Better, Excellent, Recruiter Preferred).
"""

from typing import Dict, Any, List, Optional
from utils.logger import logger
from utils.gemini_client import gemini_generate, gemini_available

class ResumeOptimizer:
    # ── 1. Professional Summary Optimizer ──────────────────────────────────
    @staticmethod
    def optimize_summary(
        raw_summary: str,
        job_title: str = "Software Engineer",
        target_skills: Optional[List[str]] = None,
        tone: str = "Professional"
    ) -> Dict[str, str]:
        """
        Rewrites executive summary in specified tone (Professional, Modern, Executive, Creative, Technical).
        """
        skills_str = ", ".join(target_skills[:5]) if target_skills else "key domain skills"
        
        if gemini_available():
            try:
                prompt = (
                    f"Rewrite this candidate's professional resume summary for a target role of '{job_title}'.\n"
                    f"Tone: {tone}\n"
                    f"Key Skills to incorporate: {skills_str}\n"
                    f"Original Summary:\n{raw_summary}\n\n"
                    f"Return ONLY the optimized 3-4 sentence professional summary."
                )
                optimized = gemini_generate(prompt, temperature=0.7, timeout=10)
                return {
                    "original": raw_summary,
                    "optimized": optimized,
                    "tone": tone,
                    "mode": "ai"
                }
            except Exception as e:
                logger.warning(f"[ResumeOptimizer] Gemini summary optimization fallback: {e}")

        # Fallback template-based optimization
        fallback = (
            f"Results-driven {job_title} with proven expertise in {skills_str}. "
            f"Demonstrated success in delivering high-impact solutions, optimizing workflows, and collaborating across cross-functional teams. "
            f"Passionate about leveraging modern technologies to drive organizational growth and technical excellence."
        )
        return {
            "original": raw_summary,
            "optimized": fallback,
            "tone": tone,
            "mode": "template"
        }

    # ── 2. STAR Method Experience Bullet Optimizer ─────────────────────────
    @staticmethod
    def convert_to_star(bullet_point: str, job_title: str = "") -> Dict[str, str]:
        """
        Converts a plain bullet point into a structured STAR (Situation, Task, Action, Result) format.
        """
        if gemini_available():
            try:
                prompt = (
                    f"Transform this resume bullet point into a high-impact STAR method bullet point (Action + Context + Quantified Result).\n"
                    f"Bullet: {bullet_point}\n"
                    f"Target Role: {job_title}\n\n"
                    f"Return ONLY the single optimized bullet point starting with a strong action verb."
                )
                star_bullet = gemini_generate(prompt, temperature=0.6, timeout=8)
                return {
                    "original": bullet_point,
                    "star_bullet": star_bullet,
                    "mode": "ai"
                }
            except Exception as e:
                logger.warning(f"[ResumeOptimizer] Gemini STAR conversion fallback: {e}")

        # Rule-based fallback STAR enhancement
        words = bullet_point.strip("•*- ").split()
        first_word = words[0] if words else "Developed"
        fallback_star = f"Spearheaded {bullet_point.strip('•*- ')}, increasing operational efficiency by 25% and accelerating project delivery."
        return {
            "original": bullet_point,
            "star_bullet": fallback_star,
            "mode": "template"
        }

    # ── 3. Multi-Level Bullet Rewriter (Basic -> Better -> Excellent -> Recruiter Preferred) ──
    @staticmethod
    def generate_rewrite_levels(bullet_point: str, job_title: str = "") -> Dict[str, str]:
        """
        Generates 4 levels of rewrites: Basic, Better, Excellent, and Recruiter Preferred.
        """
        if gemini_available():
            try:
                prompt = (
                    f"Rewrite this resume bullet point into 4 progressive quality levels:\n"
                    f"Original Bullet: {bullet_point}\n"
                    f"Role: {job_title}\n\n"
                    f"Provide response in EXACT JSON format with keys: 'basic', 'better', 'excellent', 'recruiter_preferred'\n"
                    f"Do NOT include markdown formatting or extra text outside JSON."
                )
                raw_json = gemini_generate(prompt, temperature=0.5, timeout=12)
                # Clean any code fences
                clean_json = raw_json.replace("```json", "").replace("```", "").strip()
                import json
                parsed = json.loads(clean_json)
                return {
                    "basic": parsed.get("basic", bullet_point),
                    "better": parsed.get("better", f"Improved: {bullet_point}"),
                    "excellent": parsed.get("excellent", f"Advanced: {bullet_point}"),
                    "recruiter_preferred": parsed.get("recruiter_preferred", f"Recruiter Gold Standard: {bullet_point}")
                }
            except Exception as e:
                logger.warning(f"[ResumeOptimizer] Gemini multi-level rewrite fallback: {e}")

        # Fallback templates
        clean = bullet_point.strip("•*- ")
        return {
            "basic": f"Responsible for {clean.lower()}.",
            "better": f"Executed {clean.lower()} to support team objectives.",
            "excellent": f"Engineered and delivered {clean.lower()}, improving throughput by 20%.",
            "recruiter_preferred": f"Spearheaded {clean.lower()}, driving 30% performance gains and reducing cost by $15,000 across the enterprise."
        }

    # ── 4. Action Verbs & Metrics Suggester ────────────────────────────────
    @staticmethod
    def suggest_action_verbs(category: str = "Technical") -> List[str]:
        verbs = {
            "Technical": ["Architected", "Engineered", "Automated", "Deployed", "Refactored", "Optimized", "Configured", "Debugged"],
            "Leadership": ["Spearheaded", "Directed", "Orchestrated", "Mentored", "Championed", "Guided", "Supervised", "Mobilized"],
            "Analytical": ["Evaluated", "Analyzed", "Forecasted", "Identified", "Audited", "Modeled", "Diagnosed", "Benchmark"],
            "Creative": ["Conceptualized", "Designed", "Authored", "Pioneered", "Transformed", "Devised", "Crafted", "Published"]
        }
        return verbs.get(category, verbs["Technical"])

    @staticmethod
    def suggest_metrics_to_add(text: str) -> List[str]:
        """Identifies bullet points lacking numbers/metrics and suggests specific metric types."""
        suggestions = []
        lines = [line.strip("•*- ") for line in text.split("\n") if line.strip()]
        import re
        for line in lines:
            if not re.search(r'\b\d+%\b|\$\d+|\b\d+\b', line) and len(line) > 20:
                suggestions.append(f"Add metric to: '{line[:40]}...' (e.g. % efficiency gain, $ saved, team size, response time reduction)")
        return suggestions[:5]
