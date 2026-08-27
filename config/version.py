"""
ResumeIQ Central Version & Build Type Configuration
"""

APP_VERSION = "2.0"
BUILD_TYPE = "Production"

def get_app_version_string() -> str:
    if BUILD_TYPE.lower() == "production":
        return f"ResumeIQ v{APP_VERSION} (Production Build)"
    return f"ResumeIQ v{APP_VERSION} ({BUILD_TYPE})"

def get_splash_version_string() -> str:
    if BUILD_TYPE.lower() == "production":
        return f"v{APP_VERSION} • Hybrid Gemini AI & Local Intelligence"
    return f"v{APP_VERSION} ({BUILD_TYPE}) • Hybrid Gemini AI & Local Intelligence"
