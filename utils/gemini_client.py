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
GEMINI_MODEL = "gemini-2.0-flash"
GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"


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
    Send a prompt to Gemini and return the text response.
    Raises GeminiError on failure.
    """
    api_key = _get_api_key()
    if not api_key:
        raise GeminiError("No Gemini API key configured. Add it in Settings.")

    url = f"{GEMINI_API_BASE}/{model}:generateContent?key={api_key}"
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
        logger.error(f"[Gemini] HTTP {e.code}: {body}")
        if e.code == 429:
            raise GeminiError("Gemini rate limit reached. Please wait and try again.")
        if e.code == 403:
            raise GeminiError("Gemini API key invalid or quota exhausted.")
        raise GeminiError(f"Gemini HTTP error {e.code}: {body}")
    except Exception as e:
        logger.error(f"[Gemini] Request failed: {e}")
        raise GeminiError(str(e))


def gemini_available() -> bool:
    """Returns True if a Gemini API key is configured."""
    return bool(_get_api_key())


class GeminiError(Exception):
    """Raised when a Gemini API call fails."""
    pass
