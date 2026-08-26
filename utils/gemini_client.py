"""
utils/gemini_client.py
Centralized Gemini API client for ResumeIQ.
All modules should use this instead of building raw HTTP requests.
"""

import json
import os
import urllib.request
import urllib.error
from utils.logger import logger

# Current working model — update here if Google deprecates it
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")
GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"


FALLBACK_MODELS = ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-2.5-flash", "gemini-1.5-pro"]

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
    max_tokens: int = 2048,
    timeout: int = 20,
) -> str:
    """
    Send a prompt to Gemini and return the text response with automatic model fallback.
    Raises GeminiError on failure.
    """
    api_key = _get_api_key()
    if not api_key:
        raise GeminiError("No Gemini API key configured. Add it in Settings.")

    models_to_try = [model] + [m for m in FALLBACK_MODELS if m != model]
    last_error = None

    for m in models_to_try:
        url = f"{GEMINI_API_BASE}/{m}:generateContent?key={api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            },
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
                raise GeminiError("Gemini rate limit reached. Please wait and try again.")
            if e.code == 403:
                raise GeminiError("Gemini API key invalid or quota exhausted.")
            raise GeminiError(f"Gemini HTTP error {e.code}: {body}")
        except Exception as e:
            logger.error(f"[Gemini] Request failed on model {m}: {e}")
            last_error = GeminiError(str(e))
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
