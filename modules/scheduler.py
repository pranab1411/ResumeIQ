"""
Feature 18: Background ATS Re-scan Scheduler for ResumeIQ.
Uses QTimer to periodically re-score saved resumes and track score changes.
"""

from PyQt6.QtCore import QObject, QTimer, pyqtSignal
from utils.logger import logger

class ATSRescanScheduler(QObject):
    """
    Background scheduler that re-scans saved resumes weekly and reports score changes.
    Runs as a QObject with a QTimer — no threads needed.
    """

    rescan_complete = pyqtSignal(list)   # Emits list of {filename, old_score, new_score, delta}
    rescan_started = pyqtSignal()

    def __init__(self, user_id: int, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.run_rescan)

    def start(self, interval_ms: int = 7 * 24 * 60 * 60 * 1000):
        """Start the scheduler. Default interval: 7 days."""
        self.timer.start(interval_ms)
        logger.info(f"[Scheduler] ATS rescan scheduler started (interval: {interval_ms // 1000}s)")

    def stop(self):
        self.timer.stop()
        logger.info("[Scheduler] ATS rescan scheduler stopped.")

    def run_rescan(self):
        """Performs an immediate rescan of all user resumes."""
        try:
            from database.database import db
            from modules.local_ai_agent import local_ai_agent

            self.rescan_started.emit()
            logger.info(f"[Scheduler] Starting scheduled ATS rescan for user {self.user_id}...")

            resumes = db.get_user_resumes(self.user_id)
            changes = []

            for resume in resumes:
                if not resume.get("extracted_text") or not resume.get("job_description"):
                    continue
                try:
                    old_score = float(resume.get("ats_score", 0.0))
                    result = local_ai_agent.analyze_resume(
                        resume["extracted_text"],
                        resume.get("job_description", ""),
                        mode="experienced"
                    )
                    new_score = float(result.get("ats_score", old_score))
                    delta = round(new_score - old_score, 1)

                    if abs(delta) >= 1.0:  # Only track meaningful changes
                        db.update_resume_analysis(resume["id"], new_score, resume.get("job_title", ""), resume.get("job_description", ""))
                        changes.append({
                            "filename": resume["filename"],
                            "old_score": old_score,
                            "new_score": new_score,
                            "delta": delta
                        })
                        logger.info(f"[Scheduler] {resume['filename']}: {old_score}% → {new_score}% (Δ{delta:+})")
                except Exception as e:
                    logger.warning(f"[Scheduler] Could not rescan {resume.get('filename', '?')}: {e}")

            logger.info(f"[Scheduler] Rescan complete. {len(changes)} resumes had score changes.")
            self.rescan_complete.emit(changes)

        except Exception as e:
            logger.error(f"[Scheduler] Rescan error: {e}")
