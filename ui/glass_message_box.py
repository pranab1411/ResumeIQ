import sys
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QColor, QFont, QIcon

class GlassMessageBox(QDialog):
    """Custom Glassmorphism Styled Modal Dialog for ResumeIQ."""
    
    def __init__(self, parent=None, title="Notification", message="", icon_type="info"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedWidth(420)
        
        # Enable translucent background & frameless look
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)

        # Outer Container Frame with Glassmorphism Border & Background
        container = QFrame(self)
        container.setObjectName("GlassDialogFrame")
        container.setStyleSheet("""
            QFrame#GlassDialogFrame {
                background-color: rgba(22, 19, 44, 0.94);
                border: 1.5px solid rgba(168, 85, 247, 0.45);
                border-radius: 16px;
            }
        """)

        # Drop Shadow Effect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(139, 92, 246, 90))
        shadow.setOffset(0, 8)
        container.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(container)

        dialog_layout = QVBoxLayout(container)
        dialog_layout.setContentsMargins(24, 20, 24, 20)
        dialog_layout.setSpacing(14)

        # Header Layout (Icon + Title)
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)

        # Select Icon Emoji
        icons = {
            "info": "ℹ️",
            "success": "🎉",
            "warning": "⚠️",
            "error": "❌",
            "email": "📧"
        }
        emoji = icons.get(icon_type.lower(), "ℹ️")

        icon_label = QLabel(emoji)
        icon_label.setStyleSheet("font-size: 26px; background: transparent;")
        header_layout.addWidget(icon_label)

        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 17px; font-weight: 800; color: #FFFFFF; background: transparent;")
        header_layout.addWidget(title_label, 1)

        # Close X Button
        btn_close = QPushButton("✕")
        btn_close.setFixedSize(28, 28)
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.08);
                color: #94A3B8;
                border: none;
                border-radius: 14px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(239, 68, 68, 0.7);
                color: #FFFFFF;
            }
        """)
        btn_close.clicked.connect(self.reject)
        header_layout.addWidget(btn_close)

        dialog_layout.addLayout(header_layout)

        # Body Message Text Label
        msg_label = QLabel(message)
        msg_label.setWordWrap(True)
        msg_label.setStyleSheet("font-size: 13.5px; font-weight: 500; color: #CBD5E1; line-height: 1.4; background: transparent;")
        dialog_layout.addWidget(msg_label)

        dialog_layout.addSpacing(6)

        # Action Buttons Layout
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_ok = QPushButton("OK")
        btn_ok.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_ok.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6366F1, stop:0.5 #8B5CF6, stop:1 #EC4899);
                color: #FFFFFF;
                border: none;
                border-radius: 10px;
                padding: 8px 24px;
                min-width: 90px;
                min-height: 28px;
                font-weight: 700;
                font-size: 14px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4F46E5, stop:0.5 #7C3AED, stop:1 #DB2777);
            }
        """)
        btn_ok.clicked.connect(self.accept)
        btn_layout.addWidget(btn_ok)
        btn_layout.addStretch()

        dialog_layout.addLayout(btn_layout)

        # Support Window Dragging
        self._drag_pos = None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self._drag_pos:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    # Static Convenience Methods matching QMessageBox API
    @staticmethod
    def information(parent, title, message):
        dialog = GlassMessageBox(parent, title, message, icon_type="info")
        return dialog.exec()

    @staticmethod
    def success(parent, title, message):
        dialog = GlassMessageBox(parent, title, message, icon_type="success")
        return dialog.exec()

    @staticmethod
    def warning(parent, title, message):
        dialog = GlassMessageBox(parent, title, message, icon_type="warning")
        return dialog.exec()

    @staticmethod
    def critical(parent, title, message):
        dialog = GlassMessageBox(parent, title, message, icon_type="error")
        return dialog.exec()
