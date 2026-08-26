import os
import unittest
import tempfile
from database.database import DatabaseManager
from utils.security import hash_password, verify_password

class TestDatabase(unittest.TestCase):
    def setUp(self):
        # Create a temporary SQLite database for isolated unit testing
        self.temp_db_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db_path = self.temp_db_file.name
        self.temp_db_file.close()
        self.db = DatabaseManager(self.temp_db_path)

    def tearDown(self):
        try:
            if os.path.exists(self.temp_db_path):
                os.remove(self.temp_db_path)
        except Exception:
            pass

    def test_user_registration_and_authentication(self):
        success, msg, username = self.db.register_user("Alice Tester", "alice@test.com", "SecurePass123!")
        self.assertTrue(success)
        self.assertTrue(username.startswith("riq_alice_"))

        # Authenticate with correct password
        user, auth_msg = self.db.authenticate_user("alice@test.com", "SecurePass123!")
        self.assertIsNotNone(user)
        self.assertEqual(user["name"], "Alice Tester")

        # Authenticate with incorrect password
        bad_user, bad_msg = self.db.authenticate_user("alice@test.com", "WrongPassword!")
        self.assertIsNone(bad_user)

    def test_duplicate_user_registration(self):
        s1, m1, u1 = self.db.register_user("Bob", "bob@test.com", "Pass1234!")
        self.assertTrue(s1)
        s2, m2, u2 = self.db.register_user("Bob 2", "bob@test.com", "Pass5678!")
        self.assertFalse(s2)

    def test_resume_lifecycle(self):
        s, m, u = self.db.register_user("Charlie", "charlie@test.com", "Pass1234!")
        user, _ = self.db.authenticate_user("charlie@test.com", "Pass1234!")
        resume_id = self.db.add_resume(user["id"], "resume.pdf", "/path/to/resume.pdf", "Raw text content")
        self.assertIsNotNone(resume_id)

        # Update analysis
        self.db.update_resume_analysis(resume_id, 88.5, "Software Engineer", "Required Python")
        resumes = self.db.get_user_resumes(user["id"])
        self.assertEqual(len(resumes), 1)
        self.assertEqual(float(resumes[0]["ats_score"]), 88.5)

    def test_app_settings(self):
        self.db.set_setting("test_key", "test_value_123")
        val = self.db.get_setting("test_key")
        self.assertEqual(val, "test_value_123")

    def test_security_password_hashing(self):
        hashed, salt = hash_password("Secret123")
        self.assertTrue(verify_password("Secret123", hashed, salt))
        self.assertFalse(verify_password("WrongSecret", hashed, salt))

if __name__ == "__main__":
    unittest.main()
