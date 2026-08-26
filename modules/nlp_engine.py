import os
import json
import re
import spacy
from typing import Dict, List, Set, Any, Tuple
from utils.logger import logger
from utils.paths import get_asset_path

SKILLS_FILE = get_asset_path("assets", "skills.json")
NAMES_FILE = get_asset_path("assets", "names_db.json")

# Comprehensive exclusion vocabularies
NON_NAME_KEYWORDS: Set[str] = {
    # Section Labels & Headers
    "about", "me", "about me", "profile", "personal", "personal profile", "summary", 
    "executive", "executive summary", "professional summary", "career summary", "contact", 
    "contact info", "contact information", "experience", "work experience", "education", 
    "academic background", "skills", "key skills", "technical skills", "soft skills", 
    "curriculum", "vitae", "resume", "cv", "professional resume", "projects", "academic projects",
    "certifications", "work", "history", "career", "objective", "career objective", "info", 
    "information", "details", "personal details", "phone", "telephone", "mobile", "email", 
    "address", "linkedin", "github", "portfolio", "references", "declaration", "page", 
    "hobbies", "languages", "technical", "professional", "qualification", "qualifications", 
    "achievements", "overview", "bio", "biography", "background", "candidate profile",
    "resumeiq", "confidential", "supervisor", "guide", "mentor", "references available",
    # Locations, Months & Common Words
    "january", "february", "march", "april", "may", "june", "july", "august", "september",
    "october", "november", "december", "present", "current", "india", "usa", "uk", "bhopal",
    "delhi", "mumbai", "bangalore", "hyderabad", "pune", "chennai", "kolkata", "new york",
    "california", "texas", "london", "street", "road", "avenue", "city", "state", "country",
    "pincode", "zipcode", "gpa", "cgpa", "percentage", "score", "grade"
}

JOB_TITLES_VOCABULARY: Set[str] = {
    "software developer", "backend developer", "frontend developer", "full stack developer", 
    "web developer", "mobile developer", "android developer", "ios developer", "python developer",
    "java developer", "react developer", "node developer", "cloud developer",
    "software engineer", "backend engineer", "frontend engineer", "full stack engineer",
    "data engineer", "data scientist", "data analyst", "machine learning engineer", "ai engineer",
    "cloud engineer", "cloud architect", "devops engineer", "site reliability engineer", "sre",
    "qa engineer", "qa analyst", "test engineer", "automation engineer",
    "product manager", "project manager", "scrum master", "technical lead", "tech lead",
    "engineering manager", "ui/ux designer", "ui designer", "ux designer", "graphic designer",
    "system administrator", "network engineer", "database administrator", "dba",
    "cybersecurity analyst", "security engineer", "penetration tester",
    "fresher", "intern", "graduate", "student", "associate software engineer", "junior developer", 
    "senior developer", "senior software engineer", "principal engineer", "lead developer",
    "experienced professional", "consultant", "specialist", "coordinator", "director", "officer",
    "architect", "analyst", "developer", "engineer", "designer", "manager", "lead"
}

DEGREE_VOCABULARY: Set[str] = {
    "b.tech", "btech", "b.e.", "be", "bca", "mca", "b.s.", "m.s.", "bs", "ms",
    "b.sc", "m.sc", "bsc", "msc", "bba", "mba", "ph.d.", "phd", "diploma",
    "bachelor", "bachelors", "master", "masters", "doctorate", "degree",
    "computer science", "information technology", "electrical engineering",
    "mechanical engineering", "civil engineering", "electronics"
}

