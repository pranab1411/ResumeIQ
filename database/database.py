import sqlite3
import os
import re
import random
from typing import Optional, List, Dict, Any
from utils.security import hash_password, verify_password
from utils.logger import logger
from utils.paths import get_data_path

DB_PATH = get_data_path("database", "resumeiq.db")

class DatabaseManager:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            conn.execute("PRAGMA journal_mode=WAL")
        except Exception:
            pass
        return conn

    def init_db(self):
        """Creates tables if they don't exist and runs migrations."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    username TEXT UNIQUE,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Migration check for username column
            try:
                cursor.execute("ALTER TABLE users ADD COLUMN username TEXT")
            except sqlite3.OperationalError:
                pass

            # Auto-assign usernames for pre-existing records without a username
            cursor.execute("SELECT id, name FROM users WHERE username IS NULL OR username = ''")
            for user_row in cursor.fetchall():
                clean_name = re.sub(r'[^a-zA-Z0-9]', '', user_row["name"].split()[0]).lower() if user_row["name"] else "user"
                rand_num = random.randint(1000, 9999)
                new_uname = f"riq_{clean_name}_{rand_num}"
                cursor.execute("UPDATE users SET username = ? WHERE id = ?", (new_uname, user_row["id"]))
            conn.commit()
            
            # Resumes table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS resumes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    filename TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ats_score REAL DEFAULT 0.0,
                    job_title TEXT DEFAULT '',
                    job_description TEXT DEFAULT '',
                    extracted_text TEXT DEFAULT '',
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            """)
            
            # Skills table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS skills (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    resume_id INTEGER NOT NULL,
                    skill TEXT NOT NULL,
                    category TEXT DEFAULT 'General',
                    is_matched INTEGER DEFAULT 1,
                    FOREIGN KEY (resume_id) REFERENCES resumes (id) ON DELETE CASCADE
                )
            """)
            
            # Reports table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    resume_id INTEGER NOT NULL,
                    pdf_name TEXT NOT NULL,
                    pdf_path TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (resume_id) REFERENCES resumes (id) ON DELETE CASCADE
                )
            """)

            # Settings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS app_settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            """)

            # ATS Score History table (Phase 1)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ats_score_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    resume_id INTEGER NOT NULL,
                    score REAL NOT NULL,
                    rqi REAL DEFAULT 0.0,
                    confidence_score REAL DEFAULT 0.0,
                    readiness_score REAL DEFAULT 0.0,
                    industry TEXT DEFAULT 'General',
                    company TEXT DEFAULT '',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (resume_id) REFERENCES resumes (id) ON DELETE CASCADE
                )
            """)

            # Resume Versions table (Phase 1)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS resume_versions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    resume_id INTEGER NOT NULL,
                    version_number INTEGER NOT NULL,
                    version_name TEXT DEFAULT '',
                    extracted_text TEXT DEFAULT '',
                    ats_score REAL DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (resume_id) REFERENCES resumes (id) ON DELETE CASCADE
                )
            """)

            # AI Suggestions table (Phase 15)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ai_suggestions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    resume_id INTEGER NOT NULL,
                    suggestion_type TEXT NOT NULL,
                    original_text TEXT,
                    suggested_text TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (resume_id) REFERENCES resumes (id) ON DELETE CASCADE
                )
            """)

            # Cover Letters table (Phase 15)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cover_letters (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    job_title TEXT,
                    company_name TEXT,
                    letter_text TEXT NOT NULL,
                    file_path TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            """)

            # LinkedIn Reviews table (Phase 15)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS linkedin_reviews (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    headline TEXT,
                    about TEXT,
                    composite_score REAL DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            """)

            # Job Descriptions table (Phase 15)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS job_descriptions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    job_title TEXT,
                    company_name TEXT,
                    jd_text TEXT NOT NULL,
                    industry TEXT DEFAULT 'General',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            """)

            # Audit Log table (Phase 15)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    action TEXT NOT NULL,
                    details TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()
            logger.info("Database initialized successfully with WAL mode & Phase 15 schema.")

    # --- App Settings ---
    def set_setting(self, key: str, value: str):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO app_settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
                (key, value)
            )
            conn.commit()

    def get_setting(self, key: str, default: str = "") -> str:
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT value FROM app_settings WHERE key = ?", (key,))
                row = cursor.fetchone()
                return row["value"] if row else default
        except Exception:
            return default

    def reset_user_database_data(self, user_id: Optional[int] = None):
        """
        Deletes all stored resumes, extracted skills, generated reports, and app settings
        from the database while strictly PRESERVING user login credentials (users table).
        Resets auto-increment counters so fresh uploads start cleanly at ID 1.
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                if user_id is not None:
                    cursor.execute("DELETE FROM reports WHERE resume_id IN (SELECT id FROM resumes WHERE user_id = ?)", (user_id,))
                    cursor.execute("DELETE FROM skills WHERE resume_id IN (SELECT id FROM resumes WHERE user_id = ?)", (user_id,))
                    cursor.execute("DELETE FROM resumes WHERE user_id = ?", (user_id,))
                    cursor.execute("DELETE FROM ats_score_history WHERE resume_id IN (SELECT id FROM resumes WHERE user_id = ?)", (user_id,))
                    cursor.execute("DELETE FROM resume_versions WHERE resume_id IN (SELECT id FROM resumes WHERE user_id = ?)", (user_id,))
                else:
                    cursor.execute("DELETE FROM reports")
                    cursor.execute("DELETE FROM skills")
                    cursor.execute("DELETE FROM resumes")
                    cursor.execute("DELETE FROM ats_score_history")
                    cursor.execute("DELETE FROM resume_versions")
                
                cursor.execute("DELETE FROM app_settings")
                
                # Reset auto-increment sequence if resumes table is empty
                cursor.execute("SELECT COUNT(*) FROM resumes")
                if cursor.fetchone()[0] == 0:
                    try:
                        cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('resumes', 'skills', 'reports', 'ats_score_history', 'resume_versions')")
                    except Exception:
                        pass
                
                conn.commit()
                logger.info("Database reset executed: cleared resumes, skills, reports, and sequence counters (login info preserved).")
        except Exception as e:
            logger.error(f"Error executing database reset: {e}")

    def clear_all_settings(self):
        """Resets all stored app settings to factory defaults."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM app_settings")
                conn.commit()
                logger.info("App settings reset to default factory values.")
        except Exception as e:
            logger.error(f"Error resetting app settings: {e}")

    # --- User Authentication & Username Generation ---
    def generate_unique_username(self, name: str) -> str:
        clean_first = re.sub(r'[^a-zA-Z0-9]', '', name.split()[0]).lower() if name and name.strip() else "user"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            while True:
                rand_num = random.randint(1000, 9999)
                candidate = f"riq_{clean_first}_{rand_num}"
                cursor.execute("SELECT id FROM users WHERE username = ?", (candidate,))
                if not cursor.fetchone():
                    return candidate

    def register_user(self, name: str, email: str, password: str) -> tuple[bool, str, str]:
        email = email.strip().lower()
        pwd_hash, salt = hash_password(password)
        username = self.generate_unique_username(name)
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO users (name, email, username, password_hash, salt) VALUES (?, ?, ?, ?, ?)",
                    (name.strip(), email, username, pwd_hash, salt)
                )
                conn.commit()
                logger.info(f"Registered new user {email} with auto-generated username: {username}")
                return True, "Registration successful!", username
        except sqlite3.IntegrityError:
            return False, "An account with this email address already exists.", ""
        except Exception as e:
            logger.error(f"Error registering user: {e}")
            return False, f"Registration failed: {str(e)}", ""

    def update_user_password(self, identifier: str, new_password: str) -> tuple[bool, str]:
        identifier = identifier.strip().lower()
        pwd_hash, salt = hash_password(new_password)
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, email FROM users WHERE LOWER(username) = ? OR LOWER(email) = ?", (identifier, identifier))
                user = cursor.fetchone()
                if not user:
                    return False, "No registered account found with this Username / Email."
                
                cursor.execute(
                    "UPDATE users SET password_hash = ?, salt = ? WHERE id = ?",
                    (pwd_hash, salt, user["id"])
                )
                conn.commit()
                logger.info(f"Updated password for user: {user['email']}")
                return True, "Password updated successfully!"
        except Exception as e:
            logger.error(f"Error updating password for {identifier}: {e}")
            return False, f"Password reset failed: {str(e)}"

    def authenticate_user(self, identifier: str, password: str) -> tuple[Optional[Dict[str, Any]], str]:
        identifier = identifier.strip().lower()
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE LOWER(username) = ? OR LOWER(email) = ?", (identifier, identifier))
                user_row = cursor.fetchone()
                
                if not user_row:
                    return None, "Invalid Username or Password."
                
                if verify_password(password, user_row["password_hash"], user_row["salt"]):
                    user_dict = {
                        "id": user_row["id"],
                        "name": user_row["name"],
                        "email": user_row["email"],
                        "username": user_row["username"] or user_row["email"],
                        "created_at": user_row["created_at"]
                    }
                    return user_dict, "Login successful!"
                else:
                    return None, "Invalid Username or Password."
        except Exception as e:
            logger.error(f"Error authenticating user: {e}")
            return None, f"Authentication error: {str(e)}"

    # --- Resumes ---
    def add_resume(self, user_id: int, filename: str, file_path: str, extracted_text: str = "") -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO resumes (user_id, filename, file_path, extracted_text) VALUES (?, ?, ?, ?)",
                (user_id, filename, file_path, extracted_text)
            )
            conn.commit()
            return cursor.lastrowid

    def update_resume_analysis(self, resume_id: int, ats_score: float, job_title: str, job_description: str):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE resumes SET ats_score = ?, job_title = ?, job_description = ? WHERE id = ?",
                (ats_score, job_title, job_description, resume_id)
            )
            conn.commit()

    def get_user_resumes(self, user_id: int) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM resumes WHERE user_id = ? ORDER BY id ASC",
                (user_id,)
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_resume(self, resume_id: int) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM resumes WHERE id = ?", (resume_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    # --- Skills ---
    def save_resume_skills(self, resume_id: int, matched_skills: List[str], missing_skills: List[str]):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Clear existing skills for this resume
            cursor.execute("DELETE FROM skills WHERE resume_id = ?", (resume_id,))
            
            for skill in matched_skills:
                cursor.execute(
                    "INSERT INTO skills (resume_id, skill, is_matched) VALUES (?, ?, 1)",
                    (resume_id, skill)
                )
            for skill in missing_skills:
                cursor.execute(
                    "INSERT INTO skills (resume_id, skill, is_matched) VALUES (?, ?, 0)",
                    (resume_id, skill)
                )
            conn.commit()

    def get_resume_skills(self, resume_id: int) -> Dict[str, List[str]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT skill, is_matched FROM skills WHERE resume_id = ?", (resume_id,))
            rows = cursor.fetchall()
            
            matched = [row["skill"] for row in rows if row["is_matched"] == 1]
            missing = [row["skill"] for row in rows if row["is_matched"] == 0]
            return {"matched": matched, "missing": missing}

    # --- Reports ---
    def save_report(self, resume_id: int, pdf_name: str, pdf_path: str) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO reports (resume_id, pdf_name, pdf_path) VALUES (?, ?, ?)",
                (resume_id, pdf_name, pdf_path)
            )
            conn.commit()
            return cursor.lastrowid

    def get_reports_for_user(self, user_id: int) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT r.id, r.pdf_name, r.pdf_path, r.created_at, res.filename, res.ats_score
                FROM reports r
                JOIN resumes res ON r.resume_id = res.id
                WHERE res.user_id = ?
                ORDER BY r.id ASC
            """, (user_id,))
            return [dict(row) for row in cursor.fetchall()]

    # --- ATS Score History & Resume Versions ---
    def record_score_history(
        self,
        resume_id: int,
        score: float,
        rqi: float = 0.0,
        confidence_score: float = 0.0,
        readiness_score: float = 0.0,
        industry: str = "General",
        company: str = ""
    ) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO ats_score_history
                (resume_id, score, rqi, confidence_score, readiness_score, industry, company)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (resume_id, score, rqi, confidence_score, readiness_score, industry, company))
            conn.commit()
            return cursor.lastrowid

    def get_score_history(self, resume_id: int) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM ats_score_history
                WHERE resume_id = ?
                ORDER BY created_at ASC
            """, (resume_id,))
            return [dict(row) for row in cursor.fetchall()]

    def create_resume_version(
        self,
        resume_id: int,
        version_name: str,
        extracted_text: str,
        ats_score: float = 0.0
    ) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COALESCE(MAX(version_number), 0) + 1 FROM resume_versions WHERE resume_id = ?",
                (resume_id,)
            )
            next_ver = cursor.fetchone()[0]
            cursor.execute("""
                INSERT INTO resume_versions (resume_id, version_number, version_name, extracted_text, ats_score)
                VALUES (?, ?, ?, ?, ?)
            """, (resume_id, next_ver, version_name, extracted_text, ats_score))
            conn.commit()
            return cursor.lastrowid

    def get_resume_versions(self, resume_id: int) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM resume_versions
                WHERE resume_id = ?
                ORDER BY version_number ASC
            """, (resume_id,))
            return [dict(row) for row in cursor.fetchall()]

db = DatabaseManager()
