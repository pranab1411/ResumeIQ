"""
modules/semantic_engine.py
Semantic Similarity Engine using SentenceTransformers with TF-IDF fallback.
"""

from utils.logger import logger

_model_cache = None

def _get_transformer_model():
    global _model_cache
    if _model_cache is not None:
        return _model_cache
    try:
        from sentence_transformers import SentenceTransformer
        logger.info("[SemanticEngine] Loading SentenceTransformer 'all-MiniLM-L6-v2'...")
        _model_cache = SentenceTransformer('all-MiniLM-L6-v2')
        return _model_cache
    except Exception as e:
        logger.warning(f"[SemanticEngine] SentenceTransformers unavailable ({e}), using TF-IDF fallback.")
        return None

class SemanticEngine:
    @staticmethod
    def calculate_similarity(text1: str, text2: str) -> float:
        """
        Calculates semantic similarity (0.0 to 100.0) between text1 and text2.
        """
        if not text1 or not text2:
            return 50.0

        model = _get_transformer_model()
        if model is not None:
            try:
                from sentence_transformers import util
                emb1 = model.encode(text1, convert_to_tensor=True)
                emb2 = model.encode(text2, convert_to_tensor=True)
                sim = util.cos_sim(emb1, emb2).item()
                return round(min(100.0, max(0.0, float(sim) * 100.0)), 1)
            except Exception as err:
                logger.warning(f"[SemanticEngine] Embedding calc error: {err}")

        # Fallback TF-IDF
        from modules.ats_calculator import ATSCalculator
        return ATSCalculator.calculate_tf_idf_similarity(text1, text2)
