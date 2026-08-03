import os
import json
import re
import spacy
from typing import Dict, List, Set, Any, Tuple
from utils.logger import logger
from utils.paths import get_asset_path

SKILLS_FILE = get_asset_path("assets", "skills.json")
NAMES_FILE = get_asset_path("assets", "names_db.json")

# Strict non-name header, section label & job title blacklist filter
NON_NAME_KEYWORDS: Set[str] = {
    "about", "me", "about me", "profile", "personal", "summary", "executive", "contact", 
    "experience", "education", "skills", "curriculum", "vitae", "resume", "cv", "projects", 
    "certifications", "work", "history", "career", "objective", "info", "information", 
    "details", "phone", "email", "address", "linkedin", "github", "portfolio", "references", 
    "declaration", "page", "hobbies", "languages", "technical", "professional", "qualification",
    "qualifications", "achievements", "overview", "bio", "biography", "background", "contact info",
    "personal profile", "work experience", "career summary", "executive summary", "key skills",
    "soft skills", "technical skills", "academic background", "personal details",
    # Job Titles, Roles & Industry Blacklist
    "support", "engineer", "developer", "designer", "manager", "analyst", "consultant",
    "specialist", "administrator", "lead", "architect", "associate", "intern", "assistant",
    "coordinator", "director", "officer", "helpdesk", "service", "services", "customer",
    "agent", "representative", "trainee", "fresher", "senior", "junior", "principal", "staff",
    "head", "vp", "ceo", "cto", "cfo", "team", "group", "department", "division", "tech",
    "technology", "solutions", "systems", "operations", "management", "business", "sales",
    "marketing", "finance", "accounting", "recruiter", "hr", "human", "resources"
}

class NLPEngine:
    def __init__(self):
        self.nlp = None
        self._load_spacy()
        self.known_skills_category = self._load_skills_db()
        self.known_skills_flat = self._flatten_skills()
        self.global_first_names, self.global_last_names = self._load_names_db()

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

    def _load_names_db(self) -> Tuple[Set[str], Set[str]]:
        if os.path.exists(NAMES_FILE):
            try:
                with open(NAMES_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    firsts = {x.lower() for x in data.get("first_names", [])}
                    lasts = {x.lower() for x in data.get("last_names", [])}
                    logger.info(f"Loaded Global Names DB: {len(firsts)} first names, {len(lasts)} last names.")
                    return firsts, lasts
            except Exception as e:
                logger.error(f"Error loading names_db.json: {e}")
        return set(), set()

    def _flatten_skills(self) -> Dict[str, str]:
        """Maps skill lower-case -> original display skill name."""
        flat = {}
        for category, skills in self.known_skills_category.items():
            for skill in skills:
                flat[skill.lower()] = skill
        return flat

    def is_valid_candidate_name(self, candidate_name: str) -> bool:
        """Validates if a string is a valid human name, excluding section headers & titles."""
        if not candidate_name or not candidate_name.strip():
            return False
            
        clean = candidate_name.strip().strip(":,-_#|•")
        clean_lower = clean.lower()

        if clean_lower in NON_NAME_KEYWORDS:
            return False
            
        words = [w.strip() for w in clean_lower.split() if w.strip()]
        if not (1 <= len(words) <= 4):
            return False

        for w in words:
            if w in NON_NAME_KEYWORDS:
                return False
            if any(char.isdigit() for char in w):
                return False
            if "@" in w or "http" in w or "www." in w or ".com" in w:
                return False

        # Check matching against global names database or capitalized proper noun format
        has_dict_match = any(w in self.global_first_names or w in self.global_last_names for w in words)
        is_all_alphabetic = all(re.match(r'^[a-zA-Z\.\'-]+$', w) for w in words)

        return is_all_alphabetic and (has_dict_match or all(w[0].isupper() for w in clean.split() if w))

    def extract_candidate_name(self, text: str) -> str:
        """Accurately extracts candidate name from resume header using NLP and Global Names DB."""
        if not text:
            return "Candidate"

        lines = [line.strip() for line in text.split("\n") if line.strip()][:15]

        # Helper to clean token parts
        def clean_token(tok: str) -> str:
            # Strip job title words from token
            words = [w for w in tok.split() if w.lower() not in NON_NAME_KEYWORDS]
            return " ".join(words)

        # 1. Try spaCy PERSON entities with strict exclude validation
        if self.nlp:
            header_text = "\n".join(lines[:10])
            doc = self.nlp(header_text)
            for ent in doc.ents:
                if ent.label_ == "PERSON":
                    clean_ent = ent.text.split("\n")[0].strip().strip(":,-_#|•")
                    clean_candidate = clean_token(clean_ent)
                    if clean_candidate and self.is_valid_candidate_name(clean_candidate):
                        return clean_candidate.title()

        # 2. Check top lines against global names database and exclude filters
        for line in lines:
            if "@" in line or "http" in line or "phone" in line.lower() or "resume" in line.lower():
                continue
            
            parts = [p.strip() for p in re.split(r'[|•,\t:-]', line) if p.strip()]
            for part in parts:
                clean_part = clean_token(part)
                if clean_part and self.is_valid_candidate_name(clean_part):
                    return clean_part.title()

        # 3. Check first non-keyword line
        for line in lines:
            line_clean = line.strip().strip(":,-_#|•")
            clean_part = clean_token(line_clean)
            if clean_part and self.is_valid_candidate_name(clean_part):
                return clean_part.title()

        return "Candidate"

    def extract_contact_info(self, text: str) -> Dict[str, str]:
        """Extracts candidate email, phone, and accurately parsed candidate name."""
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        phone_pattern = r'\(?\+?\d{1,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}[-.\s]?\d{3,9}'
        
        emails = re.findall(email_pattern, text)
        phones = re.findall(phone_pattern, text)
        
        email = emails[0] if emails else "Not Found"
        phone = phones[0] if phones else "Not Found"
        
        name = self.extract_candidate_name(text)

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
            escaped = re.escape(skill_lower)
            pattern = r'(?:\b|(?<=\W))' + escaped + r'(?:\b|(?=\W))'
            if re.search(pattern, text_lower):
                found_skills.add(original_name)
                
        return sorted(list(found_skills))

    def extract_keywords_from_jd(self, jd_text: str) -> List[str]:
        """Extracts key skills/technologies mentioned in Job Description."""
        return self.extract_skills(jd_text)

nlp_engine = NLPEngine()
