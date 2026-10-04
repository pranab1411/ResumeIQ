"""
Internal Admin SMTP Gateway Configuration.
Loads credentials securely from an AES-256-GCM encrypted payload or environment variables.
Scrape-proof: Zero plaintext email addresses or 16-character app passwords exist here.
"""
import os
from utils.credential_cipher import decrypt_smtp_payload

# AES-256-GCM Encrypted Embedded Credentials Payload
# Generated via encrypt_smtp.py
ENCRYPTED_SMTP_PAYLOAD = os.getenv("RESUMEIQ_ENCRYPTED_SMTP", "")

# Decrypt credentials at runtime if embedded payload exists
_creds = decrypt_smtp_payload(ENCRYPTED_SMTP_PAYLOAD) if ENCRYPTED_SMTP_PAYLOAD else {}

# Admin Sender Email Address (Configured via Encrypted Payload, Env Var, or UI Settings)
DEFAULT_SMTP_USER = os.getenv("RESUMEIQ_SMTP_USER", _creds.get("user", ""))

# Admin Google App Password (Configured via Encrypted Payload, Env Var, or UI Settings)
DEFAULT_SMTP_PASSWORD = os.getenv("RESUMEIQ_SMTP_PASSWORD", _creds.get("pass", ""))

# SMTP Gateway Server Settings
DEFAULT_SMTP_HOST = os.getenv("RESUMEIQ_SMTP_HOST", _creds.get("host", "smtp.gmail.com"))
DEFAULT_SMTP_PORT = int(os.getenv("RESUMEIQ_SMTP_PORT", str(_creds.get("port", 587))))


