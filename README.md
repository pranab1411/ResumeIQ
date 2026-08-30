<p align="center">
  <img src="assets/logo.png" alt="ResumeIQ Logo" width="200"/>
</p>

<h1 align="center">ResumeIQ — AI Resume Analyzer & ATS Optimization Desktop Suite</h1>

<p align="center">
  <a href="https://github.com/pranab1411/ResumeIQ/releases/latest">
    <img src="https://img.shields.io/badge/Release-v2.1.0-emerald?style=flat-square&logo=github" alt="Latest Release"/>
  </a>
  <img src="https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-blue?style=flat-square&logo=python" alt="Python"/>
  <img src="https://img.shields.io/badge/GUI-PyQt6-indigo?style=flat-square&logo=qt" alt="PyQt6"/>
  <img src="https://img.shields.io/badge/AI-Google%20Gemini-emerald?style=flat-square&logo=google" alt="Google Gemini"/>
  <img src="https://img.shields.io/badge/NLP-spaCy-green?style=flat-square&logo=spacy" alt="spaCy"/>
  <img src="https://img.shields.io/badge/PDF-ReportLab%205-purple?style=flat-square" alt="ReportLab"/>
  <img src="https://img.shields.io/badge/Database-SQLite3%20WAL-lightgrey?style=flat-square&logo=sqlite" alt="SQLite"/>
  <a href="LICENSE">
    <img src="https://img.shields.io/badge/License-Proprietary%20Freeware-orange?style=flat-square" alt="License"/>
  </a>
</p>

<p align="center">
  <a href="https://github.com/pranab1411/ResumeIQ/releases/latest">
    <img src="https://img.shields.io/badge/Download-Windows%20Setup%20Installer%20v2.1.0-blue?style=for-the-badge&logo=windows&logoColor=white" alt="Download ResumeIQ Windows Installer"/>
  </a>
</p>

---

**ResumeIQ** is an advanced AI-powered desktop suite engineered with **Python 3.11**, **PyQt6**, **Google Gemini AI**, **spaCy NLP**, and **ReportLab 5**. It delivers enterprise-grade resume intelligence, multi-criteria ATS compatibility evaluation, dynamic target job role prediction, and vector executive PDF reports — with **100% on-device local privacy** and optional **cloud AI acceleration**.

---

## 👨‍💻 Developer Information

