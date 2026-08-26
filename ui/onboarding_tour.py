"""
Feature 10: First-Time User Onboarding Walkthrough for ResumeIQ.
Shows a 5-step tooltip overlay guide for new users.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QGraphicsDropShadowEffect, QApplication
)
from PyQt6.QtCore import Qt, QTimer, QPoint
from PyQt6.QtGui import QColor, QFont
from database.database import db
from utils.logger import logger


TOUR_STEPS = [
    {
        "icon": "👋",
        "title": "Welcome to ResumeIQ!",
        "body": "ResumeIQ uses AI to analyze your resume against top MNC ATS systems like Workday, Taleo, Greenhouse, Lever, and iCIMS. Let's take a quick tour!",
        "step": "1 / 5"
    },
    {
        "icon": "📄",
        "title": "Analyze Your Resume",
        "body": "Go to 'Analyze Resume' in the sidebar. Upload your PDF or DOCX resume, paste a job description, and click Analyze to get your ATS compatibility score.",
        "step": "2 / 5"
    },
    {
        "icon": "🌐",
        "title": "Top MNC ATS Scoring",
        "body": "After analysis, you'll see your resume scored across 5 top MNC ATS platforms. Each system (Workday, Taleo, etc.) has different weighting criteria.",
        "step": "3 / 5"
    },
    {
        "icon": "📈",
        "title": "Analytics & History",
        "body": "Visit the 'Analytics' page to see your ATS score history chart, skill radar chart, and industry benchmarking percentile.",
        "step": "4 / 5"
    },
    {
        "icon": "🚀",
        "title": "You're All Set!",
        "body": "Export comprehensive PDF evaluation reports and ask our AI Assistant for tailored resume improvement advice!",
        "step": "5 / 5"
    },
]


class OnboardingTour(QDialog):
    """5-step glassmorphism onboarding dialog for first-time users."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_step = 0
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setModal(True)
        self.setFixedSize(480, 300)
        self._build_ui()
        self._update_step()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.card = QFrame()
        self.card.setObjectName("GlassCard")
        self.card.setStyleSheet("""
            QFrame#GlassCard {
                background-color: rgba(22, 19, 44, 0.97);
                border: 1.5px solid rgba(139, 92, 246, 0.6);
                border-radius: 20px;
            }
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setColor(QColor(139, 92, 246, 120))
        shadow.setOffset(0, 10)
        self.card.setGraphicsEffect(shadow)
        layout.addWidget(self.card)

        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(30, 26, 30, 22)
        card_layout.setSpacing(12)

        # Step indicator
        self.lbl_step = QLabel("1 / 5")
        self.lbl_step.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.lbl_step.setStyleSheet("color: #64748B; font-size: 11.5px;")
        card_layout.addWidget(self.lbl_step)

        # Icon + Title row
        title_row = QHBoxLayout()
        self.lbl_icon = QLabel("👋")
        self.lbl_icon.setStyleSheet("font-size: 32px;")
        self.lbl_title = QLabel()
        self.lbl_title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        self.lbl_title.setStyleSheet("color: #FFFFFF;")
        title_row.addWidget(self.lbl_icon)
        title_row.addWidget(self.lbl_title, 1)
        card_layout.addLayout(title_row)

        # Body text
        self.lbl_body = QLabel()
        self.lbl_body.setWordWrap(True)
        self.lbl_body.setStyleSheet("color: #CBD5E1; font-size: 13px; line-height: 1.5;")
        card_layout.addWidget(self.lbl_body)
        card_layout.addStretch()

        # Progress dots + Buttons
        bottom_row = QHBoxLayout()

        self.dots_layout = QHBoxLayout()
        self.dots_layout.setSpacing(6)
        self.dot_labels = []
        for i in range(len(TOUR_STEPS)):
            dot = QLabel("●")
            dot.setStyleSheet("color: #334155; font-size: 10px;")
            self.dots_layout.addWidget(dot)
            self.dot_labels.append(dot)
        bottom_row.addLayout(self.dots_layout)
        bottom_row.addStretch()

        self.btn_skip = QPushButton("Skip Tour")
        self.btn_skip.setObjectName("SecondaryButton")
        self.btn_skip.setFixedHeight(34)
        self.btn_skip.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_skip.clicked.connect(self.accept)

        self.btn_next = QPushButton("Next →")
        self.btn_next.setObjectName("PrimaryButton")
        self.btn_next.setFixedHeight(34)
        self.btn_next.setFixedWidth(100)
        self.btn_next.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_next.clicked.connect(self._next_step)

        bottom_row.addWidget(self.btn_skip)
        bottom_row.addWidget(self.btn_next)
        card_layout.addLayout(bottom_row)

    def _update_step(self):
        step = TOUR_STEPS[self.current_step]
        self.lbl_step.setText(step["step"])
        self.lbl_icon.setText(step["icon"])
        self.lbl_title.setText(step["title"])
        self.lbl_body.setText(step["body"])

        # Update dots
        for i, dot in enumerate(self.dot_labels):
            dot.setStyleSheet(
                "color: #8B5CF6; font-size: 10px;" if i == self.current_step
                else "color: #334155; font-size: 10px;"
            )

        is_last = self.current_step == len(TOUR_STEPS) - 1
        self.btn_next.setText("🚀 Get Started!" if is_last else "Next →")

    def _next_step(self):
        if self.current_step < len(TOUR_STEPS) - 1:
            self.current_step += 1
            self._update_step()
        else:
            self.accept()

    @staticmethod
    def show_if_first_time(parent=None):
        """Shows the onboarding tour only on first launch. Stores a flag in DB."""
        try:
            shown = db.get_setting("onboarding_shown", "false")
            if shown == "true":
                return
            db.set_setting("onboarding_shown", "true")
            tour = OnboardingTour(parent)
            # Center on parent or screen
            if parent:
                geo = parent.geometry()
                x = geo.x() + (geo.width() - tour.width()) // 2
                y = geo.y() + (geo.height() - tour.height()) // 2
                tour.move(x, y)
            tour.exec()
            logger.info("[Onboarding] First-time tour completed.")
        except Exception as e:
            logger.warning(f"[Onboarding] Could not show tour: {e}")
