# ResumeIQ — AI Resume Analyzer & ATS Optimization Desktop Suite

![Python](https://img.shields.io/badge/Python-3.12%2B-blue)
![PyQt6](https://img.shields.io/badge/GUI-PyQt6-indigo)
![NLP](https://img.shields.io/badge/NLP-spaCy-green)
![SQLite](https://img.shields.io/badge/Database-SQLite3-lightgrey)

**ResumeIQ** is an AI-powered desktop application built with PyQt6, spaCy, pdfplumber, python-docx, ReportLab, and Matplotlib. It parses resumes (PDF & DOCX), performs NLP entity and skill extraction, calculates 4-Pillar ATS compatibility scores against custom Job Descriptions, predicts matching job roles aligning to candidate skills, visualizes analytics, and generates PDF evaluation reports.

---

## 🌟 Key Features

1. **User Authentication & Security**:
   - Salted SHA-256 password hashing.
   - User account registration and authentication.
2. **Resume Parsing & Extraction**:
   - Multi-format text extraction (PDF & DOCX).
   - spaCy entity recognition for Candidate Name, Email, and Phone Number.
   - Taxonomy-driven skill extraction across **22 tech and non-tech role categories** (350+ skills) including **IT Support & Desktop Engineering**, **Software Engineering**, **Data Science & AI**, **Cloud & DevOps**, **Digital Marketing**, **Product Management**, **Finance**, **HR**, **Sales**, and **Operations**.
3. **4-Pillar ATS Compatibility Engine**:
   - Industry-grade 4-Pillar scoring formula: `(40% Skill Match) + (25% TF-IDF Similarity) + (20% Hygiene & Structure) + (15% Experience Alignment)`.
   - Granular 5-star rating system (0.0 to 5.0 Stars) supporting full, fractional (¾, ½, ¼), and empty star representations.
   - Score categorization: *Needs Improvement* (<50%), *Average* (50-75%), *Excellent* (>75%).
   - Actionable AI improvement suggestions tailored for fresher and experienced candidates.
4. **Target Job Role Prediction**:
   - Predicts top matching job roles based on skills extracted from the candidate's resume (e.g. *Desktop Support Engineer*, *Full Stack Developer*, *Data Scientist*, *IT Support Engineer*, *Product Manager*).
   - Shows percentage alignment and key matching skills for each recommended role.
5. **Interactive Dashboard & Analytics**:
   - Real-time Matplotlib charts embedded in PyQt6 canvas (Pie charts, Bar graphs).
   - Overview KPI summary metrics and score category breakdown.
6. **PDF Evaluation Report Export**:
   - ReportLab PDF generator compiling candidate score, star rating, matched/missing skills, predicted matching job roles table, and actionable recommendations.
7. **SQLite Storage & History**:
   - Persistent storage for resumes, extracted text, ATS scores, skills breakdown, and generated reports.

---

## 📁 Directory Structure

```text
ResumeIQ/
├── assets/
│   ├── skills.json          # Pre-populated 22-category tech & non-tech skills taxonomy
│   └── check.svg            # UI checkbox vector asset
├── database/
│   ├── database.py          # SQLite connection manager & CRUD operations
│   └── resumeiq.db          # Auto-generated SQLite database
├── models/
│   ├── user.py              # User data DTO
│   └── resume.py            # Resume analysis result DTO
├── modules/
│   ├── auth.py              # Authentication business logic
│   ├── parser.py            # PDF & DOCX text extraction
│   ├── nlp_engine.py        # spaCy extraction engine & skill matching
│   ├── ats_calculator.py    # 4-Pillar ATS scoring, skill normalization & role predictor
│   ├── benchmarks.py        # Tech & non-tech industry ATS benchmarks
│   ├── cover_letter_generator.py # Automated cover letter generator
│   ├── linkedin_optimizer.py    # LinkedIn profile review & scoring
│   ├── local_ai_agent.py        # Local AI resume rewrite & bullet optimizer
│   ├── mnc_ats_engine.py        # Multi-MNC ATS system simulator
│   ├── report_generator.py      # ReportLab PDF report generator with matching job roles
│   └── scheduler.py             # Periodic background rescan scheduler
├── reports/                 # Output folder for generated PDF reports
├── resumes/                 # Storage folder for uploaded resume files
├── ui/
│   ├── styles.py            # Design tokens & QSS dark theme stylesheet
│   ├── login_window.py      # PyQt6 Login & Register UI
│   ├── dashboard_window.py  # Main Dashboard window & navigation views
│   ├── closing_screen.py    # Shutdown splash screen
│   ├── floating_widget.py   # Desktop quick-access widget
│   └── splash_screen.py     # Startup glassmorphism splash screen
├── utils/
│   ├── security.py          # Password hashing & email validation
│   ├── logger.py            # Logging utility
│   └── paths.py             # Cross-platform data path helper
├── main.py                  # Application entry point
├── build_installer.py       # Inno Setup & PyInstaller compiler script
├── setup_installer.py       # Dependency setup & health check assistant
├── Install-ResumeIQ.ps1     # Automated PowerShell installer script
├── requirements.txt         # Dependencies manifest
└── README.md                # Documentation
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+ (Recommended: Python 3.12 64-bit)
- Virtual environment (`venv`)

### Installation

1. Activate virtual environment (Windows):
   ```bash
   venv\Scripts\activate
   ```

2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Download spaCy English language model:
   ```bash
   python -m spacy download en_core_web_sm
   ```

4. Launch the Application:
   ```bash
   python main.py
   ```

---

## 📦 Windows Installers & Automated Setup

ResumeIQ includes automated setup and installer creation tools:

### Option 1: Standalone Windows GUI Installer (`ResumeIQ_Setup.exe`)
Build a standard Windows installer wizard with desktop shortcuts and automatic Visual C++ Redistributable check & download:

```bash
python build_installer.py
```

- Compiles standalone `dist/ResumeIQ.exe` bundling PyQt6, spaCy NLP model (`en_core_web_sm`), pdfplumber, and ReportLab.
- Uses `installer_setup.iss` to package into a single setup wizard (`Output/ResumeIQ_Setup_v1.0.0.exe`).
- Automatically detects missing system prerequisites on the client PC and downloads `vc_redist.x64.exe` from Microsoft's official servers.

### Option 2: Automated PowerShell Bootstrapper (`Install-ResumeIQ.ps1`)
Automated setup script for machines where Python runtime is managed on host:

```powershell
# Run in PowerShell as Administrator or User:
.\Install-ResumeIQ.ps1
```

- **Python Check**: Automatically checks if Python 3.10+ is installed; downloads and installs Python 3.12 64-bit silently if missing.
- **Dependency Download**: Creates virtual environment `.venv`, downloads required packages from `requirements.txt`, and downloads spaCy's `en_core_web_sm` model.
- **Shortcuts**: Automatically generates Windows Desktop and Start Menu shortcuts.

### Option 3: Python Setup & Health Check Assistant (`setup_installer.py`)

```bash
python setup_installer.py
```

- Scans installed packages, downloads missing dependencies, loads spaCy model, and creates working directories (`assets/`, `database/`, `reports/`, `resumes/`).

---

## 📝 License
Built as an MCA Minor Project / Portfolio Confidential Application.
