"""
Internal Admin SMTP Gateway Configuration.
Embedded in source code for automated background Real Email OTP delivery.
Hidden from end-user UI screens.
"""
import os

# Admin Sender Email Address
DEFAULT_SMTP_USER = os.getenv("RESUMEIQ_SMTP_USER", "support.resumeiq@gmail.com")

# Admin Google App Password (16 characters)
DEFAULT_SMTP_PASSWORD = os.getenv("RESUMEIQ_SMTP_PASSWORD", "vjmynneneydhzipn")

# SMTP Gateway Server Settings
DEFAULT_SMTP_HOST = "smtp.gmail.com"
DEFAULT_SMTP_PORT = 587
