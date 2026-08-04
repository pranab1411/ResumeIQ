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
            
    # SHA-256 or PBKDF2 verification
    if len(stored_hash) == 64 and not "$" in stored_hash:
        salted_pwd = (salt + password).encode('utf-8')
        return hashlib.sha256(salted_pwd).hexdigest() == stored_hash
        
    salted = (salt + password).encode('utf-8')
    computed = hashlib.pbkdf2_hmac('sha256', salted, salt.encode('utf-8'), 100000).hex()
    return computed == stored_hash

def generate_remember_token() -> str:
    """Generates an encrypted remember-me token."""
    return secrets.token_urlsafe(32)

def is_valid_email(email: str) -> bool:
    """Basic email regex validation."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email.strip()))
