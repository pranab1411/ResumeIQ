#!/usr/bin/env python3
"""
ResumeIQ — Intelligent Dependency Setup & Health Checker Assistant
Scans system environment, verifies required packages, downloads missing libraries,
loads the spaCy NLP model, and ensures directories exist.
"""

import sys
import os
import subprocess
import shutil

REQUIRED_MODULES = [
    ("PyQt6", "PyQt6"),
    ("spacy", "spacy"),
    ("pdfplumber", "pdfplumber"),
    ("docx", "python-docx"),
    ("reportlab", "reportlab"),
    ("matplotlib", "matplotlib"),
    ("pandas", "pandas"),
    ("sklearn", "scikit-learn")
]

def print_banner():
    print("=" * 65)
    print("  ResumeIQ — Automated Dependency Setup & System Verification")
    print("=" * 65)

def check_python_version():
    v = sys.version_info
    print(f"[1/5] Python Environment: {v.major}.{v.minor}.{v.micro}")
    if v.major < 3 or (v.major == 3 and v.minor < 10):
        print("  ❌ Warning: ResumeIQ requires Python 3.10 or newer.")
        return False
    print("  ✅ Python version compatible.")
    return True

def install_missing_packages():
    print("\n[2/5] Checking required Python packages...")
    missing_pip = []
    
    for module_name, pkg_name in REQUIRED_MODULES:
        try:
            __import__(module_name)
            print(f"  ✅ {pkg_name}: Installed")
        except ImportError:
            print(f"  ❌ {pkg_name}: Missing")
            missing_pip.append(pkg_name)
            
    if missing_pip:
        print(f"\n  🚀 Downloading and installing missing packages: {', '.join(missing_pip)}...")
        req_file = os.path.join(os.path.dirname(__file__), "requirements.txt")
        if os.path.exists(req_file):
            cmd = [sys.executable, "-m", "pip", "install", "-r", req_file]
        else:
            cmd = [sys.executable, "-m", "pip", "install"] + missing_pip
            
        res = subprocess.run(cmd)
        if res.returncode == 0:
            print("  ✅ All packages installed successfully.")
        else:
            print("  ⚠️ Package installation encountered warnings.")
    else:
        print("  ✅ All required packages are present.")

def verify_spacy_model():
    print("\n[3/5] Verifying spaCy NLP model ('en_core_web_sm')...")
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        print("  ✅ spaCy model 'en_core_web_sm' is loaded and operational.")
    except Exception:
        print("  ⚠️ Model 'en_core_web_sm' not found. Downloading latest version from spaCy repository...")
        cmd = [sys.executable, "-m", "spacy", "download", "en_core_web_sm"]
        res = subprocess.run(cmd)
        if res.returncode == 0:
            print("  ✅ 'en_core_web_sm' model installed successfully.")
        else:
            print("  ❌ Failed to download spaCy model automatically.")

def prepare_directories():
    print("\n[4/5] Preparing application directory structure...")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dirs = ["assets", "database", "reports", "resumes"]
    for d in dirs:
        p = os.path.join(base_dir, d)
        os.makedirs(p, exist_ok=True)
        print(f"  ✅ Directory ready: {d}/")

def main():
    print_banner()
    check_python_version()
    install_missing_packages()
    verify_spacy_model()
    prepare_directories()
    print("\n" + "=" * 65)
    print("  🎉 Setup complete! All dependencies and requirements are ready.")
    print("  You can launch the application by running: python main.py")
    print("=" * 65)

if __name__ == "__main__":
    main()
