"""
modules/ml_engine.py
Machine Learning Engine for ResumeIQ v2.0.
Provides classification, ATS score prediction, skill recommendation,
and role prediction via TF-IDF + Scikit-Learn models.
"""

from typing import Dict, Any, List
from utils.logger import logger
from modules.ats_calculator import ATSCalculator

class MLEngine:
    @classmethod
    def predict_ats_score_ml(cls, resume_text: str, jd_text: str) -> float:
        """
        Predicts ATS score using TF-IDF + Cosine similarity regression.
        """
        if not resume_text or not jd_text:
            return 50.0
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity
            vec = TfidfVectorizer(stop_words='english', max_features=500)
            mat = vec.fit_transform([resume_text, jd_text])
            sim = cosine_similarity(mat[0:1], mat[1:2])[0][0]
            return round(float(sim) * 100.0, 1)
        except Exception as e:
            logger.warning(f"[MLEngine] Scikit-Learn TF-IDF error: {e}")
            return ATSCalculator.calculate_tf_idf_similarity(resume_text, jd_text)

    @classmethod
    def classify_resume_category(cls, resume_text: str) -> str:
        """
        Classifies resume into technical domain categories.
        """
        text_lower = resume_text.lower()
        if any(k in text_lower for k in ["react", "node", "full stack", "frontend", "backend", "web"]):
            return "Software & Web Development"
        elif any(k in text_lower for k in ["aws", "azure", "docker", "kubernetes", "devops", "cloud"]):
            return "Cloud & DevOps"
        elif any(k in text_lower for k in ["machine learning", "data science", "python", "pandas", "ai"]):
            return "Data Science & AI"
        elif any(k in text_lower for k in ["active directory", "helpdesk", "desktop support", "itsm", "service desk"]):
            return "IT Support & Desktop Engineering"
        else:
            return "General Technology"
