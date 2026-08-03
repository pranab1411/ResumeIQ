import os
import json
import re
import spacy
from typing import Dict, List, Set, Any
from utils.logger import logger
from utils.paths import get_asset_path

SKILLS_FILE = get_asset_path("assets", "skills.json")

class NLPEngine:
    def __init__(self):
        self.nlp = None
        self._load_spacy()
        self.known_skills_category = self._load_skills_db()
        self.known_skills_flat = self._flatten_skills()

    def _load_spacy(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
            logger.info("Loaded spaCy model 'en_core_web_sm'.")
        except Exception as e:
            logger.warning(f"Could not load spaCy model directly ({e}). Attempting fallback or blank model...")
            try:
                import en_core_web_sm
                self.nlp = en_core_web_sm.load()
            except Exception:
                self.nlp = spacy.blank("en")

    def _load_skills_db(self) -> Dict[str, List[str]]:
        if os.path.exists(SKILLS_FILE):
            try:
                with open(SKILLS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("skills_by_category", {})
            except Exception as e:
                logger.error(f"Error loading skills.json: {e}")
        return {}

    def _flatten_skills(self) -> Dict[str, str]:
        """Maps skill lower-case -> original display skill name."""
        flat = {}
        for category, skills in self.known_skills_category.items():
            for skill in skills:
                flat[skill.lower()] = skill
        return flat

    def extract_contact_info(self, text: str) -> Dict[str, str]:
        """Extracts candidate email, phone, and name."""
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        phone_pattern = r'\(?\+?\d{1,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}[-.\s]?\d{3,9}'
        
        emails = re.findall(email_pattern, text)
        phones = re.findall(phone_pattern, text)
        
        email = emails[0] if emails else "Not Found"
        phone = phones[0] if phones else "Not Found"
        
        # Name extraction using spaCy PERSON entities
        name = "Candidate"
        if self.nlp:
            doc = self.nlp(text[:500]) # Scan top header of resume
            for ent in doc.ents:
                if ent.label_ == "PERSON" and len(ent.text.split()) in [2, 3]:
                    name = ent.text.split('\n')[0].strip()
                    break
        
        if name == "Candidate":
            # Fallback: check first line
            first_line = text.split("\n")[0].strip() if text else ""
            if first_line and len(first_line.split()) in [2, 3] and not "@" in first_line:
                name = first_line

        return {
            "name": name,
            "email": email,
            "phone": phone
        }

    def extract_skills(self, text: str) -> List[str]:
        """Extracts recognized skills from text using boundary matching."""
        if not text:
            return []
            
        found_skills: Set[str] = set()
        text_lower = text.lower()
        
        for skill_lower, original_name in self.known_skills_flat.items():
            # Use regex pattern to avoid false substring matches (e.g. 'c' inside 'cat')
            escaped = re.escape(skill_lower)
            pattern = r'(?:\b|(?<=\W))' + escaped + r'(?:\b|(?=\W))'
            if re.search(pattern, text_lower):
                found_skills.add(original_name)
                
        return sorted(list(found_skills))

    def extract_keywords_from_jd(self, jd_text: str) -> List[str]:
        """Extracts key skills/technologies mentioned in Job Description."""
        return self.extract_skills(jd_text)

nlp_engine = NLPEngine()
