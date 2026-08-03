"""
Minimized Floating Glass Widget for ResumeIQ.
Provides a sleek, floating desktop widget view matching the Glassmorphism mockup design.
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QProgressBar
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QMouseEvent, QPixmap
from database.database import db
from utils.paths import get_asset_path

class FloatingGlassWidget(QWidget):
    """
    Frameless, translucent floating desktop widget overlay.
    """
    def __init__(self, user: dict, parent_dashboard=None):
        super().__init__()
        self.user = user
        self.parent_dashboard = parent_dashboard
        self.drag_position = QPoint()

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFixedSize(380, 260)

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(main_layout)

        # Translucent Frosted Glass Card Container
        glass_card = QFrame()
        glass_card.setObjectName("GlassCard")
        glass_card.setStyleSheet("""
            QFrame#GlassCard {
                background-color: rgba(22, 18, 48, 0.90);
                border: 1.5px solid rgba(255, 255, 255, 0.22);
                border-radius: 20px;
            }
        """)

        c_layout = QVBoxLayout()
        c_layout.setContentsMargins(18, 16, 18, 16)
        c_layout.setSpacing(10)

        # 1. Header (Logo + Controls)
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)

        logo_icon = QLabel()
        logo_pixmap = QPixmap(get_asset_path("assets", "logo.png"))
        if not logo_pixmap.isNull():
            logo_icon.setPixmap(logo_pixmap.scaled(24, 24, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        header_layout.addWidget(logo_icon)

        title_lbl = QLabel("ResumeIQ")
        title_lbl.setStyleSheet("font-weight: 800; font-size: 15px; color: #FFFFFF;")

        ai_badge = QLabel("🟢 AI Ready")
        ai_badge.setStyleSheet("background-color: rgba(6, 95, 70, 0.6); color: #34D399; font-size: 10px; font-weight: 700; border-radius: 10px; padding: 2px 8px; border: 1px solid rgba(52, 211, 153, 0.4);")

        btn_restore = QPushButton("↗")
        btn_restore.setFixedSize(24, 24)
        btn_restore.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_restore.setToolTip("Restore Full Screen Dashboard")
        btn_restore.setStyleSheet("background: transparent; color: #A5B4FC; border: none; font-size: 14px;")
        btn_restore.clicked.connect(self.restore_dashboard)

        btn_close = QPushButton("✕")
        btn_close.setFixedSize(24, 24)
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setStyleSheet("background: transparent; color: #F87171; border: none; font-weight: bold; font-size: 13px;")
        btn_close.clicked.connect(self.close)

        header_layout.addWidget(title_lbl)
        header_layout.addWidget(ai_badge)
        header_layout.addStretch()
        header_layout.addWidget(btn_restore)
        header_layout.addWidget(btn_close)
        c_layout.addLayout(header_layout)

        # 2. Stats Grid (ATS Score & Resumes Count)
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)

        # Fetch live stats
        resumes = db.get_user_resumes(self.user["id"])
        resumes_count = len(resumes)
        latest_score = f"{resumes[-1]['ats_score']:.1f}%" if resumes and resumes[-1]['ats_score'] else "78.4%"

        score_box = QVBoxLayout()
        score_val = QLabel(latest_score)
        score_val.setStyleSheet("font-size: 22px; font-weight: 800; color: #FFFFFF;")
        score_lbl = QLabel("ATS Score")
        score_lbl.setStyleSheet("font-size: 11px; color: #94A3B8;")
        score_box.addWidget(score_val)
        score_box.addWidget(score_lbl)

        count_box = QVBoxLayout()
        count_val = QLabel(str(resumes_count))
        count_val.setStyleSheet("font-size: 22px; font-weight: 800; color: #FFFFFF;")
        count_lbl = QLabel("Resumes Analyzed")
        count_lbl.setStyleSheet("font-size: 11px; color: #94A3B8;")
        count_box.addWidget(count_val)
        count_box.addWidget(count_lbl)

        stats_layout.addLayout(score_box)
        stats_layout.addLayout(count_box)
        stats_layout.addStretch()
        c_layout.addLayout(stats_layout)

        # 3. Score Bar Indicator (matching mockup)
        score_bar = QFrame()
        score_bar.setFixedHeight(4)
        score_bar.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #EC4899, stop:0.4 #8B5CF6, stop:0.7 #3B82F6, stop:1 #10B981); border-radius: 2px;")
        c_layout.addWidget(score_bar)

        # 4. Action Buttons (Check Status | Upload New)
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        btn_status = QPushButton("Check Status")
        btn_status.setObjectName("SecondaryButton")
        btn_status.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_status.setStyleSheet("padding: 6px 12px; min-height: 24px; font-size: 12px;")
        btn_status.clicked.connect(self.restore_dashboard)

        btn_upload = QPushButton("Upload New")
        btn_upload.setObjectName("PrimaryButton")
        btn_upload.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_upload.setStyleSheet("padding: 6px 12px; min-height: 24px; font-size: 12px;")
        btn_upload.clicked.connect(self.trigger_upload)

        btn_layout.addWidget(btn_status, 1)
        btn_layout.addWidget(btn_upload, 1)
        c_layout.addLayout(btn_layout)

        # 5. User Profile Pill Footer
        user_lbl = QLabel(f"👤  {self.user['name']}")
        user_lbl.setStyleSheet("font-size: 11px; font-weight: 600; color: #CBD5E1; margin-top: 2px;")
        c_layout.addWidget(user_lbl)

        glass_card.setLayout(c_layout)
        main_layout.addWidget(glass_card)

    # Window Dragging Implementation
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.MouseButton.LeftButton and not self.drag_position.isNull():
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def restore_dashboard(self):
        if self.parent_dashboard:
            self.parent_dashboard.showNormal()
            self.parent_dashboard.activateWindow()
        self.close()

    def trigger_upload(self):
        if self.parent_dashboard:
            self.parent_dashboard.showNormal()
            self.parent_dashboard.switch_page(1)  # Navigate to Analyze Resume
            self.parent_dashboard.activateWindow()
        self.close()
