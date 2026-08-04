"""
modules/skill_normalizer.py
Skill normalization, alias mapping, duplicate skill removal, and confidence scoring.
"""

import json
import os
from typing import List, Dict, Tuple, Any
from utils.logger import logger

_ALIAS_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "skill_aliases.json")

def _load_aliases() -> Dict[str, str]:
    alias_map = {}
    try:
        if os.path.exists(_ALIAS_PATH):
            with open(_ALIAS_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                for canonical, aliases in data.items():
                    alias_map[canonical.lower()] = canonical.lower()
                    for alias in aliases:
                        alias_map[alias.lower()] = canonical.lower()
    except Exception as e:
        logger.warning(f"[SkillNormalizer] Failed to load skill_aliases.json: {e}")
    return alias_map

_ALIAS_MAP = _load_aliases()

class SkillNormalizer:
    @staticmethod
    def normalize_skill(skill: str) -> str:
        s_clean = skill.strip().lower()
        return _ALIAS_MAP.get(s_clean, s_clean)

    @staticmethod
    def deduplicate_skills(skills: List[str]) -> List[Dict[str, Any]]:
        """
        Deduplicates skill list, normalizes aliases, and calculates confidence scores (0.0 to 1.0).
        Returns list of dicts: {"skill": canonical_name, "original": raw_name, "confidence": float}
        """
        seen = {}
        for s in skills:
            if not s or len(s.strip()) < 2:
                continue
            raw = s.strip()
            norm = SkillNormalizer.normalize_skill(raw)
            
            # Calculate confidence score
            conf = 0.85
            if norm in _ALIAS_MAP:
                conf = 0.95
            if len(norm) > 3:
                conf += 0.05
                
            conf = round(min(1.0, conf), 2)
            
            if norm not in seen or conf > seen[norm]["confidence"]:
                seen[norm] = {
                    "skill": norm.title(),
                    "original": raw,
                    "confidence": conf
                }
                
        return list(seen.values())
