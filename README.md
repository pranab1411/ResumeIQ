# ResumeIQ — AI Resume Analyzer & ATS Optimization Desktop Suite

![Python](https://img.shields.io/badge/Python-3.12%2B-blue)
![PyQt6](https://img.shields.io/badge/GUI-PyQt6-indigo)
![NLP](https://img.shields.io/badge/NLP-spaCy-green)
![SQLite](https://img.shields.io/badge/Database-SQLite3-lightgrey)

**ResumeIQ** is an offline-capable, NLP-powered desktop application built with Python 3.12, PyQt6, spaCy, pdfplumber, python-docx, and ReportLab. It parses resumes across multiple formats (PDF, DOCX, TXT, RTF, ODT, HTML), performs entity and domain skill extraction, computes a transparent 4-Pillar Multi-Criteria Decision Analysis (MCDA) ATS compatibility score against custom Job Descriptions, predicts aligned job roles, provides career optimization suggestions, and generates executive PDF evaluation reports.

---

## 🌟 Key Features

1. **User Authentication & Cryptographic Security**:
   - Per-user salted Argon2 / PBKDF2-SHA256 password hashing.
   - Secure account registration, authentication, and SQLite persistence.
2. **Multi-Format Resume Parsing**:
   - Multi-format text extraction (PDF, DOCX, TXT, RTF, ODT, HTML) with OCR image fallback.
   - spaCy Named Entity Recognition (NER) for Candidate Name, Email, and Phone Number.
   - Curated domain taxonomy skill extraction across **22 tech and non-tech role categories** (350+ skills).
3. **4-Pillar MCDA Scoring Engine**:
   - Multi-Criteria Decision Analysis scoring model:
     $$\text{ATS Score} = (0.40 \times \text{Skills}) + (0.25 \times \text{TF-IDF Cosine}) + (0.20 \times \text{Hygiene/Format}) + (0.15 \times \text{Experience})$$
   - Granular 5-star rating system (0.0 to 5.0 Stars) supporting fractional representations.
   - Score categorization: *Needs Improvement* (<50%), *Average* (50–75%), *Excellent* (>75%).
4. **Target Job Role Prediction**:
   - Predicts top matching job roles based on skills extracted from the candidate's resume (e.g. *Full Stack Developer*, *Data Scientist*, *Desktop Support Engineer*, *DevOps Engineer*).
5. **Simulated Enterprise ATS Profiles**:
   - Heuristic multi-criteria profiling simulating ATS evaluation priorities (Workday, Oracle Taleo, Greenhouse, Lever, iCIMS).
6. **Executive PDF Evaluation Report Export**:
   - Generates an executive ReportLab PDF report containing candidate metrics, traceable MCDA contribution table, extracted evidence (verbs, % metrics), skill gap matrix, and actionable recommendations.

---

## 📁 Directory Structure

```text
ResumeIQ/
├── assets/                  # Domain skills taxonomy & UI vector assets
│   ├── skills.json          # 22-category tech & non-tech skills taxonomy
│   └── names_db.json        # Global first & last names database
├── config/
│   ├── ats_config.json      # Configurable ATS weights, thresholds & benchmarks
│   └── smtp_config.py       # Environment-based SMTP configuration
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
│   └── scheduler.py         # Periodic background rescan scheduler
├── tests/                   # Automated unit test suite
│   ├── test_ats_calculator.py
│   ├── test_database.py
│   ├── test_nlp_engine.py
│   ├── test_parsers.py
│   └── test_report_generator.py
├── ui/                      # PyQt6 GUI components & dark theme stylesheets
│   ├── dashboard_window.py  # Main Dashboard window
│   ├── login_window.py      # Login & Registration UI
│   └── styles.py            # Dark theme QSS design tokens
├── utils/                   # Security, logging & path helpers
│   ├── gemini_client.py     # Gemini REST client
│   └── security.py          # Password hashing & email validation
├── main.py                  # Application entry point
├── build_installer.py       # Inno Setup & PyInstaller compiler script
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

## 🧪 Running Automated Tests

Run the full automated test suite:

```bash
python -m unittest discover -s tests -p "test_*.py"
```

---

## 📦 Windows Installers & Automated Setup

Build a standard Windows installer wizard (`test_builds/ResumeIQ v2.0.0 test build <N>.exe`):

```bash
python build_test.py
```

---

## 📝 License
Built as an MCA Minor Project / Academic Portfolio Application.
