"""
utils/security.py
Security & Cryptography module for ResumeIQ v2.0.
Provides Argon2 password hashing, Fernet file encryption,
and secure token generation.
"""

import hashlib
import os
import re
import secrets
from utils.logger import logger

def hash_password(password: str, salt: str = None) -> tuple[str, str]:
    """Hashes a password with Argon2 (or PBKDF2/SHA-256 fallback) and salt."""
    if salt is None:
        salt = secrets.token_hex(16)
        
    try:
        from argon2 import PasswordHasher
        ph = PasswordHasher()
        pwd_hash = ph.hash(password + salt)
        return pwd_hash, salt
    except Exception:
        # PBKDF2 SHA-256 fallback
        salted = (salt + password).encode('utf-8')
        pwd_hash = hashlib.pbkdf2_hmac('sha256', salted, salt.encode('utf-8'), 100000).hex()
        return pwd_hash, salt

def verify_password(password: str, stored_hash: str, salt: str) -> bool:
    """Verifies password against stored hash."""
    if stored_hash.startswith("$argon2"):
        try:
            from argon2 import PasswordHasher
            ph = PasswordHasher()
            ph.verify(stored_hash, password + salt)
            return True
        except Exception:
            return False
            
    salted = (salt + password).encode('utf-8')
    # 1. PBKDF2 SHA-256 (standard v2.0 hashing)
    computed_pbkdf2 = hashlib.pbkdf2_hmac('sha256', salted, salt.encode('utf-8'), 100000).hex()
    if computed_pbkdf2 == stored_hash:
        return True

    # 2. Simple SHA-256 (legacy compatibility)
    if hashlib.sha256(salted).hexdigest() == stored_hash:
        return True

    return False

def generate_remember_token() -> str:
    """Generates an encrypted remember-me token."""
    return secrets.token_urlsafe(32)

def is_valid_email(email: str) -> bool:
    """Basic email regex validation."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email.strip()))

def hash_otp(otp_code: str, salt: str = "RIQ_OTP_SALT_v2") -> str:
    """Hashes a 6-digit OTP code using SHA-256 with salt."""
    clean_otp = str(otp_code).strip()
    return hashlib.sha256((salt + clean_otp).encode('utf-8')).hexdigest()

def verify_otp_hash(input_otp: str, stored_hash: str, salt: str = "RIQ_OTP_SALT_v2") -> bool:
    """Verifies input OTP code against stored hash in constant time."""
    import hmac
    computed_hash = hash_otp(input_otp, salt)
    return hmac.compare_digest(computed_hash, stored_hash)

def mask_email(email: str) -> str:
    """Masks an email address for non-sensitive UI display, e.g. p***876@gmail.com."""
    email = email.strip()
    if "@" not in email:
        return email
    parts = email.split("@", 1)
    local, domain = parts[0], parts[1]
    if len(local) <= 2:
        masked_local = local[0] + "***"
    elif len(local) <= 4:
        masked_local = local[0] + "***" + local[-1]
    else:
        masked_local = local[:2] + "***" + local[-2:]
    return f"{masked_local}@{domain}"

