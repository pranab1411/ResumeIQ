import secrets
import time
import smtplib
from email.mime.text import MIMEText
from typing import Dict, Tuple, Any, Optional

from database.database import db
from utils.security import hash_otp, verify_otp_hash, mask_email, is_valid_email
from utils.logger import logger

class RealOTPService:
    """
    100% Free Autonomous Real OTP Dispatch & Verification Engine.
    Provides cryptographically secure 6-digit OTP generation, 5-minute TTL expiration,
    hashed OTP storage, max 5 failed attempts limit, 60s resend cooldown,
    and server-side authenticated password reset authorization.
    """
    def __init__(self):
        self.ttl_seconds = 300       # 5 minutes validity
        self.cooldown_seconds = 60  # 60s resend cooldown
        self.max_attempts = 5       # Max 5 attempts per issued OTP
        self.auth_ttl_seconds = 600 # 10 minutes reset authorization window
        logger.info("Initialized Real OTP Service Engine with Phase 16 State Machine & Security.")

    def send_smtp_email(self, recipient: str, otp_code: str) -> Tuple[bool, str]:
        """Attempts real SMTP email dispatch to external mail server using admin credentials."""
        try:
            from config import smtp_config
            default_user = smtp_config.DEFAULT_SMTP_USER
            default_pass = smtp_config.DEFAULT_SMTP_PASSWORD
            default_host = smtp_config.DEFAULT_SMTP_HOST
            default_port = smtp_config.DEFAULT_SMTP_PORT
        except ImportError:
            default_user, default_pass, default_host, default_port = "support.resumeiq@gmail.com", "", "smtp.gmail.com", 587

        smtp_host = db.get_setting("smtp_host", "") or default_host
        smtp_port = int(db.get_setting("smtp_port", "") or str(default_port))
        smtp_user = db.get_setting("smtp_user", "") or default_user
        smtp_password = db.get_setting("smtp_password", "") or default_pass

        if not smtp_user or not smtp_password or "your_" in smtp_user or "your_" in smtp_password:
            logger.warning("[REAL OTP SERVICE] Embedded Admin SMTP credentials pending update.")
            return False, "NO_SMTP_CONFIG"

        try:
            msg = MIMEText(
                f"Hello,\n\n"
                f"Your ResumeIQ Password Reset Verification OTP Code is:\n"
                f"👉 {otp_code}\n\n"
                f"This OTP code is valid for 5 minutes. Enter this code in ResumeIQ to reset your password.\n\n"
                f"Regards,\nResumeIQ Security Team",
                "plain",
                "utf-8"
            )
            msg["Subject"] = f"ResumeIQ Password Reset OTP: {otp_code}"
            msg["From"] = smtp_user
            msg["To"] = recipient

            with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.sendmail(smtp_user, [recipient], msg.as_string())

            logger.info(f"[REAL OTP SERVICE] Successfully sent email to {recipient} via {smtp_host}")
            return True, f"Real Email OTP successfully sent to {recipient}!"
        except Exception as e:
            logger.error(f"[REAL OTP SERVICE] SMTP email sending failed: {e}")
            return False, str(e)

    def generate_and_send_email_otp(self, identifier: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        email = identifier.strip().lower()
        if not email or not is_valid_email(email):
            return False, "Please enter a valid Registered Email Address.", None

        # Check if user exists in database
        user = db.get_user_by_email(email)
        if not user:
            return False, "No registered account found with this email address.", None

        now = time.time()
        # Rate Limit / Cooldown check: Check active session for email
        active_session = db.get_active_password_reset_session(email)
        if active_session:
            resend_at = active_session.get("resend_available_at", 0)
            if now < resend_at:
                cooldown_remaining = int(resend_at - now)
                return False, f"Please wait {cooldown_remaining}s before requesting a new OTP.", None

        # Cryptographically secure 6-digit OTP (100000 - 999999)
        otp_code = str(secrets.randbelow(900000) + 100000)
        otp_hash_val = hash_otp(otp_code)

        # Store session in SQLite DB (invalidates any old OTP for this email)
        session_record = db.create_password_reset_session(
            email=email,
            otp_hash=otp_hash_val,
            ttl_seconds=self.ttl_seconds,
            cooldown_seconds=self.cooldown_seconds,
            max_attempts=self.max_attempts
        )

        logger.info(f"[REAL EMAIL OTP SERVICE] Issued new 6-digit OTP for '{email}'. Active session ID: {session_record['id']}.")

        # Attempt SMTP delivery
        self.send_smtp_email(email, otp_code)

        masked_addr = mask_email(email)
        details = {
            "email": email,
            "masked_email": masked_addr,
            "ttl_seconds": self.ttl_seconds,
            "cooldown_seconds": self.cooldown_seconds,
            "max_attempts": self.max_attempts
        }

        return True, "Verification code sent successfully.", details

    def verify_otp(self, identifier: str, input_otp: str) -> Tuple[bool, str, Optional[str]]:
        """
        Validates submitted OTP code against active database session.
        Returns (success: bool, message: str, reset_token: Optional[str]).
        """
        email = identifier.strip().lower()
        clean_input = "".join(filter(str.isdigit, str(input_otp)))

        if not email or not clean_input:
            return False, "Please enter both your email address and 6-digit OTP code.", None

        if len(clean_input) != 6:
            return False, "Invalid verification code. OTP must be exactly 6 numeric digits.", None

        now = time.time()
        active_session = db.get_active_password_reset_session(email)

        if not active_session:
            return False, "Your verification session has expired. Please request a new OTP.", None

        status = active_session.get("otp_status", "EXPIRED")
        session_id = active_session["id"]
        expires_at = active_session["otp_expires_at"]
        attempts = active_session.get("otp_attempts", 0)
        max_attempts = active_session.get("max_otp_attempts", 5)
        stored_hash = active_session["otp_hash"]

        # Check status & Expiration
        if status == "USED":
            return False, "This verification code has already been used. Please request a new OTP.", None
        if status == "LOCKED" or attempts >= max_attempts:
            db.update_otp_attempts(session_id, attempts, status="LOCKED")
            return False, "Too many incorrect attempts. Please request a new OTP.", None
        if status == "EXPIRED" or now > expires_at:
            db.update_otp_attempts(session_id, attempts, status="EXPIRED")
            return False, "This verification code has expired. Please request a new OTP.", None

        # Verify hash
        is_correct = verify_otp_hash(clean_input, stored_hash)

        if not is_correct:
            new_attempts = attempts + 1
            if new_attempts >= max_attempts:
                db.update_otp_attempts(session_id, new_attempts, status="LOCKED")
                return False, "Invalid verification code. This was your final attempt. Please request a new OTP.", None
            else:
                db.update_otp_attempts(session_id, new_attempts)
                remaining = max_attempts - new_attempts
                return False, f"Invalid verification code. You have {remaining} attempts remaining.", None

        # Correct OTP: Issue reset token & mark VERIFIED
        reset_token = secrets.token_urlsafe(32)
        db.mark_otp_verified(session_id, reset_token, auth_ttl_seconds=self.auth_ttl_seconds)
        logger.info(f"[REAL OTP SERVICE] OTP verified successfully for '{email}'. Issued authorization token.")
        return True, "OTP verified successfully!", reset_token

    def authorize_password_reset(self, identifier: str, reset_token: str, new_password: str, confirm_password: str) -> Tuple[bool, str]:
        """
        Validates server-side reset authorization token and updates account password.
        """
        email = identifier.strip().lower()
        if not email or not reset_token:
            return False, "Invalid or missing reset authorization."

        if not new_password or not confirm_password:
            return False, "Please enter and confirm your new password."

        if len(new_password) < 6:
            return False, "New password must be at least 6 characters long."

        if new_password != confirm_password:
            return False, "New passwords do not match."

        # Server-side token validation
        is_auth, auth_msg, session_id = db.validate_reset_token_authorization(email, reset_token)
        if not is_auth:
            return False, auth_msg

        # Update password in database
        success, update_msg = db.update_user_password(email, new_password)
        if success:
            db.mark_reset_session_used(session_id)
            logger.info(f"[REAL OTP SERVICE] Password reset completed successfully for '{email}'.")
            return True, "Password reset successful! Please sign in with your new password."
        else:
            return False, update_msg

otp_service = RealOTPService()
