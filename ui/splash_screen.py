"""
Glassmorphism Startup Splash / Loading Screen for ResumeIQ.
Provides a modern loading animation during application startup.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, QFrame, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QPixmap
from utils.paths import get_asset_path

class SplashScreen(QWidget):
    """Frameless Translucent Glassmorphism Splash Screen with Animated Progress Bar."""
    
    loading_complete = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.SplashScreen)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFixedSize(500, 340)

        self.progress_val = 0
        self.status_messages = [
            (15, "Initializing Database Schema..."),
            (35, "Loading spaCy NLP Engine..."),
            (60, "Loading Real 4-Pillar ATS Calculation Engine..."),
            (85, "Loading Top MNC ATS Registry (Workday, Taleo, Greenhouse)..."),
            (100, "Ready! Launching ResumeIQ...")
        ]
        self.msg_idx = 0

        self.init_ui()
        self.start_timer()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Translucent Glass Card Frame
        card = QFrame()
        card.setObjectName("GlassSplashCard")
        card.setStyleSheet("""
            QFrame#GlassSplashCard {
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
        card_layout.setContentsMargins(35, 30, 35, 30)
        card_layout.setSpacing(12)
        card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Logo Image
        self.logo_label = QLabel()
        logo_pixmap = QPixmap(get_asset_path("assets", "logo.png"))
        if not logo_pixmap.isNull():
            self.logo_label.setPixmap(logo_pixmap.scaled(85, 85, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(self.logo_label)

        # Title & Subtitle
        self.title_label = QLabel("ResumeIQ")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("font-size: 28px; font-weight: 800; color: #FFFFFF; letter-spacing: 1px;")

        self.subtitle_label = QLabel("AI Resume & Career Intelligence Engine")
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle_label.setStyleSheet("font-size: 13px; font-weight: 600; color: #A5B4FC;")

        card_layout.addWidget(self.title_label)
        card_layout.addWidget(self.subtitle_label)
        card_layout.addSpacing(10)

        # Status Message Text Label
        self.lbl_status = QLabel("Initializing Application...")
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_status.setStyleSheet("font-size: 12px; font-weight: 500; color: #CBD5E1;")
        card_layout.addWidget(self.lbl_status)

        # Neon Gradient Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 4px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6366F1, stop:0.5 #8B5CF6, stop:1 #EC4899);
                border-radius: 3px;
            }
        """)
        card_layout.addWidget(self.progress_bar)

        # Version Pill Label
        self.lbl_version = QLabel("v2.5 Pro • 100% Offline AI")
        self.lbl_version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_version.setStyleSheet("font-size: 11px; color: #64748B; margin-top: 4px;")
        card_layout.addWidget(self.lbl_version)

    def start_timer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_progress)
        self.timer.start(35) # Smooth progress interval

    def _update_progress(self):
        self.progress_val += 2
        self.progress_bar.setValue(self.progress_val)

        # Update status text based on progress milestone
        if self.msg_idx < len(self.status_messages):
            target_val, msg = self.status_messages[self.msg_idx]
            if self.progress_val >= target_val:
                self.lbl_status.setText(msg)
                self.msg_idx += 1

        if self.progress_val >= 100:
            self.timer.stop()
            QTimer.singleShot(400, self._on_finish)

    def _on_finish(self):
        self.loading_complete.emit()
        self.close()

    def center_on_screen(self, screen_geometry):
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)
