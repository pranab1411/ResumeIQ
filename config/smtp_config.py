"""
Internal Admin SMTP Gateway Configuration.
Loads credentials securely from environment variables.
"""
import os

# Admin Sender Email Address (Configured via Environment Variable)
DEFAULT_SMTP_USER = os.getenv("RESUMEIQ_SMTP_USER", "support.resumeiq@gmail.com")

# Admin Google App Password (Configured via Environment Variable)
DEFAULT_SMTP_PASSWORD = os.getenv("RESUMEIQ_SMTP_PASSWORD", "")

# SMTP Gateway Server Settings
DEFAULT_SMTP_HOST = os.getenv("RESUMEIQ_SMTP_HOST", "smtp.gmail.com")
DEFAULT_SMTP_PORT = int(os.getenv("RESUMEIQ_SMTP_PORT", "587"))

