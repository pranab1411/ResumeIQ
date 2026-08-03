"""
Feature 17: User Profile Page for ResumeIQ.
Shows user avatar, stats, account details, and management actions.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QGridLayout, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor
from database.database import db
from modules.ats_calculator import ATSCalculator
from utils.logger import logger


class ProfilePage(QWidget):
    """User Profile page displaying avatar, stats, and account actions."""

    logout_requested = pyqtSignal()

    def __init__(self, user: dict, parent=None):
        super().__init__(parent)
        self.user = user
        self._build_ui()

    def _build_ui(self):
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        scroll.setWidget(container)

        # Page Header
        header = QLabel("👤 My Profile")
        header.setObjectName("HeaderTitle")
        sub = QLabel("View and manage your account information and resume statistics.")
        sub.setObjectName("SubTitle")
        layout.addWidget(header)
        layout.addWidget(sub)

        # Avatar + Identity Card
        identity_card = QFrame()
        identity_card.setObjectName("CardFrame")
        id_layout = QHBoxLayout(identity_card)
        id_layout.setContentsMargins(24, 24, 24, 24)
        id_layout.setSpacing(24)

        # Avatar circle (initials)
        initials = "".join([n[0].upper() for n in self.user.get("name", "U").split()[:2]])
        avatar_lbl = QLabel(initials)
        avatar_lbl.setFixedSize(80, 80)
        avatar_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar_lbl.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #6366F1, stop:1 #EC4899);
            border-radius: 40px;
            font-size: 28px;
            font-weight: 800;
            color: #FFFFFF;
        """)
        id_layout.addWidget(avatar_lbl)

        # User info text
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)
        name_lbl = QLabel(self.user.get("name", "Unknown User"))
        name_lbl.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        name_lbl.setStyleSheet("color: #FFFFFF;")

        email_lbl = QLabel(f"📧 {self.user.get('email', 'N/A')}")
        email_lbl.setStyleSheet("color: #A5B4FC; font-size: 13px;")

        username_lbl = QLabel(f"🆔 @{self.user.get('username', 'N/A')}")
        username_lbl.setStyleSheet("color: #94A3B8; font-size: 12px;")

        joined_lbl = QLabel(f"📅 Member since {str(self.user.get('created_at', 'N/A'))[:10]}")
        joined_lbl.setStyleSheet("color: #64748B; font-size: 12px;")

        info_layout.addWidget(name_lbl)
        info_layout.addWidget(email_lbl)
        info_layout.addWidget(username_lbl)
        info_layout.addWidget(joined_lbl)
        id_layout.addLayout(info_layout, 1)

        layout.addWidget(identity_card)

        # --- Stats Grid ---
        stats_header = QLabel("📊 Resume Statistics")
        stats_header.setObjectName("SectionHeader")
        layout.addWidget(stats_header)

        stats_grid = QGridLayout()
        stats_grid.setSpacing(16)
        self._populate_stats(stats_grid)
        layout.addLayout(stats_grid)

        # --- Account Actions ---
        actions_header = QLabel("⚙️ Account Actions")
        actions_header.setObjectName("SectionHeader")
        layout.addWidget(actions_header)

        actions_card = QFrame()
        actions_card.setObjectName("CardFrame")
        actions_layout = QHBoxLayout(actions_card)
        actions_layout.setContentsMargins(20, 16, 20, 16)
        actions_layout.setSpacing(12)

        btn_logout = QPushButton("🚪 Sign Out")
        btn_logout.setObjectName("SecondaryButton")
        btn_logout.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_logout.clicked.connect(self.logout_requested.emit)

        actions_layout.addWidget(btn_logout)
        actions_layout.addStretch()
        layout.addWidget(actions_card)

    def _populate_stats(self, grid: QGridLayout):
        """Fetches resume stats from DB and populates the stats grid."""
        try:
            resumes = db.get_user_resumes(self.user["id"])
            count = len(resumes)
            avg_score = round(sum(r["ats_score"] for r in resumes) / count, 1) if count else 0.0
            best_score = max((r["ats_score"] for r in resumes), default=0.0)
            best_cat = ATSCalculator.get_score_category(best_score)
        except Exception as e:
            logger.error(f"[ProfilePage] Stats error: {e}")
            count, avg_score, best_score, best_cat = 0, 0.0, 0.0, "N/A"

        stat_items = [
            ("📄", "Total Resumes", str(count), "#6366F1"),
            ("📊", "Avg ATS Score", f"{avg_score}%", "#10B981"),
            ("🏆", "Best Score", f"{best_score}%", "#F59E0B"),
            ("🎯", "Top Rating", best_cat, "#EC4899"),
        ]

        for col, (icon, title, value, color) in enumerate(stat_items):
            card = QFrame()
            card.setObjectName("KPICard")
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(18, 18, 18, 18)
            card_layout.setSpacing(6)
            card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            icon_lbl = QLabel(icon)
            icon_lbl.setStyleSheet(f"font-size: 26px;")
            icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

            val_lbl = QLabel(value)
            val_lbl.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
            val_lbl.setStyleSheet(f"color: {color};")
            val_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

            title_lbl = QLabel(title)
            title_lbl.setStyleSheet("color: #94A3B8; font-size: 12px;")
            title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

            card_layout.addWidget(icon_lbl)
            card_layout.addWidget(val_lbl)
            card_layout.addWidget(title_lbl)
            grid.addWidget(card, 0, col)
