"""
modules/career_hub.py
Career Development Hub Engine for ResumeIQ v2.0.
Provides personalized learning roadmaps, skill gap analysis, certification recommendations,
and career progression milestones.
"""

import json
import os
from typing import Dict, Any, List
from utils.logger import logger

_ROADMAP_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "career_roadmaps.json")

def _load_roadmaps() -> Dict:
    try:
        if os.path.exists(_ROADMAP_PATH):
            with open(_ROADMAP_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        logger.warning(f"[CareerHub] Failed loading career_roadmaps.json: {e}")
    return {}

_ROADMAPS = _load_roadmaps()

class CareerHub:
    @classmethod
    def get_career_plan(cls, track: str = "Software Engineering", user_skills: List[str] = None) -> Dict[str, Any]:
        user_skills = user_skills or []
        user_skills_lower = {s.lower() for s in user_skills}

        track_data = _ROADMAPS.get(track, _ROADMAPS.get("Software Engineering", {}))
        stages = track_data.get("stages", [])

        # Analyze skill gaps per stage
        processed_stages = []
        for stage in stages:
            req_skills = stage.get("key_skills", [])
            matched = [s for s in req_skills if s.lower() in user_skills_lower]
            missing = [s for s in req_skills if s.lower() not in user_skills_lower]
            pct = round((len(matched) / max(1, len(req_skills))) * 100.0, 1)

            processed_stages.append({
                "title": stage["title"],
                "years": stage["years"],
                "required_skills": req_skills,
                "matched_skills": matched,
                "missing_skills": missing,
                "readiness_pct": pct,
                "recommended_certs": stage.get("recommended_certs", [])
            })

        return {
            "track": track,
            "stages": processed_stages,
            "overall_readiness": processed_stages[0]["readiness_pct"] if processed_stages else 50.0
        }