* **Developer:** **Pranab Chourasiya**
* **LinkedIn Profile:** [linkedin.com/in/pranab-chourasiya-87409735b](https://www.linkedin.com/in/pranab-chourasiya-87409735b/)
* **GitHub Profile:** [github.com/pranab1411](https://github.com/pranab1411)
* **GitHub Repository:** [github.com/pranab1411/ResumeIQ](https://github.com/pranab1411/ResumeIQ)
* **Contact Email:** [pranabchourasiya876@gmail.com](mailto:pranabchourasiya876@gmail.com)

---

## 🌟 Key Features

### 1. Hybrid Cloud & On-Device AI Architecture
- **Dual-Engine Processing:** Operates 100% offline using high-performance local spaCy NLP, with seamless cloud acceleration via Google Gemini AI (`gemini-2.5-flash`, `gemini-2.0-flash`, `gemini-flash-latest`).
- **Resilient 429 Quota Fallback:** Automatically falls through to standby Gemini models when encountering rate limits or quota boundaries.
- **Dynamic Header Status Badge:** Real-time visual status indicator in the Dashboard displaying `✨ Google Gemini AI Active` (emerald green) or `🤖 Free Local spaCy AI Active` (purple).

### 2. Universal Dynamic Role Prediction & Decision Engine
- **Zero Hardcoded Branches:** Predicts candidate target roles, matched/missing skills, recommended additions, and field-specific required credentials dynamically across all global industries (Software, IT, Healthcare, Finance, Law, Civil, Design, HR, Sales).
- **Infinite Name Recognition Engine:** Identifies names across global naming conventions while filtering out job titles, certifications, and header terms.

### 3. 4-Pillar MCDA Scoring & 5-Star Rating System
- **Multi-Criteria Decision Analysis:** Industry-standard weighted ATS formula:
  $$\text{ATS Score} = (0.40 \times \text{Skills}) + (0.25 \times \text{TF-IDF Cosine}) + (0.20 \times \text{Hygiene/Format}) + (0.15 \times \text{Experience})$$
- **Vector 5-Star Ratings:** Fractional vector half-star rendering (0.0 to 5.0 Stars) for granular quality assessment.
- **Enterprise ATS Benchmarks:** Heuristic simulation models for Workday, Oracle Taleo, Greenhouse, Lever, and iCIMS.

### 4. Executive Single-Page Vector PDF Evaluation Reports
- **Executive Header:** Embedded high-resolution ResumeIQ branding and dynamic engine badge (`Google Gemini AI Powered` vs `Local spaCy AI Evaluation`).
- **Report Symbol & Status Legend Card:** Dedicated status indicators (`⭐ Exceeded`, `✓ Met`, `⚠ Partially Met`, `✕ Action Required`) optimizing whitespace.
- **Comprehensive Scorecards:** 4-pillar scores, keyword matrices, section audits, and actionable recruiter recommendations.

### 5. Multi-Format Resume Parsing
- Supports PDF, DOCX, TXT, RTF, ODT, and HTML with OCR image fallback.
- Header detection for *"About Me"*, *"Profile"*, *"Personal Profile"*, *"Executive Summary"*, and *"Career Objective"*.

### 6. State-Machine Email OTP Password Reset Security
- **Cryptographic 6-Digit Generator:** Secure numeric OTP creation via `secrets.randbelow()`.
- **SHA-256 Hashed Storage:** Salted storage; raw OTPs are never saved in plaintext.
- **Brute-Force Guard:** Strict 5-attempt locking limit and 60-second cooldown timer.
- **Automated Dispatch:** Confirmation notification dispatched from `support.resumeiq@gmail.com` via TLS SMTP upon successful reset.

### 7. Dedicated "About Developer & Engine Architecture" Page
- Integrated dark glassmorphic view with interactive developer links, architecture breakdown, and full tech stack matrix.

### 8. Pre-Build Codebase Verification System
- Automated 65-file AST syntax parser and 23-module import validation integrated directly into build pipelines to prevent regressions.

---

## 🔑 How to Get a Free Google Gemini API Key

ResumeIQ works 100% offline out-of-the-box. To enable Google Gemini AI features:

1. **Visit Google AI Studio:** Open [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey).
2. **Sign In:** Log in with any Google account.
3. **Create API Key:** Click **"Create API Key"** and copy your key (starts with `AIzaSy...`).
4. **Configure in ResumeIQ:** Navigate to ⚙️ **Settings** -> **Google Gemini AI Configuration**, paste the key, click **Save Key**, and test the connection.

---

## 📁 Directory Structure

```text
ResumeIQ/
├── assets/                  # Domain skills taxonomy, names database & UI assets
│   ├── skills.json          # 22-category skills taxonomy
│   ├── names_db.json        # Global first & last names database
│   ├── app_icon.ico         # Executable & window icon
│   └── logo.png             # ResumeIQ high-resolution logo
├── config/
│   ├── version.py           # Application version & build type configuration
│   ├── ats_config.json      # Configurable ATS weights, thresholds & benchmarks
│   └── smtp_config.py       # SMTP credentials & TLS email configuration
├── database/
│   ├── database.py          # SQLite connection manager with WAL mode & CRUD
│   └── resumeiq.db          # Local SQLite database
├── modules/
│   ├── ats_calculator.py    # 4-Pillar MCDA scoring, skill normalization & role predictor
│   ├── ats_benchmark.py     # RQI, Content Strength & industry benchmark engine
│   ├── mnc_ats_engine.py    # Simulated enterprise ATS compatibility engine
│   ├── nlp_engine.py        # spaCy extraction engine & skill matcher
│   ├── parser.py            # Unified multi-format document parser
│   ├── report_generator.py  # ReportLab executive PDF report generator
│   └── otp_service.py       # State-machine email OTP generator & validator
├── tests/                   # Automated unit test suite (54 tests)
│   ├── test_ats_calculator.py
│   ├── test_database.py
│   ├── test_nlp_engine.py
│   ├── test_parsers.py
│   └── test_report_generator.py
├── ui/                      # PyQt6 GUI components & dark theme stylesheets
│   ├── about_developer_page.py # About Developer & Engine Architecture view
│   ├── dashboard_window.py  # Main Dashboard window & navigation stack
│   ├── login_window.py      # Login & Registration UI
│   ├── profile_page.py      # Candidate Profile & Target Role settings
│   ├── glass_message_box.py # Custom glassmorphic notifications
│   ├── onboarding_tour.py   # Interactive onboarding tour wizard
│   ├── floating_widget.py   # Desktop floating glass view
│   ├── closing_screen.py    # Animated shutdown splash screen
│   └── styles.py            # Dark theme QSS design tokens
├── utils/                   # Security, logging & path helpers
│   ├── gemini_client.py     # Gemini REST client with automatic fallback
│   ├── logger.py            # Central logging utility
│   └── security.py          # Password hashing & validation
├── main.py                  # Application entry point
├── build_test.py            # Automated Inno Setup test build compiler
├── build_installer.py       # Inno Setup official production build compiler
├── installer_setup.iss      # Inno Setup installer script
├── requirements.txt         # Dependencies manifest
├── CHANGELOG.md             # Version history & release notes
└── README.md                # Documentation
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+ (Recommended: Python 3.11 / 3.12 64-bit)
- Windows 10 or Windows 11 (64-bit)

### Installation & Local Run

1. Clone repository:
   ```bash
   git clone https://github.com/pranab1411/ResumeIQ.git
   cd ResumeIQ
   ```

2. Create and activate virtual environment:
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Download spaCy English model:
   ```bash
   python -m spacy download en_core_web_sm
   ```

5. Launch Application:
   ```bash
   python main.py
   ```

---

## 🧪 Running Automated Test Suite

ResumeIQ maintains a comprehensive test suite covering parsers, scoring formulas, NLP entities, database CRUD, and OTP state transitions:

```powershell
$env:PYTHONPATH="."; python -m unittest discover -s tests -p "test_*.py"
# Output: Ran 54 tests (OK)
```

---

## 📦 Building Production & Test Installers

* **Compile Official Production Setup:**
  ```powershell
  python build_installer.py
  ```
  *Generates `Output/ResumeIQ_Setup_v2.1.exe`.*

* **Compile Auto-Incremented Test Build:**
  ```powershell
  python build_test.py
  ```
  *Generates `test_builds/ResumeIQ v2.1 test build <N>.exe`.*

---

## 📝 License & Restrictions
Designed & Engineered by **Pranab Chourasiya**. Copyright (c) 2026. All Rights Reserved.

ResumeIQ is provided as **Free-of-Charge Software** under a **Proprietary Freeware License**:
* 🆓 **Free to Use:** Free for personal and evaluation use.
* 🚫 **No Resale:** Selling, reselling, sublicensing, or charging fees for this software is strictly prohibited.
* 🔒 **No Modification:** Modifying, decompiling, reverse engineering, or creating derivative works of this software is strictly prohibited.

See the full **[LICENSE](LICENSE)** file for complete terms.
