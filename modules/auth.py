from database.database import db
from utils.security import is_valid_email
from typing import Optional, Dict, Any, Tuple
from modules.otp_service import otp_service

class AuthManager:
    @staticmethod
    def login(identifier: str, password: str) -> Tuple[Optional[Dict[str, Any]], str]:
        if not identifier or not password:
            return None, "Please enter your Username and Password."
        
        return db.authenticate_user(identifier, password)

    @staticmethod
    def register(name: str, email: str, password: str, confirm_password: str) -> Tuple[bool, str, str]:
        if not name or not email or not password or not confirm_password:
            return False, "Please fill in all required fields.", ""
        if not is_valid_email(email):
            return False, "Please enter a valid email address.", ""
        if len(password) < 6:
            return False, "Password must be at least 6 characters long.", ""
        if password != confirm_password:
            return False, "Passwords do not match.", ""

        return db.register_user(name, email, password)

    @staticmethod
    def reset_password(identifier: str, reset_token: str, new_password: str, confirm_password: str) -> Tuple[bool, str]:
        return otp_service.authorize_password_reset(identifier, reset_token, new_password, confirm_password)
