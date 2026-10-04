#!/usr/bin/env python3
"""
encrypt_smtp.py
ResumeIQ Local SMTP Credential Encryption Utility.

Allows you to securely encrypt your new SMTP email and App Password using AES-256-GCM.
Outputs high-entropy ciphertext that can be embedded into config/smtp_config.py
without exposing plaintext credentials to GitHub scrapers or binary string extractors.
"""

import sys
import getpass
import os
import re

# Fix Windows console UTF-8 output encoding
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.credential_cipher import encrypt_smtp_payload, decrypt_smtp_payload
from modules.otp_service import otp_service

def main():
    print("=" * 65)
    print("🔐 ResumeIQ Local SMTP Credential Encryption Vault")
    print("   AES-256-GCM Authenticated Encryption Engine")
    print("=" * 65)
    print("Enter your new SMTP credentials below.")
    print("Passwords are typed silently and NEVER echoed or saved in plaintext.\n")

    # 1. Email
    while True:
        email = input("👉 Sender Email Address (e.g. your_email@gmail.com): ").strip()
        if "@" in email and "." in email:
            break
        print("   ❌ Invalid email format. Please try again.")

    # 2. App Password (hidden input)
    while True:
        password = getpass.getpass("👉 16-Character App Password (input hidden): ").strip()
        # Remove any spaces if user pasted with spaces
        password_clean = re.sub(r'\s+', '', password)
        if len(password_clean) >= 6:
            password = password_clean
            break
        print("   ❌ Password is too short. Google App Passwords are 16 characters.")

    # 3. SMTP Host
    host_input = input("👉 SMTP Host [default: smtp.gmail.com]: ").strip()
    host = host_input if host_input else "smtp.gmail.com"

    # 4. SMTP Port
    port_input = input("👉 SMTP Port [default: 587]: ").strip()
    try:
        port = int(port_input) if port_input else 587
    except ValueError:
        port = 587

    print("\n" + "-" * 65)
    print("⚡ Testing SMTP Connection & Authentication before encrypting...")
    ok, msg = otp_service.test_smtp_connection(host, port, email, password)
    if ok:
        print(f"   ✅ SUCCESS: {msg}")
    else:
        print(f"   ⚠️ WARNING: {msg}")
        choice = input("   Proceed with encryption anyway? (y/n) [default: y]: ").strip().lower()
        if choice == 'n':
            print("Aborted.")
            return

    # 5. Encrypt
    token = encrypt_smtp_payload(email, password, host, port)

    # 6. Verify decryption locally
    verified = decrypt_smtp_payload(token)
    assert verified.get("user") == email, "Integrity check failed: user mismatch!"
    assert verified.get("pass") == password, "Integrity check failed: password mismatch!"

    print("\n" + "=" * 65)
    print("🛡️ ENCRYPTION COMPLETE (AES-256-GCM)")
    print("=" * 65)
    print(f"Encrypted Payload Token:\n\n{token}\n")

    # Offer to automatically update config/smtp_config.py
    cfg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config", "smtp_config.py")
    if os.path.exists(cfg_path):
        auto_update = input("👉 Automatically update 'config/smtp_config.py' with this payload? (Y/n): ").strip().lower()
        if auto_update != 'n':
            with open(cfg_path, "r", encoding="utf-8") as f:
                content = f.read()

            new_content = re.sub(
                r'ENCRYPTED_SMTP_PAYLOAD\s*=\s*os\.getenv\(.*?\)',
                f'ENCRYPTED_SMTP_PAYLOAD = os.getenv("RESUMEIQ_ENCRYPTED_SMTP", "{token}")',
                content
            )
            with open(cfg_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            print("   ✅ Updated config/smtp_config.py with encrypted payload!")
            print("   Your app is now ready with scrape-proof embedded credentials.")
        else:
            print(f"   You can manually set in config/smtp_config.py:")
            print(f'   ENCRYPTED_SMTP_PAYLOAD = os.getenv("RESUMEIQ_ENCRYPTED_SMTP", "{token}")')

    print("=" * 65)

if __name__ == "__main__":
    main()
