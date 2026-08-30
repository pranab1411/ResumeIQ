# ResumeIQ Changelog & Release Notes

## 🌟 [2.1.0] - August 28, 2026 (Official Production Release)

### 🤖 1. 100% Dynamic Google Gemini AI Decision Architecture
- **Zero Hardcoded Industry Branches:** Eliminated static industry `if/elif` branches. Google Gemini AI dynamically predicts candidate target roles, matched/missing skills, recommended additions, and field-specific required asset fixes (CompTIA/CCNA for IT, GitHub for Software, Behance for Design, Medical License for Healthcare, PE License for Civil, Bar Admission for Law).
- **Gemini Model Standards & 429 Quota Fallback:** Configured default models (`gemini-2.5-flash`, `gemini-2.0-flash`, `gemini-flash-latest`) with automatic fallthrough on HTTP 429 rate limit / quota exhaustion.
- **JSON Truncation Protection:** Enforced `responseMimeType: "application/json"`, increased token buffer to 4,096 tokens, and implemented intelligent JSON boundary repair for unclosed responses.
- **Dynamic AI Header Status Badge:** Real-time visual indicator in Dashboard Header displaying `✨ Google Gemini AI Active` (emerald green) when API key is active vs `🤖 Free Local spaCy AI Active` (purple) when using local offline engine.

### 🖼️ 2. Brand New ResumeIQ Logo & Visual Refresh
- **New Brand Assets:** Converted and integrated high-resolution ResumeIQ logo across all UI windows, taskbar icons, system tray floating widget, executable icons, installer setup wizard, and GitHub repository `README.md`.
- **PDF Report Header Image & Engine Badge:** Embedded high-resolution ResumeIQ logo and dynamic engine indicator (`Google Gemini AI Powered Evaluation` vs `Local spaCy AI Evaluation`) directly into single-page executive PDF evaluation report headers.
- **Report Symbol & Status Legend Card:** Added a dedicated status legend card (`⭐ Exceeded`, `✓ Met`, `⚠ Partially Met`, `✕ Action Required`) in the executive PDF report right stack to optimize whitespace utilization.

### 🔍 3. Mandatory Pre-Build Codebase Verification System
- **Automated Sanity Check:** Integrated 65-file AST syntax check and 23-module import verification system into `build_installer.py` and `build_test.py` to prevent broken builds.

### 👤 4. Candidate Profile Parsing & Seniority Improvements
- **Split-Line Full Name Combination:** Automatically combines candidate name headers split across lines (e.g. `PRANAB` \n `CHOURASIYA` -> `Pranab Chourasiya`).
- **Apostrophe & Non-Standard Experience Detection:** Accurately extracts apostrophe dates (`June'2025`, `Jan'2023`) and multi-year statements (`having 11 years of experience...`).

---

## 🌟 [2.0.0] - August 27, 2026

### 1. Dedicated "About Developer & Engine Architecture" Page
- **Navigation Integration:** Added **`👨‍💻 About Developer`** to the main sidebar navigation.
- **Developer Profile Card:** Features developer details (**Pranab Chourasiya**) with interactive action buttons:
  - 💼 **LinkedIn Profile:** `https://www.linkedin.com/in/pranab-chourasiya-87409735b/`
  - 🐙 **GitHub Profile:** `https://github.com/pranab1411`
  - ⭐ **ResumeIQ Repository:** `https://github.com/pranab1411/ResumeIQ`
  - ✉️ **Contact Developer Email:** `pranabchourasiya876@gmail.com`
- **Architecture & Tech Stack Matrix:** Highlights 100% On-Device Local Processing, spaCy NLP, ReportLab 5, SQLite WAL, PyQt6, PyInstaller, and Inno Setup 6.

### 2. State-Machine Email OTP Password Reset Engine
- **Cryptographic 6-Digit Generator:** Uses `secrets.randbelow()` for secure 6-digit numeric OTP creation.
- **SHA-256 Hashed Storage:** Stored as salted SHA-256 hashes; raw OTPs are never saved in plaintext or logged.
- **5-Attempt Locking Limit:** Strictly locks OTP after 5 failed attempts (`"Invalid verification code. You have X attempts remaining."` / `"Maximum OTP attempts exceeded. Please request a new OTP."`).
- **60-Second Cooldown Timer:** Enforces a 60-second minimum cooldown between resend requests with a live UI countdown (`"Resend OTP in 59s"`).
- **5-Minute TTL & Token Authorization:** Issues a short-lived 10-minute server-side `reset_token` upon successful verification; password updates cannot be bypassed via client-side flags.
- **Masked Email Modal:** Displays masked email address (`p***876@gmail.com`) in confirmation dialogs.

### 3. Password Changed Confirmation Email
- **Automated Dispatch:** Automatically dispatches a confirmation email from **`support.resumeiq@gmail.com`** via TLS SMTP immediately after password update succeeds in the database.
- **Security Notice:** Subject: `"ResumeIQ Password Changed Successfully"`. Includes new password details and security escalation warning.

### 4. Vector 5-Star Rating Cards & Section Analysis
- **Executive PDF Star Ratings:** Added vector half-star drawing helpers supporting fractional ratings (e.g. `4.2 / 5.0`).
- **Overall Resume Rating Card:** Added dedicated star rating card in executive PDF report right stack.
- **"About Me" Summary Recognition:** Header parser now recognizes `"About Me"`, `"Profile"`, `"Personal Profile"`, `"Executive Summary"`, and `"Career Objective"` as valid summary sections.

### 5. Proprietary Freeware License
- Added official **[LICENSE](file:///d:/py%20project/ResumeIQ/LICENSE)** granting free-of-charge personal use while strictly prohibiting code modification, reverse engineering, decompilation, and resale.

---

## 🛠️ Bug Fixes & Refinements

1. **Dashboard RichText Fix:** Resolved raw HTML `<b>` text rendering in dark dashboard Health Audit matrix labels by enabling `Qt.TextFormat.RichText`.
2. **Target Role Analysis Spacing:** Fixed vertical text collisions between `TARGET ROLE ANALYSIS` header and the role subtitle with dedicated typography styles and padding (`2.5pt`).
3. **Section Analysis Table Overlap:** Restored clean 3-column layout (`Section` | `Status` | `Recommendation`) with explicit ReportLab column width constraints.
4. **Out-of-the-Box SMTP Credentials:** Embedded `support.resumeiq@gmail.com` App Password in `config/smtp_config.py` and added auto-seeding in SQLite `database.py` `init_db()`.

---

## 🗑️ Feature Removals & Deprecations

1. **Raw Plaintext OTP Storage:** Removed legacy memory dictionary storing raw OTP strings.
2. **Unauthenticated Reset Endpoints:** Deprecated parameterless password reset calls in `AuthManager.reset_password()`.
3. **Permissive Open-Source Licensing:** Replaced generic MIT license with a custom Proprietary Freeware License.

---

## 🧪 Automated Testing Verification

All 43 unit tests across parsers, report generation, NLP engines, database CRUD, and the upgraded OTP security engine pass cleanly:

```powershell
$env:PYTHONPATH="."; python -m unittest discover -s tests -p "test_*.py"
# Output: Ran 43 tests in 42.9s (OK)
```
