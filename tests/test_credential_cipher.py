import unittest
from utils.credential_cipher import encrypt_smtp_payload, decrypt_smtp_payload

class TestCredentialCipher(unittest.TestCase):
    def test_encryption_decryption_cycle(self):
        user = "test.sender@example.com"
        pwd = "very_secret_app_password_123"
        host = "smtp.gmail.com"
        port = 587

        token = encrypt_smtp_payload(user, pwd, host, port)
        self.assertIsInstance(token, str)
        self.assertGreater(len(token), 30)

        # Plaintext secrets must not appear in the token string
        self.assertNotIn(user, token)
        self.assertNotIn(pwd, token)

        creds = decrypt_smtp_payload(token)
        self.assertEqual(creds.get("user"), user)
        self.assertEqual(creds.get("pass"), pwd)
        self.assertEqual(creds.get("host"), host)
        self.assertEqual(creds.get("port"), port)

    def test_random_nonce_uniqueness(self):
        # Two encryptions of the same plaintext must produce different ciphertexts
        token1 = encrypt_smtp_payload("user@example.com", "pass123")
        token2 = encrypt_smtp_payload("user@example.com", "pass123")
        self.assertNotEqual(token1, token2)

    def test_corrupted_token_handling(self):
        # Tampered or corrupted tokens should return empty dictionary without crashing
        self.assertEqual(decrypt_smtp_payload(""), {})
        self.assertEqual(decrypt_smtp_payload("invalid_token"), {})
        self.assertEqual(decrypt_smtp_payload(None), {})

if __name__ == "__main__":
    unittest.main()
