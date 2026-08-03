import hashlib
import os
import re

def hash_password(password: str, salt: str = None) -> tuple[str, str]:
    """Hashes a password with SHA-256 and salt. Returns (password_hash, salt)."""
    if salt is None:
        salt = os.urandom(16).hex()
    
    salted_pwd = (salt + password).encode('utf-8')
    pwd_hash = hashlib.sha256(salted_pwd).hexdigest()
    return pwd_hash, salt

def verify_password(password: str, stored_hash: str, salt: str) -> bool:
    """Verifies if the provided password matches the stored hash given the salt."""
    computed_hash, _ = hash_password(password, salt)
    return computed_hash == stored_hash

def is_valid_email(email: str) -> bool:
    """Basic email regex validation."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email.strip()))
