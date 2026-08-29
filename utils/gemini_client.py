"""
utils/gemini_client.py
Centralized Gemini API client for ResumeIQ.
All modules should use this instead of building raw HTTP requests.
"""

import json
import os
import urllib.request
import urllib.error
from typing import List, Optional, Dict, Any
from utils.logger import logger

# Current working model — updated to 2026 Gemini model standards (gemini-3.6-flash)
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.6-flash")
GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"

FALLBACK_MODELS = [
    "gemini-3.6-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.5-flash",
    "gemini-flash-latest",
    "gemini-flash-lite-latest",
    "gemini-3.7-flash",
    "gemini-3.1-flash-lite",
    "gemini-pro-latest"
]

def fetch_available_models(api_key: str) -> List[str]:
    """Dynamically queries Google Gemini API ListModels endpoint to get all active generation models."""
    if not api_key:
        return []
    try:
        url = f"{GEMINI_API_BASE}?key={api_key}"
        req = urllib.request.Request(url, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=6) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            active_models = []
            for m in data.get("models", []):
                methods = m.get("supportedGenerationMethods", [])
                if "generateContent" in methods:
                    m_name = m["name"].replace("models/", "")
                    active_models.append(m_name)
            if active_models:
                logger.info(f"[Gemini] Dynamically discovered {len(active_models)} available API models.")
                return active_models
    except Exception as e:
        logger.warning(f"[Gemini] Dynamic model discovery fallback: {e}")
    return []

def _get_api_key() -> str:
    """Retrieve API key from environment or DB settings."""
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if key:
        return key
    try:
        from database.database import db
        key = db.get_setting("gemini_api_key") or ""
    except Exception:
        pass
    return key.strip()


def gemini_generate(
    prompt: str,
    *,
    model: str = GEMINI_MODEL,
    temperature: float = 0.7,
    max_tokens: int = 4096,
    timeout: int = 20,
    response_mime_type: Optional[str] = None,
) -> str:
    """
    Send a prompt to Gemini and return the text response with automatic model fallback.
    Supports response_mime_type="application/json" to guarantee structured JSON output.
    Raises GeminiError on failure.
    """
    api_key = _get_api_key()
    if not api_key:
        raise GeminiError("No Gemini API key configured. Add it in Settings.")

    models_to_try = [model] + [m for m in FALLBACK_MODELS if m != model]
    last_error = None

    gen_config: Dict[str, Any] = {
        "temperature": temperature,
        "maxOutputTokens": max_tokens,
    }
    if response_mime_type:
        gen_config["responseMimeType"] = response_mime_type

    for m in models_to_try:
        url = f"{GEMINI_API_BASE}/{m}:generateContent?key={api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": gen_config,
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url, data=data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                candidates = result.get("candidates", [])
                if not candidates:
                    raise GeminiError("Empty candidates in Gemini response.")
                return candidates[0]["content"]["parts"][0]["text"].strip()
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="ignore")[:300]
            if e.code == 404:
                logger.warning(f"[Gemini] Model '{m}' returned 404, attempting fallback model...")
                last_error = GeminiError(f"Model {m} not found (HTTP 404).")
                continue
            logger.error(f"[Gemini] HTTP {e.code}: {body}")
            if e.code == 429:
                logger.warning(f"[Gemini] Model '{m}' hit quota/rate limit (HTTP 429). Attempting fallback model...")
                last_error = GeminiError("Gemini API rate limit or quota exceeded across all attempted models. Please wait a moment and try again.")
                continue
            if e.code == 403:
                raise GeminiError("Gemini API key invalid or quota exhausted.")
            last_error = GeminiError(f"Gemini HTTP error {e.code}: {body}")
            continue
        except Exception as e:
            logger.error(f"[Gemini] Request failed on model {m}: {e}")
            last_error = GeminiError(str(e))
            continue

    # Secondary Dynamic Model Discovery Fallback
    logger.info("[Gemini] Fallback models exhausted. Attempting dynamic model discovery from Google ListModels API...")
    discovered = fetch_available_models(api_key)
    for m in discovered:
        if m in models_to_try:
            continue
        url = f"{GEMINI_API_BASE}/{m}:generateContent?key={api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": gen_config,
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url, data=data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                candidates = result.get("candidates", [])
                if candidates:
                    return candidates[0]["content"]["parts"][0]["text"].strip()
        except urllib.error.HTTPError as e:
            logger.warning(f"[Gemini] Discovered model '{m}' returned HTTP {e.code}. Continuing...")
            continue
        except Exception as e:
            logger.warning(f"[Gemini] Discovered model '{m}' failed ({e}). Continuing...")
            continue

    if last_error:
        raise last_error
    raise GeminiError("All Gemini model attempts failed.")


def gemini_available() -> bool:
    """Returns True if a Gemini API key is configured."""
    return bool(_get_api_key())



class GeminiError(Exception):
    """Raised when a Gemini API call fails."""
    pass
