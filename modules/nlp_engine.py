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
    "marketing", "finance", "accounting", "recruiter", "hr", "human", "resources",
    "creator", "founder", "author", "freelancer", "contributor", "owner", "partner"
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

    def extract_name_with_gemini(self, text: str) -> Optional[str]:
        """Uses Gemini AI to extract candidate name from resume text if API key is configured."""
        try:
            from utils.gemini_client import gemini_generate, gemini_available, GeminiError
            if not gemini_available():
                return None

            lines = [line.strip() for line in text.split("\n") if line.strip()][:10]
            header_text = "\n".join(lines)
            prompt = (
                "Extract ONLY the candidate's real full name from this resume header. "
                "Do NOT include job titles, emails, phone numbers, or section headers like 'About Me'. "
                "Return ONLY the plain candidate name and nothing else.\n\nResume Header:\n" + header_text
            )
            raw_name = gemini_generate(prompt, timeout=5)
            clean_name = raw_name.split("\n")[0].strip().strip("\"':,-_#|•")
            if clean_name and self.is_valid_candidate_name(clean_name):
                logger.info(f"[GEMINI AI] Extracted candidate name: {clean_name}")
                return clean_name.title()
        except Exception as e:
            logger.warning(f"Gemini AI name extraction fallback: {e}")
        return None

    def extract_candidate_name(self, text: str) -> str:
        """Accurately extracts candidate name using Gemini AI + spaCy NLP + Global Names DB."""
        if not text:
            return "Candidate"

        lines = [line.strip() for line in text.split("\n") if line.strip()][:15]

        # 0. Try Gemini AI Name Extraction if API Key is configured
        gemini_name = self.extract_name_with_gemini(text)
        if gemini_name:
            return gemini_name

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

    def extract_normalized_skills(self, text: str) -> List[Dict[str, Any]]:
        """Extracts skills and returns normalized skills with confidence scores."""
        raw_skills = self.extract_skills(text)
        from modules.skill_normalizer import SkillNormalizer
        return SkillNormalizer.deduplicate_skills(raw_skills)

    def extract_soft_skills(self, text: str) -> List[str]:
        """Extracts key soft skills and leadership traits."""
        if not text:
            return []
        soft_skills_db = [
            "Leadership", "Teamwork", "Communication", "Problem Solving", "Critical Thinking",
            "Time Management", "Adaptability", "Collaboration", "Decision Making", "Conflict Resolution",
            "Negotiation", "Mentorship", "Agile Mindset", "Ownership", "Strategic Thinking", "Emotional Intelligence"
        ]
        found = []
        text_lower = text.lower()
        for ss in soft_skills_db:
            if re.search(r'\b' + re.escape(ss.lower()) + r'\b', text_lower):
                found.append(ss)
        return found

    def extract_achievements(self, text: str) -> List[str]:
        """Extracts STAR method achievement bullets and high-impact statements."""
        if not text:
            return []
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        star_verbs = ["achieved", "increased", "decreased", "reduced", "improved", "developed", "spearheaded", "generated", "saved", "launched", "boosted", "optimized", "awarded"]
        achievements = []
        for line in lines:
            line_lower = line.lower()
            if any(v in line_lower for v in star_verbs) and (re.search(r'\b\d+%\b|\$\d+|\b\d+\b', line)):
                achievements.append(line.strip("•*- "))
        return achievements[:10]

    def extract_metrics(self, text: str) -> List[str]:
        """Extracts quantified metrics (%, $, numbers, time saved)."""
        if not text:
            return []
        metric_pattern = r'\b\d+%\b|\$\d+(?:\,\d+)*(?:\.\d+)?\b|\b\d+\+\s+(?:years?|projects?|users?|clients?|teams?)\b|\b\d+x\b'
        return list(set(re.findall(metric_pattern, text, re.IGNORECASE)))

    def extract_certifications(self, text: str) -> List[str]:
        """Extracts recognized industry certifications."""
        if not text:
            return []
        certs_db = [
            "AWS Certified", "AWS Solutions Architect", "AWS Developer", "Azure Fundamentals",
            "Azure Administrator", "GCP Professional", "PMP", "Scrum Master", "CSM", "CKA",
            "CompTIA Security+", "CompTIA Network+", "CompTIA A+", "CISSP", "ITIL", "CCNA",
            "Google Data Analytics", "Meta Front-End", "TensorFlow Certified"
        ]
        found = []
        text_lower = text.lower()
        for cert in certs_db:
            if cert.lower() in text_lower:
                found.append(cert)
        return found

    def generate_experience_timeline(self, text: str) -> List[Dict[str, Any]]:
        """Generates experience timeline events based on extracted date ranges."""
        if not text:
            return []
        date_pattern = r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}|\b20\d{2}\b)\s*(?:–|-|to)\s*((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}|\b20\d{2}\b|Present|Current)'
        matches = re.findall(date_pattern, text, re.IGNORECASE)
        timeline = []
        for i, (start, end) in enumerate(matches):
            timeline.append({
                "period": f"{start} - {end}",
                "start": start,
                "end": end,
                "order": i + 1
            })
        return timeline

    def extract_keywords_from_jd(self, jd_text: str) -> List[str]:
        """Extracts key skills/technologies mentioned in Job Description."""
        return self.extract_skills(jd_text)

nlp_engine = NLPEngine()
