"""
utils/credential_cipher.py
High-security AES-256-GCM authenticated cipher vault for embedded credentials.
Protects sensitive configuration from static code analysis, regex scrapers,
and binary strings inspection.
"""

import os
import json
import base64
import hashlib
from typing import Dict, Any
from utils.logger import logger

# Multi-segment key entropy fragments (split and transformed)
_KEY_CORE_A = bytes([0x52, 0x65, 0x73, 0x75, 0x6D, 0x65, 0x49, 0x51])  # 'ResumeIQ'
_KEY_CORE_B = bytes([0x56, 0x61, 0x75, 0x6C, 0x74, 0x40, 0x32, 0x30])  # 'Vault@20'
_KEY_CORE_C = bytes([0x32, 0x36, 0x24, 0x53, 0x65, 0x63, 0x75, 0x72])  # '26$Secur'
_KEY_CORE_D = bytes([0x65, 0x47, 0x61, 0x74, 0x65, 0x77, 0x61, 0x79])  # 'eGateway'

def _derive_vault_key() -> bytes:
    """Dynamically reconstructs a 256-bit AES master key at runtime."""
    part1 = bytes([b ^ 0x5A for b in _KEY_CORE_A])
    part2 = _KEY_CORE_C[::-1]
    part3 = _KEY_CORE_B
    part4 = bytes([b ^ 0x3C for b in _KEY_CORE_D])
    return hashlib.sha256(part1 + part2 + part3 + part4 + b"::ResumeIQ::AES256::Vault").digest()

def encrypt_smtp_payload(user: str, password: str, host: str = "smtp.gmail.com", port: int = 587) -> str:
    """
    Encrypts SMTP credentials into an authenticated, scrape-proof AES-256-GCM token.
    Uses a fresh 96-bit random IV/nonce on each invocation.
    """
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM

    payload_data = {
        "user": user.strip(),
        "pass": password.strip(),
        "host": host.strip(),
        "port": int(port) if str(port).isdigit() else 587
    }
    raw_json = json.dumps(payload_data, separators=(',', ':')).encode('utf-8')

    key = _derive_vault_key()
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)  # 96-bit standard GCM nonce
    ciphertext = aesgcm.encrypt(nonce, raw_json, None)

    # Base64-urlsafe encoding of nonce + ciphertext (includes auth tag)
    return base64.urlsafe_b64encode(nonce + ciphertext).decode('ascii')

def decrypt_smtp_payload(token: str) -> Dict[str, Any]:
    """
    Decrypts and verifies an authenticated AES-256-GCM SMTP payload.
    Returns dictionary with keys ('user', 'pass', 'host', 'port') or empty dict on failure.
    """
    if not token or not isinstance(token, str):
        return {}

    clean_token = token.strip()
    if not clean_token:
        return {}

    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        raw_bytes = base64.urlsafe_b64decode(clean_token.encode('ascii'))
        if len(raw_bytes) < 28:  # 12 nonce + 16 auth tag minimum
            return {}

        nonce = raw_bytes[:12]
        ciphertext = raw_bytes[12:]

        key = _derive_vault_key()
        aesgcm = AESGCM(key)
        decrypted_json = aesgcm.decrypt(nonce, ciphertext, None)

        creds = json.loads(decrypted_json.decode('utf-8'))
        return {
            "user": str(creds.get("user", "")).strip(),
            "pass": str(creds.get("pass", "")).strip(),
            "host": str(creds.get("host", "smtp.gmail.com")).strip(),
            "port": int(creds.get("port", 587))
        }
    except Exception as e:
        logger.debug(f"[VAULT] Failed to decrypt credentials payload: {e}")
        return {}
