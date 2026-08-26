"""
Feature 19: Auto-Updater Checker for ResumeIQ.
Checks GitHub releases API for a newer version on app startup.
"""

from typing import Tuple
from utils.logger import logger
from config.version import APP_VERSION

CURRENT_VERSION = APP_VERSION
GITHUB_RELEASES_API = "https://api.github.com/repos/pranab1411/ResumeIQ/releases/latest"

class AppUpdater:
    """Checks for new ResumeIQ releases on GitHub."""

    @staticmethod
    def check_for_updates() -> Tuple[bool, str, str, str]:
        """
        Checks GitHub releases API for a newer version.
        Returns (update_available: bool, latest_version: str, release_notes: str, download_url: str)
        """
        try:
            import requests
            headers = {"User-Agent": "ResumeIQ-Desktop-App"}
            resp = requests.get(GITHUB_RELEASES_API, headers=headers, timeout=5)
            if resp.status_code != 200:
                return False, CURRENT_VERSION, "", ""

            data = resp.json()
            latest_tag = data.get("tag_name", "").lstrip("v")
            release_notes = data.get("body", "No release notes available.")[:500]
            download_url = data.get("html_url", "")

            if not latest_tag:
                return False, CURRENT_VERSION, "", ""

            update_available = AppUpdater._is_newer(latest_tag, CURRENT_VERSION)
            logger.info(f"[Updater] Current: v{CURRENT_VERSION}, Latest: v{latest_tag}, Update: {update_available}")
            return update_available, latest_tag, release_notes, download_url

        except Exception as e:
            logger.debug(f"[Updater] Update check skipped (offline or error): {e}")
            return False, CURRENT_VERSION, "", ""

    @staticmethod
    def _is_newer(latest: str, current: str) -> bool:
        """Compares semantic version strings."""
        try:
            def parse(v):
                return tuple(int(x) for x in v.split("."))
            return parse(latest) > parse(current)
        except Exception:
            return False

    @staticmethod
    def get_current_version() -> str:
        return CURRENT_VERSION
