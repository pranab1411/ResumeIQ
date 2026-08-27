from typing import List, Dict, Any, Tuple, Optional
import re
from utils.logger import logger
from modules.ats_benchmark import ATSBenchmarkEngine

# Synonym dictionary for ATS skill normalization (Tech & Non-Tech Roles)
SKILL_SYNONYMS = {
    # Tech - Languages & Web
    "js": "javascript",
    "javascript": "javascript",
    "js6": "javascript",
    "es6": "javascript",
    "ts": "typescript",
    "typescript": "typescript",
    "py": "python",
    "python": "python",
    "python3": "python",
    "cpp": "c++",
    "c++": "c++",
    "csharp": "c#",
    "c#": "c#",
    "html": "html",
    "html5": "html",
    "css": "css",
    "css3": "css",
    "react": "react",
    "reactjs": "react",
    "react.js": "react",
    "vue": "vue.js",
    "vuejs": "vue.js",
    "ng": "angular",
    "angularjs": "angular",
    "node": "node.js",
    "nodejs": "node.js",
    "node.js": "node.js",
    
    # Tech - Cloud & DevOps
    "aws": "amazon web services",
    "amazon web services": "amazon web services",
    "gcp": "google cloud",
    "google cloud platform": "google cloud",
    "azure": "microsoft azure",
    "k8s": "kubernetes",
    "kubernetes": "kubernetes",
    "docker": "docker",
    "containers": "docker",
    "ci/cd": "ci/cd",
    "cicd": "ci/cd",
    "iac": "infrastructure as code",
    "tf": "terraform",
    
    # Tech - Data, AI & Databases
    "ml": "machine learning",
    "machine learning": "machine learning",
    "ai": "artificial intelligence",
    "artificial intelligence": "artificial intelligence",
    "dl": "deep learning",
    "nlp": "natural language processing",
    "cv": "computer vision",
    "llm": "large language models",
    "llms": "large language models",
    "genai": "generative ai",
    "postgres": "postgresql",
    "postgresql": "postgresql",
    "sql": "sql",
    "mysql": "mysql",
    "mongo": "mongodb",
    "mongodb": "mongodb",
    "sklearn": "scikit-learn",
    "tf": "tensorflow",
    "bi": "business intelligence",

    # Tech - Security, SRE & QA
    "qa": "quality assurance",
    "sre": "site reliability engineering",
    "infosec": "information security",
    "secops": "security operations",
    "devsecops": "devsecops",
    "pen testing": "penetration testing",
    
    # Tech - IT Support & Desktop Engineering
    "ad": "active directory",
    "active directory": "active directory",
    "azure ad": "azure ad",
    "entra": "entra id",
    "gpo": "group policy",
    "o365": "office 365",
    "m365": "microsoft 365",
    "itsm": "it service management",
    "itil": "itil",
    "sccm": "sccm",
    "mecm": "mecm",
    "mdm": "mobile device management",
    "vdi": "virtual desktop infrastructure",
    "rdp": "remote desktop support",
    "vpn": "vpn",
    "dhcp": "dhcp",
    "dns": "dns",
    "wds": "windows deployment services",
    "mdt": "microsoft deployment toolkit",
    "mfa": "mfa",
    "2fa": "mfa",
    
    # Non-Tech - Business, Marketing & Operations
    "seo": "search engine optimization",
    "sem": "search engine marketing",
    "ppc": "pay-per-click",
    "cro": "conversion rate optimization",
    "crm": "customer relationship management",
    "sfa": "sales force automation",
    "hris": "human resources information system",
    "ats": "applicant tracking system",
    "pmp": "project management professional",
    "scrum": "scrum",
    "agile": "agile",
    "prd": "product requirement document",
    "ux": "user experience",
    "ui": "user interface",
    "nps": "net promoter score",
    "csat": "customer satisfaction",
    "sla": "service level agreement",
    "kpi": "key performance indicator",
    "okr": "objectives and key results",
    "gaap": "generally accepted accounting principles",
    "ifrs": "international financial reporting standards",
    "pr": "public relations",
    "cx": "customer experience"
}

