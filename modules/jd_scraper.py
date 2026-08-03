"""
Feature 4: Job Description URL Auto-Scraper for ResumeIQ.
Scrapes job descriptions from LinkedIn, Naukri, Indeed, and other job portals.
"""

import re
from typing import Tuple
from utils.logger import logger

class JDScraper:
    """Scrapes job description text from popular job portal URLs."""

    # Known selectors for major job portals
    PORTAL_SELECTORS = {
        "linkedin.com": [
            "div.show-more-less-html__markup",
            "div.description__text",
            "section.description"
        ],
        "naukri.com": [
            "div.job-desc",
            "div.jd-desc",
            "div.dang-inner-html"
        ],
        "indeed.com": [
            "div#jobDescriptionText",
            "div.jobsearch-jobDescriptionText"
        ],
        "glassdoor.com": [
            "div.jobDescriptionContent",
            "div[class*='JobDescription']"
        ],
        "shine.com": [
            "div.job-description",
            "div#jd_description"
        ]
    }

    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }

    @classmethod
    def scrape(cls, url: str) -> Tuple[bool, str]:
        """
        Scrapes job description text from the given URL.
        Returns (success: bool, text_or_error: str).
        """
        url = url.strip()
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        try:
            import requests
            from bs4 import BeautifulSoup

            response = requests.get(url, headers=cls.HEADERS, timeout=12)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Remove script and style tags
            for tag in soup(["script", "style", "noscript"]):
                tag.decompose()

            # Try portal-specific selectors first
            portal_key = next((k for k in cls.PORTAL_SELECTORS if k in url), None)
            if portal_key:
                for selector in cls.PORTAL_SELECTORS[portal_key]:
                    el = soup.select_one(selector)
                    if el:
                        text = el.get_text(separator="\n", strip=True)
                        if len(text) > 100:
                            logger.info(f"[JD Scraper] Extracted {len(text)} chars from {portal_key}")
                            return True, text

            # Generic fallback: look for large text blocks
            candidates = []
            for tag in ["article", "section", "div", "main"]:
                for el in soup.find_all(tag):
                    text = el.get_text(separator=" ", strip=True)
                    if 200 < len(text) < 15000:
                        candidates.append(text)

            if candidates:
                best = max(candidates, key=len)
                # Clean up whitespace
                best = re.sub(r'\n{3,}', '\n\n', best)
                best = re.sub(r' {2,}', ' ', best)
                logger.info(f"[JD Scraper] Fallback extraction: {len(best)} chars from {url}")
                return True, best[:5000]

            return False, "Could not extract job description text from this URL. Try pasting the JD manually."

        except ImportError:
            return False, "BeautifulSoup4 not installed. Install it with: pip install beautifulsoup4"
        except Exception as e:
            logger.error(f"[JD Scraper] Error scraping {url}: {e}")
            return False, f"Failed to scrape URL: {str(e)}"