ORGANIZATION_KEYWORDS: Set[str] = {
    "university", "college", "institute", "institution", "school", "academy",
    "technologies", "solutions", "services", "corporation", "corp", "inc",
    "ltd", "limited", "pvt", "private", "systems", "labs", "consulting",
    "department", "faculty", "campus"
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

    @staticmethod
    def normalize_candidate_name(raw_name: str) -> str:
        """Normalizes and sanitizes candidate personal names."""
        if not raw_name:
            return ""
        # Strip common prefix labels (e.g., "Name: John Doe", "Candidate Name - John Doe")
        name = re.sub(r'^(?:candidate\s+name|full\s+name|candidate|name)\s*[:\-–]\s*', '', raw_name.strip(), flags=re.IGNORECASE)
        # Remove surrounding quotes, bullets, punctuation
        name = name.strip("\"'`:,-_#|•–\t ")
        # Collapse multiple spaces
        name = re.sub(r'\s+', ' ', name).strip()
        # If all uppercase (e.g. "PRANAB CHOURASIYA"), title case it while preserving initials
        if name.isupper():
            name = name.title()
        return name

    def is_valid_candidate_name(self, candidate_name: str, context: Optional[str] = None) -> bool:
        """
        Strictly validates if a string is a valid personal human name.
        Rejects job titles, contact info, headings, degrees, organizations, and noisy phrases.
        """
        if not candidate_name or not candidate_name.strip():
            return False
            
        name = self.normalize_candidate_name(candidate_name)
        if not name or len(name) < 2 or len(name) > 40:
            return False
            
        name_lower = name.lower()

        # Reject if exact match in blacklists or known technical skills
        if (name_lower in NON_NAME_KEYWORDS or 
            name_lower in JOB_TITLES_VOCABULARY or 
            name_lower in DEGREE_VOCABULARY or
            name_lower in self.known_skills_flat):
            return False

        # Reject if contains email, URL, domain, or phone characters
        if "@" in name or "http" in name_lower or "www." in name_lower or ".com" in name_lower or "github" in name_lower or "linkedin" in name_lower:
            return False
        if any(c.isdigit() for c in name):
            return False
        if any(c in name for c in ["+", "(", ")", "[", "]", "{", "}", "=", "<", ">", "/", "\\", "%", "$", "*", "_", "~", ":", ";"]):
            return False

        # Tokens validation (supports 1-word up to 4-word names)
        words = [w.strip(".,") for w in name_lower.split() if w.strip(".,")]
        if not (1 <= len(words) <= 4):
            return False

        for w in words:
            if (w in NON_NAME_KEYWORDS or 
                w in JOB_TITLES_VOCABULARY or 
                w in DEGREE_VOCABULARY or 
                w in ORGANIZATION_KEYWORDS or
                w in self.known_skills_flat):
                return False
            if not re.match(r"^[a-zA-Z\.\'-]+$", w):
                return False

        # Character composition: must be alphabetic / punctuation like periods, hyphens, apostrophes
        is_all_alphabetic = all(re.match(r"^[a-zA-Z\.\'-]+$", w) for w in name.split())
        if not is_all_alphabetic:
            return False

        # Verify proper capitalization or dictionary presence
        has_dict_match = any(w in self.global_first_names or w in self.global_last_names for w in words)
        is_proper_cased = all(w[0].isupper() for w in name.split() if len(w) > 0 and w[0].isalpha())

        return has_dict_match or is_proper_cased

    def extract_name_with_gemini(self, text: str) -> Optional[str]:
        """Uses Gemini AI to extract candidate name from resume text if API key is configured."""
        try:
            from utils.gemini_client import gemini_generate, gemini_available, GeminiError
            if not gemini_available():
                return None

            lines = [line.strip() for line in text.split("\n") if line.strip()][:12]
            header_text = "\n".join(lines)
            prompt = (
                "You are an expert ATS resume parser. Extract ONLY the candidate's real personal full name from this resume header. "
                "Do NOT include job titles (like 'Backend Developer'), emails, phone numbers, degrees, or section headers. "
                "Output ONLY the plain candidate name and absolutely nothing else. If no personal name is found, output 'NONE'.\n\n"
                "Resume Header:\n" + header_text
            )
            raw_name = gemini_generate(prompt, timeout=6)
            clean_name = raw_name.split("\n")[0].strip().strip("\"':,-_#|•")
            if clean_name and clean_name.upper() != "NONE" and self.is_valid_candidate_name(clean_name):
                logger.info(f"[GEMINI AI] Extracted candidate name: {clean_name}")
                return self.normalize_candidate_name(clean_name)
        except Exception as e:
            logger.warning(f"Gemini AI name extraction fallback: {e}")
        return None

    def extract_candidate_name(self, text: str) -> str:
        """
        Accurately extracts candidate name using multi-signal context scoring:
        1. Gemini AI (Tier 1 preference)
        2. spaCy PERSON NER in header
        3. Header line segmentation with strict exclusion validation
        4. Global Names DB matching
        5. Controlled fallback: 'Name not confidently detected'
        """
        if not text:
            return "Name not confidently detected"

        lines = [line.strip() for line in text.split("\n") if line.strip()][:15]

        # 0. Primary Preference: Gemini AI extraction if key configured
        gemini_name = self.extract_name_with_gemini(text)
        if gemini_name and self.is_valid_candidate_name(gemini_name):
            return self.normalize_candidate_name(gemini_name)

        scored_candidates: List[Tuple[float, str]] = []

        # 1. spaCy PERSON entities in the top 10 lines
        if self.nlp:
            header_text = "\n".join(lines[:10])
            doc = self.nlp(header_text)
            for i, ent in enumerate(doc.ents):
                if ent.label_ == "PERSON":
                    for part in re.split(r'[|•,\t/–-]', ent.text):
                        clean_part = self.normalize_candidate_name(part)
                        if clean_part and self.is_valid_candidate_name(clean_part):
                            score = 100 - (i * 10)
                            words = [w.lower() for w in clean_part.split()]
                            if any(w in self.global_first_names or w in self.global_last_names for w in words):
                                score += 25
                            scored_candidates.append((score, clean_part))

        # 2. Segmented Header Lines Inspection
        for line_idx, line in enumerate(lines[:10]):
            line_lower = line.lower()
            if "@" in line or "http" in line_lower or "www." in line_lower or "github" in line_lower or "linkedin" in line_lower:
                continue
            if any(kw in line_lower for kw in ["phone", "tel", "mobile", "address", "date of birth"]):
                continue

            # Strip prefixes like "Name: John Doe"
            line_cleaned = re.sub(r'^(?:candidate\s+name|full\s+name|candidate|name)\s*[:\-–]\s*', '', line, flags=re.IGNORECASE)

            # Split on separators (| • , \t - /)
            segments = [p.strip() for p in re.split(r'[|•\t/–]', line_cleaned) if p.strip()]
            for seg_idx, segment in enumerate(segments):
                clean_seg = self.normalize_candidate_name(segment)
                if clean_seg and self.is_valid_candidate_name(clean_seg):
                    base_score = 90 - (line_idx * 8) - (seg_idx * 5)
                    words = [w.lower() for w in clean_seg.split()]
                    if any(w in self.global_first_names or w in self.global_last_names for w in words):
                        base_score += 30
                    if 2 <= len(words) <= 3:
                        base_score += 15
                    scored_candidates.append((base_score, clean_seg))

        if scored_candidates:
            scored_candidates.sort(key=lambda x: x[0], reverse=True)
            best_name = scored_candidates[0][1]
            return self.normalize_candidate_name(best_name)

        return "Name not confidently detected"

    def extract_target_role(self, text: str, fallback_role: str = "") -> str:
        """
        Extracts candidate's target job role from header lines or returns fallback role.
        """
        if not text:
            return fallback_role or "General Position"

        lines = [line.strip() for line in text.split("\n") if line.strip()][:12]
        
        for line in lines:
            segments = [s.strip() for s in re.split(r'[|•\t,–]', line) if s.strip()]
            for seg in segments:
                seg_lower = seg.lower()
                for title in JOB_TITLES_VOCABULARY:
                    if title in seg_lower and len(seg) <= 45:
                        clean_title = re.sub(r'[^\w\s\-/&]', '', seg).strip()
                        return clean_title.title()

        return fallback_role or "General Position"

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
        metric_pattern = r'\b\d+(?:,\d{3})*(?:\.\d+)?%|\$\d+(?:,\d{3})*(?:\.\d+)?\b|\b\d+(?:,\d{3})*\+\s*(?:years?|projects?|users?|clients?|teams?|daily\s+requests?|clusters?|devs?|engineers?|reqs?|rps)?|\b\d+x\b'
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

    def generate_highlighted_html(
        self,
        text: str,
        matched_skills: List[str] = None,
        missing_skills: List[str] = None,
        is_jd: bool = False
    ) -> str:
        """
        Transforms plain text into visually rich HTML with colored entity badges:
        - Matched Skills: Emerald Green badge
        - Action Verbs: Indigo badge
        - Quantified Metrics: Cyan badge
        - Missing Skills (for JD): Red badge
        """
        import html
        if not text:
            return "<p style='color:#94A3B8;font-style:italic;'>No text available to highlight.</p>"

        escaped_lines = []
        star_verbs = [
            "achieved", "increased", "decreased", "reduced", "improved", "developed",
            "spearheaded", "generated", "saved", "launched", "boosted", "optimized",
            "architected", "engineered", "designed", "deployed", "implemented", "led", "managed"
        ]
        
        matched_lower = {s.lower(): s for s in (matched_skills or []) if s}
        missing_lower = {s.lower(): s for s in (missing_skills or []) if s}

        for line in text.split("\n"):
            line_str = line.strip()
            if not line_str:
                escaped_lines.append("<br/>")
                continue

            escaped = html.escape(line_str)

            # Highlight Matched Skills
            for s_lower in sorted(matched_lower.keys(), key=len, reverse=True):
                pat = re.compile(rf'\b({re.escape(s_lower)})\b', re.IGNORECASE)
                escaped = pat.sub(r'<span style="background:rgba(16,185,129,0.25);color:#34D399;padding:1px 5px;border-radius:4px;font-weight:600;border:1px solid rgba(16,185,129,0.4);">\1</span>', escaped)

            # Highlight Missing Skills (if JD view)
            if is_jd:
                for s_lower in sorted(missing_lower.keys(), key=len, reverse=True):
                    pat = re.compile(rf'\b({re.escape(s_lower)})\b', re.IGNORECASE)
                    escaped = pat.sub(r'<span style="background:rgba(239,68,68,0.25);color:#FCA5A5;padding:1px 5px;border-radius:4px;font-weight:600;border:1px solid rgba(239,68,68,0.4);">\1</span>', escaped)
            else:
                # Highlight Action Verbs (if Resume view)
                for v in star_verbs:
                    pat = re.compile(rf'\b({re.escape(v)})\b', re.IGNORECASE)
                    escaped = pat.sub(r'<span style="background:rgba(99,102,241,0.25);color:#A5B4FC;padding:1px 5px;border-radius:4px;font-weight:600;border:1px solid rgba(99,102,241,0.4);">\1</span>', escaped)

                # Highlight Quantified Metrics (%, $, numbers)
                metric_pat = re.compile(r'(\b\d+(?:,\d{3})*(?:\.\d+)?%|\$\d+(?:,\d{3})*(?:\.\d+)?\b|\b\d+(?:,\d{3})*\+\s*(?:years?|projects?|users?|clients?|teams?|daily\s+requests?|clusters?|devs?|engineers?|reqs?|rps)?|\b\d+x\b)', re.IGNORECASE)
                escaped = metric_pat.sub(r'<span style="background:rgba(6,182,212,0.25);color:#67E8F9;padding:1px 5px;border-radius:4px;font-weight:600;border:1px solid rgba(6,182,212,0.4);">\1</span>', escaped)

            escaped_lines.append(f"<p style='margin: 4px 0; line-height: 1.6; color: #E2E8F0; font-family: Segoe UI, sans-serif; font-size: 12.5px;'>{escaped}</p>")

        return "".join(escaped_lines)

nlp_engine = NLPEngine()

