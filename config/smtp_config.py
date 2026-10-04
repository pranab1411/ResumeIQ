"""
Internal Admin SMTP Gateway Configuration.
Loads credentials securely from an AES-256-GCM encrypted payload or environment variables.
Scrape-proof: Zero plaintext email addresses or 16-character app passwords exist here.
"""
import os
from utils.credential_cipher import decrypt_smtp_payload

# AES-256-GCM Encrypted Embedded Credentials Payload
# Generated via encrypt_smtp.py (Scrape-proof; zero plaintext credentials)
ENCRYPTED_SMTP_PAYLOAD = os.getenv("RESUMEIQ_ENCRYPTED_SMTP", "dSG6b6QilL6n2rcCIE1jNYmLKUpM91IWlUdJ0614GHt8g5i6vEoYDCO6lmKHcv87EjXWL7Bc8IWue7TKdBMstSD3bA9V6X1APq7N4lvA5-qA2ry8KtOY3O-0RBGg569bKAzHPVJuorQK_qfLeXEUWFM46WNSjFesaQ6OCMGU")

# Decrypt credentials at runtime if embedded payload exists
_creds = decrypt_smtp_payload(ENCRYPTED_SMTP_PAYLOAD) if ENCRYPTED_SMTP_PAYLOAD else {}

# Admin Sender Email Address (Configured via Encrypted Payload, Env Var, or UI Settings)
DEFAULT_SMTP_USER = os.getenv("RESUMEIQ_SMTP_USER", _creds.get("user", ""))

# Admin Google App Password (Configured via Encrypted Payload, Env Var, or UI Settings)
DEFAULT_SMTP_PASSWORD = os.getenv("RESUMEIQ_SMTP_PASSWORD", _creds.get("pass", ""))

# SMTP Gateway Server Settings
DEFAULT_SMTP_HOST = os.getenv("RESUMEIQ_SMTP_HOST", _creds.get("host", "smtp.gmail.com"))
DEFAULT_SMTP_PORT = int(os.getenv("RESUMEIQ_SMTP_PORT", str(_creds.get("port", 587))))