class ATSCalculator:
    @staticmethod
    def _normalize_skill(skill: str) -> str:
        s_clean = skill.strip().lower()
        return SKILL_SYNONYMS.get(s_clean, s_clean)

    @staticmethod
    def calculate_tf_idf_similarity(resume_text: str, jd_text: str) -> float:
        """Calculates TF-IDF Cosine Similarity between resume text and job description."""
        if not resume_text or not jd_text:
            return 50.0
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity

            vectorizer = TfidfVectorizer(stop_words='english')
            tfidf_matrix = vectorizer.fit_transform([resume_text, jd_text])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return min(100.0, max(0.0, round(float(similarity) * 100.0, 1)))
        except Exception as e:
            logger.warning(f"TF-IDF calculation error: {e}. Fallback to keyword density.")
            # Fallback word overlap
            r_words = set(re.findall(r'\w+', resume_text.lower()))
            j_words = set(re.findall(r'\w+', jd_text.lower()))
            if not j_words:
                return 50.0
            overlap = len(r_words.intersection(j_words)) / len(j_words)
            return round(min(100.0, overlap * 100.0), 1)

    @staticmethod
    def calculate_hygiene_score(resume_text: str, contact_info: Dict[str, str] = None) -> float:
        """Calculates formatting, structure, action verbs, and quantifiable metrics hygiene (0-100%)."""
        if not resume_text:
            return 50.0
        
        text_lower = resume_text.lower()
        score = 0.0

        # 1. Contact Info Completeness (25 pts)
        contact_pts = 0
        if contact_info:
            if contact_info.get("email") and contact_info.get("email") != "Not Found":
                contact_pts += 12.5
            if contact_info.get("phone") and contact_info.get("phone") != "Not Found":
                contact_pts += 12.5
        else:
            if re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text_lower):
                contact_pts += 12.5
            if re.search(r'\d{10}', text_lower):
                contact_pts += 12.5
        score += contact_pts

        # 2. Key Resume Sections Present (25 pts)
        sections = ["experience", "employment", "work history", "education", "skills", "projects"]
        sections_found = sum(1 for sec in sections if sec in text_lower)
        score += min(25.0, (sections_found / 3.0) * 25.0)

        # 3. Action Verbs Usage (25 pts)
        action_verbs = ["managed", "developed", "created", "designed", "implemented", "increased", "reduced", "led", "architected", "built", "optimized", "spearheaded", "engineered"]
        verbs_found = sum(1 for verb in action_verbs if verb in text_lower)
        score += min(25.0, (verbs_found / 4.0) * 25.0)

        # 4. Quantifiable Metrics & Numbers (25 pts)
        metrics_pattern = r'\b\d+%\b|\$\d+|\b\d+\s+users\b|\b\d+\s+projects\b|\b\d+\+\s+years\b|\b\d+\s+team\b'
        metrics_count = len(re.findall(metrics_pattern, text_lower))
        if metrics_count >= 3:
            score += 25.0
        elif metrics_count > 0:
            score += metrics_count * 8.0
        else:
            score += 5.0

        return round(min(100.0, score), 1)

    @staticmethod
    def calculate_experience_score(resume_text: str, jd_text: str = "") -> float:
        """Calculates experience and degree match alignment (0-100%)."""
        if not resume_text:
            return 50.0

        text_lower = resume_text.lower()
        score = 60.0 # Base score

        # Degree matching (+20 pts)
        degrees = ["bachelor", "master", "phd", "b.tech", "m.tech", "b.s.", "m.s.", "degree", "computer science", "engineering"]
        if any(deg in text_lower for deg in degrees):
            score += 20.0

        # Years of Experience matching (+20 pts)
        exp_pattern = r'(\d+)\+?\s*years?'
        matches = re.findall(exp_pattern, text_lower)
        if matches:
            max_years = max([int(m) for m in matches if m.isdigit()])
            if max_years >= 5:
                score += 20.0
            elif max_years >= 2:
                score += 15.0
            else:
                score += 10.0
        else:
            score += 10.0

        return round(min(100.0, score), 1)

    @classmethod
    def calculate_score(
        cls,
        resume_skills: List[str],
        required_skills: List[str],
        resume_text: str = "",
        jd_text: str = "",
        contact_info: Dict[str, str] = None,
        industry: str = "General",
        company: Optional[str] = None
    ) -> Tuple[float, List[str], List[str]]:
        """
        Calculates Industry-Grade 4-Pillar ATS Score, Matched Skills, and Missing Skills.
        Formula: (0.40 × Skill Match) + (0.25 × TF-IDF Similarity) + (0.20 × Hygiene) + (0.15 × Exp Alignment)
        Weights are configurable per company via ats_config.json.
        """
        if not required_skills:
            matched = resume_skills
            missing = []
            raw_score = 100.0 if len(resume_skills) >= 5 else (len(resume_skills) * 20.0)
            return round(raw_score, 1), matched, missing

        # Load configurable weights (company-specific or default)
        weights = ATSBenchmarkEngine.get_pillar_weights(company)
        w_skills = weights.get("skills", 0.40)
        w_keywords = weights.get("keywords", 0.25)
        w_format = weights.get("format", 0.20)
        w_exp = weights.get("experience", 0.15)

        # Pillar 1: Skill & Synonym Match
        resume_normalized = {cls._normalize_skill(s): s for s in resume_skills}
        req_normalized = {cls._normalize_skill(s): s for s in required_skills}

        matched_skills = []
        missing_skills = []

        for norm_req, orig_req in req_normalized.items():
            if norm_req in resume_normalized:
                matched_skills.append(orig_req)
            else:
                missing_skills.append(orig_req)

        skill_match_pct = (len(matched_skills) / len(req_normalized)) * 100.0

        # Pillar 2: TF-IDF Cosine Similarity
        semantic_pct = cls.calculate_tf_idf_similarity(resume_text, jd_text) if resume_text and jd_text else skill_match_pct

        # Pillar 3: Hygiene & Formatting
        hygiene_pct = cls.calculate_hygiene_score(resume_text, contact_info) if resume_text else 80.0

        # Pillar 4: Education & Experience Alignment
        exp_pct = cls.calculate_experience_score(resume_text, jd_text) if resume_text else 80.0

        # Final Weighted Multi-Pillar ATS Composite Score
        composite_score = (
            (w_skills * skill_match_pct) +
            (w_keywords * semantic_pct) +
            (w_format * hygiene_pct) +
            (w_exp * exp_pct)
        )
        final_score = round(min(100.0, max(0.0, composite_score)), 1)

        logger.info(
            f"[ATS v2.0] Score: {final_score}% | "
            f"Skills: {skill_match_pct:.1f}% ({w_skills:.0%}) | "
            f"Keywords: {semantic_pct:.1f}% ({w_keywords:.0%}) | "
            f"Format: {hygiene_pct:.1f}% ({w_format:.0%}) | "
            f"Exp: {exp_pct:.1f}% ({w_exp:.0%}) | "
            f"Industry: {industry} | Company: {company or 'General'}"
        )

        return final_score, matched_skills, missing_skills

    @classmethod
    def calculate_full_analysis(
        cls,
        resume_skills: List[str],
        required_skills: List[str],
        resume_text: str = "",
        jd_text: str = "",
        contact_info: Dict[str, str] = None,
        industry: str = "General",
        company: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        v2.0 Full ATS Analysis — returns complete breakdown including:
        ATS score, pillar scores, RQI, Confidence Score, Readiness Score,
        Pass Probability, Percentile, Checklist, Company Simulation.
        """
        ats_score, matched_skills, missing_skills = cls.calculate_score(
            resume_skills, required_skills, resume_text, jd_text,
            contact_info, industry, company
        )

        weights = ATSBenchmarkEngine.get_pillar_weights(company)
        pillar_scores = {
            "skills": round(min(100.0, (len(matched_skills) / max(1, len(required_skills))) * 100.0), 1),
            "keywords": cls.calculate_tf_idf_similarity(resume_text, jd_text) if resume_text and jd_text else 0.0,
            "format": cls.calculate_hygiene_score(resume_text, contact_info),
            "experience": cls.calculate_experience_score(resume_text, jd_text),
        }

        analysis = ATSBenchmarkEngine.build_full_analysis(
            ats_score=ats_score,
            pillar_scores=pillar_scores,
            resume_text=resume_text,
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            contact_info=contact_info,
            industry=industry,
            company=company
        )
        analysis["matched_skills"] = matched_skills
        analysis["missing_skills"] = missing_skills
        analysis["score_category"] = cls.get_score_category(ats_score)
        analysis["star_rating"] = cls.get_star_rating(ats_score)
        analysis["pillar_weights"] = weights
        return analysis

    @staticmethod
    def get_score_category(score: float) -> str:
        if score < 50.0:
            return "Needs Improvement"
        elif score <= 75.0:
            return "Average"
        else:
            return "Excellent"

    @staticmethod
    def get_star_rating(score: float, is_gui: bool = False) -> str:
        """
        Calculates granular 5-star rating based on exact ATS score percentage (0-100%).
        Supports full, three-quarter (¾), half (½), one-quarter (¼), and empty stars.
        """
        raw_rating = max(0.0, min(100.0, float(score))) / 20.0  # 0.0 to 5.0
        full_stars = int(raw_rating)
        remainder = raw_rating - full_stars
        
        frac_symbol = ""
        if remainder >= 0.875:
            full_stars += 1
        elif remainder >= 0.625:
            frac_symbol = "¾"
        elif remainder >= 0.375:
            frac_symbol = "½"
        elif remainder >= 0.125:
            frac_symbol = "¼"
            
        full_symbol = "⭐" if is_gui else "★"
        empty_symbol = "☆"
        
        empty_stars = max(0, 5 - full_stars - (1 if frac_symbol else 0))
        stars_str = (full_symbol * full_stars) + (frac_symbol) + (empty_symbol * empty_stars)
        return f"{stars_str} ({raw_rating:.1f}/5 Stars)"

    @staticmethod
    def get_star_rating_gui(score: float) -> str:
        """
        Calculates granular emoji 5-star rating for GUI displays.
        """
        return ATSCalculator.get_star_rating(score, is_gui=True)

    @staticmethod
    def generate_format_health_audit(resume_text: str, contact_info: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Generates a 4-card structural hygiene diagnostic audit matrix:
        1. Word Count Budget (Optimal / Under / Over)
        2. Action Verb Density
        3. Quantified Metrics Density
        4. Contact Completeness Index
        """
        if not resume_text:
            return {
                "word_count": 0,
                "word_count_status": "Empty",
                "word_count_color": "#94A3B8",
                "action_verbs_count": 0,
                "metrics_count": 0,
                "contact_completeness_pct": 0,
                "health_grade": "C (Needs Formatting Fixes)",
                "health_score": 0.0
            }

        words = [w for w in resume_text.split() if len(w) > 1]
        word_count = len(words)

        if 350 <= word_count <= 850:
            wc_status = "Optimal (1–2 Pages)"
            wc_color = "#34D399"
        elif word_count < 350:
            wc_status = "Under Budget (<350 words)"
            wc_color = "#FBBF24"
        else:
            wc_status = "Dense / Long (>850 words)"
            wc_color = "#F87171"

        # Action Verbs
        star_verbs = ["achieved", "increased", "decreased", "reduced", "improved", "developed", 
                      "spearheaded", "generated", "saved", "launched", "boosted", "optimized", 
                      "architected", "engineered", "designed", "deployed", "implemented", "led", "managed"]
        text_lower = resume_text.lower()
        verb_count = sum(len(re.findall(rf'\b{re.escape(v)}\b', text_lower)) for v in star_verbs)

        # Quantified Metrics
        metric_pattern = r'\b\d+(?:,\d{3})*(?:\.\d+)?%|\$\d+(?:,\d{3})*(?:\.\d+)?\b|\b\d+(?:,\d{3})*\+\s*(?:years?|projects?|users?|clients?|teams?|daily\s+requests?|clusters?|devs?|engineers?|reqs?|rps)?|\b\d+x\b'
        metrics_found = list(set(re.findall(metric_pattern, resume_text, re.IGNORECASE)))
        metrics_count = len(metrics_found)

        # Contact Completeness
        contact = contact_info or {}
        contact_pts = 0
        if contact.get("name", "Candidate") not in ["Candidate", "Not Found", ""]:
            contact_pts += 30
        if contact.get("email", "Not Found") not in ["Not Found", ""]:
            contact_pts += 30
        if contact.get("phone", "Not Found") not in ["Not Found", ""]:
            contact_pts += 25
        if "github.com" in text_lower or "linkedin.com" in text_lower:
            contact_pts += 15
        contact_completeness = min(contact_pts, 100)

        # Overall Structural Health Score & Grade
        avg_score = (
            (100 if 350 <= word_count <= 850 else 60) * 0.25 +
            min(verb_count * 15, 100) * 0.25 +
            min(metrics_count * 25, 100) * 0.25 +
            contact_completeness * 0.25
        )
        if avg_score >= 80:
            grade = "A (Clean & ATS-Ready)"
        elif avg_score >= 60:
            grade = "B (Acceptable)"
        else:
            grade = "C (Needs Formatting Fixes)"

        return {
            "word_count": word_count,
            "word_count_status": wc_status,
            "word_count_color": wc_color,
            "action_verbs_count": verb_count,
            "metrics_count": metrics_count,
            "contact_completeness_pct": contact_completeness,
            "health_grade": grade,
            "health_score": round(avg_score, 1)
        }

    @staticmethod
    def generate_suggestions(
        score: float,
        matched_skills: List[str],
        missing_skills: List[str],
        contact_info: Dict[str, str],
        resume_text: str,
        mode: str = "experienced"
    ) -> List[str]:
        suggestions = []

        if mode == "fresher":
            suggestions.append("Structure & Section Hierarchy: Place your Name, Contact Info (Email, Phone, LinkedIn, GitHub) at the top, followed immediately by Career Objective, Education, Academic/Personal Projects, and Technical Skills.")
            suggestions.append("Typography & Font Sizing: Use clean, professional sans-serif fonts (e.g., Calibri, Arial, or Inter). Maintain clear font hierarchy: Name (20–24pt bold), Section Headers (14–16pt bold UPPERCASE), Body text (10–11pt regular).")
            suggestions.append("Attention-Grabbing Headline: Use bold action-oriented project titles and highlight live demo/GitHub links to immediately capture recruiter attention.")
            suggestions.append("Visual Margins & Spacing: Keep uniform 0.75-inch to 1-inch margins with consistent bullet spacing so your 1-page fresher resume looks well-filled and balanced.")
        else:
            # Missing skills suggestions for experienced candidates
            if missing_skills:
                top_missing = ", ".join(missing_skills[:5])
                suggestions.append(f"Add critical missing job skills to your resume: {top_missing}.")

            if score < 50.0:
                suggestions.append("Your resume ATS match score is low. Tailor your resume keywords specifically to match the target job description.")
                suggestions.append("Include relevant tools, programming languages, and frameworks in a dedicated 'Technical Skills' section.")
            elif score <= 75.0:
                suggestions.append("Good start! Adding a few more key job skills and certifications will push your ATS score above 75%.")
                suggestions.append("Ensure skills are mentioned in both your summary section and experience bullet points.")
            else:
                suggestions.append("Outstanding match! Your resume closely aligns with the required job qualifications.")

        # Contact info checks
        if contact_info:
            if contact_info.get("email") == "Not Found":
                suggestions.append("Ensure your email address is clearly visible near the header of your document.")
            if contact_info.get("phone") == "Not Found":
                suggestions.append("Include a valid contact phone number.")

        # Action verbs check
        action_verbs = ["managed", "developed", "created", "designed", "implemented", "increased", "reduced", "led", "architected", "built"]
        has_verbs = any(verb in resume_text.lower() for verb in action_verbs) if resume_text else False
        if not has_verbs:
            suggestions.append("Use strong action verbs (e.g., 'Developed', 'Implemented', 'Created') to quantify your impact.")

        # Metrics check
        numbers_pattern = r'\b\d+%\b|\$\d+|\b\d+\s+users\b|\b\d+\s+projects\b'
        if resume_text and not re.search(numbers_pattern, resume_text.lower()):
            suggestions.append("Add measurable achievements (e.g., 'Built 3 projects', 'Optimized query speed by 25%').")

        return suggestions

    @staticmethod
    def predict_matching_job_roles(extracted_skills: List[str], top_n: int = 4) -> List[Dict[str, Any]]:
        """
        Predicts top matching job roles based on skills extracted from candidate resume.
        """
        if not extracted_skills:
            return [
                {"role": "General Professional", "match_pct": 50.0, "category": "General", "matched_skills": ["Communication"], "match_count": 1}
            ]

        cand_norm = {ATSCalculator._normalize_skill(x) for x in extracted_skills}
        results = []

        for role_title, data in ROLE_SKILL_PROFILES.items():
            role_skills = data["skills"]
            matched = []
            for s in role_skills:
                norm_s = ATSCalculator._normalize_skill(s)
                if norm_s in cand_norm:
                    matched.append(s)
                elif len(norm_s) > 1 and any(re.search(r'(?:\b|(?<=\W))' + re.escape(norm_s) + r'(?:\b|(?=\W))', c) for c in cand_norm):
                    matched.append(s)

            matched_unique = sorted(list(set(matched)))
            if len(matched_unique) > 0:
                match_pct = round(min(100.0, (len(matched_unique) / min(len(role_skills), max(3, len(cand_norm)))) * 100.0), 1)
                results.append({
                    "role": role_title,
                    "match_pct": match_pct,
                    "category": data["category"],
                    "matched_skills": matched_unique,
                    "match_count": len(matched_unique)
                })

        results.sort(key=lambda x: (x["match_pct"], x["match_count"]), reverse=True)
        return results[:top_n]


ROLE_SKILL_PROFILES: Dict[str, Dict[str, Any]] = {
    # --- HEALTHCARE, MEDICAL & NURSING ---
    "Registered Nurse (RN) / Clinical Specialist": {
        "skills": ["Patient Care", "EHR/EMR", "Triage", "Clinical Assessment", "Pharmacology", "Vital Signs", "HIPAA Compliance", "CPR", "BLS", "Patient Education", "Infection Control"],
        "category": "Healthcare & Nursing"
    },
    "Medical Billing & Coding Specialist": {
        "skills": ["ICD-10", "CPT Coding", "Medical Billing", "Medical Coding", "Epic Systems", "Cerner", "Insurance Claims", "Practice Management", "Medical Records"],
        "category": "Healthcare Administration"
    },
    "Healthcare Administrator / Practice Manager": {
        "skills": ["Healthcare Analytics", "Practice Management", "EHR/EMR", "HIPAA Compliance", "Medical Records", "Revenue Cycle Management", "Patient Scheduling", "CMS Regulations"],
        "category": "Healthcare Administration"
    },

    # --- EDUCATION & ACADEMIA ---
    "K-12 Educator / School Teacher": {
        "skills": ["Lesson Planning", "Classroom Management", "Curriculum Development", "Student Assessment", "Differentiated Instruction", "Special Education", "EdTech", "K-12 Teaching"],
        "category": "Education & Teaching"
    },
    "Academic Administrator / Higher Education Coordinator": {
        "skills": ["Academic Advising", "Higher Education", "Curriculum Development", "Student Assessment", "Canvas LMS", "Blackboard", "Educational Leadership", "E-Learning"],
        "category": "Education & Teaching"
    },

    # --- LEGAL & COMPLIANCE ---
    "Attorney / Corporate Legal Counsel": {
        "skills": ["Legal Research", "Contract Drafting", "Litigation", "Intellectual Property", "Corporate Law", "Regulatory Compliance", "Due Diligence", "Legal Writing", "Contract Negotiation"],
        "category": "Legal & Compliance"
    },
    "Paralegal / Legal Assistant": {
        "skills": ["Legal Research", "Paralegal", "Case Management", "Westlaw", "LexisNexis", "Legal Writing", "Document Review", "Contract Drafting"],
        "category": "Legal & Compliance"
    },

    # --- ENGINEERING & ARCHITECTURE (NON-IT) ---
    "Civil & Structural Engineer": {
        "skills": ["AutoCAD", "Revit", "Civil 3D", "Structural Analysis", "Building Codes", "Surveying", "Concrete Technology", "Structural Design", "BIM", "STAAD Pro"],
        "category": "Civil & Structural Engineering"
    },
    "Mechanical & Industrial Engineer": {
        "skills": ["SolidWorks", "CATIA", "HVAC Systems", "Thermal Analysis", "Pneumatics", "Hydraulics", "PLC Programming", "CNC Machining", "Mechanical Design", "GD&T"],
        "category": "Mechanical Engineering"
    },
    "Electrical & Automation Engineer": {
        "skills": ["Circuit Design", "MATLAB", "LabVIEW", "PCB Layout", "Power Systems", "Microcontrollers", "Embedded C", "SCADA", "Instrumentation", "Control Systems"],
        "category": "Electrical Engineering"
    },
    "Architect / Spatial Designer": {
        "skills": ["Architectural Design", "Interior Design", "SketchUp", "3D Rendering", "V-Ray", "Architectural Drafting", "Sustainable Design", "Spatial Planning", "BIM"],
        "category": "Architecture & Design"
    },

    # --- SUPPLY CHAIN, LOGISTICS & PROCUREMENT ---
    "Supply Chain & Operations Manager": {
        "skills": ["Supply Chain Optimization", "Inventory Management", "Procurement", "Warehouse Management", "ERP", "SAP S/4HANA", "Demand Forecasting", "Vendor Management", "Logistics Planning"],
        "category": "Supply Chain & Logistics"
    },
    "Logistics & Freight Coordinator": {
        "skills": ["Freight Forwarding", "Warehouse Management", "Logistics Planning", "Customs Clearance", "3PL", "Inventory Control", "Purchase Orders"],
        "category": "Supply Chain & Logistics"
    },

    # --- RETAIL, HOSPITALITY & REAL ESTATE ---
    "Hotel Operations / Hospitality Manager": {
        "skills": ["Hospitality Operations", "Front Desk Management", "Customer Experience", "POS Systems", "Food Safety", "Revenue Management", "Guest Services", "Event Planning"],
        "category": "Hospitality & Retail"
    },
    "Property & Real Estate Manager": {
        "skills": ["Property Valuation", "Asset Management", "Commercial Real Estate", "Real Estate Contracts", "Facility Management", "Tenant Relations", "Leasing Strategy"],
        "category": "Real Estate & Property Management"
    },

    # --- FINANCE, BANKING & ACCOUNTING ---
    "Financial Analyst / Investment Specialist": {
        "skills": ["Financial Modeling", "Financial Analysis", "Corporate Finance", "Valuation", "Risk Assessment", "Financial Reporting", "Excel", "Budgeting", "Cash Flow Management"],
        "category": "Finance & Banking"
    },
    "Corporate Accountant / Auditor": {
        "skills": ["Accounting", "Auditing", "Tax Compliance", "Financial Reporting", "QuickBooks", "SAP", "GAAP", "IFRS", "General Ledger"],
        "category": "Finance & Accounting"
    },

    # --- HUMAN RESOURCES & RECRUITING ---
    "HR Manager / HR Business Partner": {
        "skills": ["Employee Relations", "HR Policies", "Performance Management", "Onboarding", "Compensation & Benefits", "Workday", "BambooHR", "Labor Relations", "HRIS"],
        "category": "Human Resources"
    },
    "Talent Acquisition / Recruiting Specialist": {
        "skills": ["Talent Acquisition", "Technical Recruiting", "Sourcing", "Applicant Tracking Systems", "Onboarding", "Interviewing", "Employee Retention"],
        "category": "Human Resources"
    },

    # --- SALES, MARKETING & MEDIA ---
    "Sales Executive / Account Manager": {
        "skills": ["B2B Sales", "B2C Sales", "Business Development", "Account Management", "Lead Generation", "Salesforce", "HubSpot", "Sales Pipeline Management", "Strategic Negotiation"],
        "category": "Sales & Business Development"
    },
    "Digital Marketing & SEO Specialist": {
        "skills": ["SEO", "SEM", "Google Analytics", "Content Marketing", "Social Media Marketing", "PPC", "Growth Hacking", "Email Marketing", "Copywriting", "CRO"],
        "category": "Digital Marketing"
    },
    "Content Strategist / Technical Writer": {
        "skills": ["Content Strategy", "Technical Writing", "Copywriting", "Editing", "Journalism", "Storytelling", "SEO Writing", "Media Production"],
        "category": "Media & Content Creation"
    },

    # --- SOFTWARE & IT ENGINEERING ---
    "Full Stack Developer": {
        "skills": ["Python", "JavaScript", "TypeScript", "React", "Node.js", "SQL", "PostgreSQL", "HTML", "CSS", "Git", "REST APIs", "Docker", "MongoDB"],
        "category": "Software Engineering"
    },
    "Software Engineer": {
        "skills": ["Python", "Java", "C++", "C#", "SQL", "Git", "REST APIs", "Linux", "Data Structures", "Algorithms", "Object-Oriented Programming"],
        "category": "Software Engineering"
    },
    "Frontend Developer": {
        "skills": ["JavaScript", "TypeScript", "React", "Angular", "Vue.js", "HTML", "HTML5", "CSS", "CSS3", "SASS", "Tailwind CSS", "Redux", "Vite", "Webpack", "UI/UX Design"],
        "category": "Frontend Development"
    },
    "Backend Developer": {
        "skills": ["Python", "Java", "Node.js", "Django", "Flask", "FastAPI", "Spring Boot", "SQL", "PostgreSQL", "MySQL", "MongoDB", "Redis", "Docker", "REST APIs", "Microservices"],
        "category": "Backend Development"
    },
    "Data Scientist": {
        "skills": ["Python", "R", "SQL", "Machine Learning", "Deep Learning", "Pandas", "NumPy", "scikit-learn", "TensorFlow", "PyTorch", "Data Analysis", "Matplotlib"],
        "category": "Data Science & AI"
    },
    "Data Engineer": {
        "skills": ["Python", "SQL", "Apache Spark", "Hadoop", "Apache Airflow", "dbt", "Data Warehousing", "Snowflake", "BigQuery", "Kafka", "ETL", "Databricks"],
        "category": "Data Engineering"
    },
    "DevOps / Cloud Engineer": {
        "skills": ["AWS", "Azure", "Google Cloud", "GCP", "Docker", "Kubernetes", "Terraform", "Ansible", "Jenkins", "CI/CD", "Linux", "Bash", "Prometheus"],
        "category": "Cloud & DevOps"
    },
    "Desktop Support Engineer": {
        "skills": ["Active Directory", "Windows 10", "Windows 11", "Group Policy", "GPO", "Microsoft Intune", "SCCM", "Office 365", "RDP", "ServiceNow", "TCP/IP", "VPN", "Hardware Diagnostics", "BitLocker"],
        "category": "IT Support & Infrastructure"
    },
    "IT Support Engineer": {
        "skills": ["Active Directory", "Azure AD", "Windows Server", "Office 365", "Exchange Online", "ServiceNow", "Jira Service Desk", "TCP/IP", "DHCP", "DNS", "VPN", "LAN/WAN", "Ticket Management"],
        "category": "IT Support & Infrastructure"
    },
    "AI / ML Engineer": {
        "skills": ["Python", "Machine Learning", "Deep Learning", "Generative AI", "LLMs", "NLP", "TensorFlow", "PyTorch", "Computer Vision", "OpenCV", "Hugging Face", "LangChain"],
        "category": "AI & Data Science"
    },
    "QA & Test Automation Engineer": {
        "skills": ["Automated Testing", "Manual Testing", "Selenium", "Cypress", "Playwright", "JUnit", "PyTest", "Jest", "Postman", "Regression Testing", "TDD", "BDD"],
        "category": "QA & Software Testing"
    },
    "Product Manager": {
        "skills": ["Product Strategy", "Product Roadmap", "User Research", "Agile", "Scrum", "Wireframing", "Feature Prioritization", "Product Analytics", "A/B Testing", "PRD Writing"],
        "category": "Product Management"
    },
    "Project Manager / Operations Lead": {
        "skills": ["Project Management", "Program Management", "Agile", "Scrum", "PMP", "Risk Management", "Resource Allocation", "Budgeting", "Jira", "Stakeholder Management", "Six Sigma"],
        "category": "Project & Operations Management"
    },
    "UI/UX Designer": {
        "skills": ["Figma", "UI/UX Design", "User Experience", "User Interface", "Adobe Photoshop", "Adobe Illustrator", "Wireframing", "User Research", "Prototyping"],
        "category": "Design & User Experience"
    },
    "Cybersecurity Analyst": {
        "skills": ["Penetration Testing", "Ethical Hacking", "Network Security", "Information Security", "Cryptography", "OWASP Top 10", "SIEM", "Firewalls", "Wireshark"],
        "category": "Cybersecurity"
    }
}

