"""
Glassmorphism App Closing / Exit Screen for ResumeIQ.
Provides a smooth exit animation and status cleanup screen when quitting the application.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar, QFrame, QGraphicsDropShadowEffect, QApplication
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QPixmap
from utils.paths import get_asset_path

class ClosingScreen(QWidget):
    """Frameless Translucent Glassmorphism Exit/Closing Screen."""

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.SplashScreen)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFixedSize(460, 300)

        self.progress_val = 0
        self.status_messages = [
            (25, "Saving Session Data & User Preferences..."),
            (55, "Flushing Local AI Agent Engine Cache..."),
            (85, "Cleaning Up Temporary Workspace Files..."),
            (100, "Goodbye! ResumeIQ Session Ended.")
        ]
        self.msg_idx = 0

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Translucent Glass Card Frame
        card = QFrame()
        card.setObjectName("GlassClosingCard")
        card.setStyleSheet("""
            QFrame#GlassClosingCard {
                background-color: rgba(20, 16, 42, 0.96);
                border: 1.5px solid rgba(168, 85, 247, 0.5);
                border-radius: 20px;
            }
        """)

        # Drop Shadow Effect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(35)
        shadow.setColor(QColor(139, 92, 246, 110))
        shadow.setOffset(0, 8)
        card.setGraphicsEffect(shadow)

        layout.addWidget(card)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(30, 25, 30, 25)
        card_layout.setSpacing(10)
        card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Logo Image
        logo_label = QLabel()
        logo_pixmap = QPixmap(get_asset_path("assets", "logo.png"))
        if not logo_pixmap.isNull():
            logo_label.setPixmap(logo_pixmap.scaled(72, 72, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(logo_label)

        # Title & Subtitle
        title_label = QLabel("Closing ResumeIQ...")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: 800; color: #FFFFFF;")

        subtitle_label = QLabel("Thank you for using ResumeIQ AI Systems")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("font-size: 12.5px; font-weight: 600; color: #A5B4FC;")

        card_layout.addWidget(title_label)
        card_layout.addWidget(subtitle_label)
        card_layout.addSpacing(8)

        # Status Message Text Label
        self.lbl_status = QLabel("Saving session & shutting down...")
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_status.setStyleSheet("font-size: 12px; font-weight: 500; color: #CBD5E1;")
        card_layout.addWidget(self.lbl_status)

        # Neon Gradient Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 3px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #EC4899, stop:0.5 #8B5CF6, stop:1 #6366F1);
                border-radius: 3px;
            }
        """)
        card_layout.addWidget(self.progress_bar)

    def start_closing(self):
        screen_geo = QApplication.primaryScreen().geometry()
        x = (screen_geo.width() - self.width()) // 2
        y = (screen_geo.height() - self.height()) // 2
        self.move(x, y)
        self.show()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_progress)
        self.timer.start(25)

    def _update_progress(self):
        self.progress_val += 3
        self.progress_bar.setValue(self.progress_val)

        if self.msg_idx < len(self.status_messages):
            target_val, msg = self.status_messages[self.msg_idx]
            if self.progress_val >= target_val:
                self.lbl_status.setText(msg)
                self.msg_idx += 1

        if self.progress_val >= 100:
            self.timer.stop()
            QTimer.singleShot(300, QApplication.quit)

    @staticmethod
    def show_closing_and_exit():
        """Static helper to trigger closing screen animation and exit application."""
        closing_screen = ClosingScreen()
        closing_screen.start_closing()
        # Process Qt events to render closing screen before exiting
        while closing_screen.isVisible() and closing_screen.progress_val < 100:
            QApplication.processEvents()
