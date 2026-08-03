from database.database import db
from utils.security import is_valid_email
from typing import Optional, Dict, Any, Tuple

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
    def reset_password(identifier: str, new_password: str, confirm_password: str) -> Tuple[bool, str]:
        if not identifier or not new_password or not confirm_password:
            return False, "Please fill in all fields."
        if len(new_password) < 6:
            return False, "New password must be at least 6 characters long."
        if new_password != confirm_password:
            return False, "New passwords do not match."

        return db.update_user_password(identifier, new_password)
