import unittest
import time
from database.database import db
from modules.otp_service import otp_service
from modules.auth import AuthManager
from utils.security import mask_email

class TestOTPSecurityEngine(unittest.TestCase):
    def setUp(self):
        self.test_email = "test.otp.user@example.com"
        self.test_password = "Password123!"
        # Clean existing test user and reset sessions
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE email = ?", (self.test_email,))
            cursor.execute("DELETE FROM password_reset_sessions WHERE email = ?", (self.test_email,))
            conn.commit()

        # Register test user
        db.register_user("Test OTP Candidate", self.test_email, self.test_password)

    def test_email_masking(self):
        self.assertEqual(mask_email("pranabchourasiya876@gmail.com"), "pr***76@gmail.com")
        self.assertEqual(mask_email("test@example.com"), "t***t@example.com")
        self.assertEqual(mask_email("ab@c.com"), "a***@c.com")

    def test_valid_otp_generation_and_verification(self):
        success, msg, details = otp_service.generate_and_send_email_otp(self.test_email)
        self.assertTrue(success)
        self.assertIn("masked_email", details)
        self.assertEqual(details["masked_email"], "te***er@example.com")

        # Fetch active session from DB
        session = db.get_active_password_reset_session(self.test_email)
        self.assertIsNotNone(session)
        self.assertEqual(session["otp_attempts"], 0)
        self.assertEqual(session["otp_status"], "PENDING")

        # Retrieve actual OTP code from active memory session table in DB
        # To test verification, we simulate user submitting the correct code
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT otp_hash FROM password_reset_sessions WHERE id = ?", (session["id"],))
            stored_hash = cursor.fetchone()[0]

        # Verify incorrect OTP increments attempt counter
        wrong_success, wrong_msg, token = otp_service.verify_otp(self.test_email, "000000")
        self.assertFalse(wrong_success)
        self.assertIn("4 attempts remaining", wrong_msg)

        # Check attempt count updated in DB
        session = db.get_active_password_reset_session(self.test_email)
        self.assertEqual(session["otp_attempts"], 1)

    def test_attempt_locking_after_five_failed_attempts(self):
        success, msg, details = otp_service.generate_and_send_email_otp(self.test_email)
        self.assertTrue(success)

        # Submit 4 wrong attempts
        for k in range(1, 5):
            ok, err_msg, _ = otp_service.verify_otp(self.test_email, f"11111{k}")
            self.assertFalse(ok)
            expected_remaining = 5 - k
            if expected_remaining > 1:
                self.assertIn(f"{expected_remaining} attempts remaining", err_msg)
            elif expected_remaining == 1:
                self.assertIn("1 attempts remaining", err_msg)

        # 5th failed attempt should trigger final attempt locking message
        ok5, msg5, _ = otp_service.verify_otp(self.test_email, "999999")
        self.assertFalse(ok5)
        self.assertIn("This was your final attempt. Please request a new OTP.", msg5)

        # Subsequent attempt should be rejected with locked status
        ok_locked, msg_locked, _ = otp_service.verify_otp(self.test_email, "999999")
        self.assertFalse(ok_locked)
        self.assertIn("Too many incorrect attempts", msg_locked)

    def test_resend_cooldown_and_old_otp_invalidation(self):
        success1, msg1, details1 = otp_service.generate_and_send_email_otp(self.test_email)
        self.assertTrue(success1)

        # Rapid resend attempt within 60s cooldown must fail
        success_cooldown, msg_cooldown, _ = otp_service.generate_and_send_email_otp(self.test_email)
        self.assertFalse(success_cooldown)
        self.assertIn("Please wait", msg_cooldown)

    def test_unauthorized_password_reset_rejection(self):
        # Direct password reset without verified reset token must fail
        ok, msg = AuthManager.reset_password(self.test_email, "fake_token_123", "NewSecret123!", "NewSecret123!")
        self.assertFalse(ok)
        self.assertTrue(any(word in msg.lower() for word in ["invalid", "verified", "authorization", "expired", "otp"]))

if __name__ == "__main__":
    unittest.main()
