"""
ui/about_developer_page.py
Dedicated About Developer & Engine Architecture Page for ResumeIQ v2.1.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QGridLayout, QScrollArea
)
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices

class AboutDeveloperPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(20)

        # Header Title
        header_box = QVBoxLayout()
        header_title = QLabel("👨‍💻 About Developer & ResumeIQ Engine")
        header_title.setObjectName("HeaderTitle")
        header_title.setStyleSheet("font-size: 22px; font-weight: bold; color: #F8FAFC;")
        
        header_sub = QLabel("Hybrid Gemini AI & spaCy NLP Resume Intelligence & Career Optimization Suite")
        header_sub.setStyleSheet("font-size: 13px; color: #94A3B8;")
        
        header_box.addWidget(header_title)
        header_box.addWidget(header_sub)
        content_layout.addLayout(header_box)

        # Top Section: Developer Profile Card & Mission Card
        top_grid = QHBoxLayout()
        top_grid.setSpacing(20)

        # Developer Profile Card
        dev_card = QFrame()
        dev_card.setObjectName("CardFrame")
        dev_card.setStyleSheet("background: #1E293B; border-radius: 12px; border: 1px solid #334155;")
        dev_layout = QVBoxLayout(dev_card)
        dev_layout.setContentsMargins(20, 20, 20, 20)
        dev_layout.setSpacing(12)

        dev_badge = QLabel("DEVELOPER PROFILE")
        dev_badge.setStyleSheet("font-size: 10px; font-weight: bold; color: #818CF8; letter-spacing: 1px;")
        
        dev_name = QLabel("Pranab Chourasiya")
        dev_name.setStyleSheet("font-size: 20px; font-weight: bold; color: #F8FAFC;")

        dev_bio = QLabel(
            "Designed and engineered ResumeIQ — a local, privacy-first resume analysis "
            "and ATS matching engine built to empower job seekers with instant, defensible "
            "resume improvements without cloud data exposure."
        )
        dev_bio.setWordWrap(True)
        dev_bio.setStyleSheet("font-size: 12px; color: #CBD5E1; line-height: 1.4;")

        # Action Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        btn_linkedin = QPushButton("💼 LinkedIn Profile")
        btn_linkedin.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_linkedin.setStyleSheet("""
            QPushButton {
                background: #0A66C2; color: white; border-radius: 6px; padding: 8px 14px; font-weight: bold; font-size: 11.5px;
            }
            QPushButton:hover { background: #004182; }
        """)
        btn_linkedin.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://www.linkedin.com/in/pranab-chourasiya-87409735b/")))

        btn_github = QPushButton("🐙 GitHub Profile")
        btn_github.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_github.setStyleSheet("""
            QPushButton {
                background: #334155; color: #F8FAFC; border-radius: 6px; padding: 8px 14px; font-weight: bold; font-size: 11.5px;
            }
            QPushButton:hover { background: #475569; }
        """)
        btn_github.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/pranab1411")))

        btn_repo = QPushButton("⭐ ResumeIQ Repo")
        btn_repo.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_repo.setStyleSheet("""
            QPushButton {
                background: #4F46E5; color: white; border-radius: 6px; padding: 8px 14px; font-weight: bold; font-size: 11.5px;
            }
            QPushButton:hover { background: #4338CA; }
        """)
        btn_repo.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/pranab1411/ResumeIQ")))

        btn_email = QPushButton("✉️ Contact Developer")
        btn_email.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_email.setStyleSheet("""
            QPushButton {
                background: #059669; color: white; border-radius: 6px; padding: 8px 14px; font-weight: bold; font-size: 11.5px;
            }
            QPushButton:hover { background: #047857; }
        """)
        btn_email.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("mailto:pranabchourasiya876@gmail.com")))

        btn_layout.addWidget(btn_linkedin)
        btn_layout.addWidget(btn_github)
        btn_layout.addWidget(btn_repo)
        btn_layout.addWidget(btn_email)
        btn_layout.addStretch()

        dev_layout.addWidget(dev_badge)
        dev_layout.addWidget(dev_name)
        dev_layout.addWidget(dev_bio)
        dev_layout.addLayout(btn_layout)

        # Engine Mission Card
        mission_card = QFrame()
        mission_card.setObjectName("CardFrame")
        mission_card.setStyleSheet("background: #1E293B; border-radius: 12px; border: 1px solid #334155;")
        mission_layout = QVBoxLayout(mission_card)
        mission_layout.setContentsMargins(20, 20, 20, 20)
        mission_layout.setSpacing(12)

        mission_badge = QLabel("CORE ARCHITECTURE PROMISE")
        mission_badge.setStyleSheet("font-size: 10px; font-weight: bold; color: #34D399; letter-spacing: 1px;")

        mission_title = QLabel("🤖 Hybrid Gemini AI & Local Intelligence")
        mission_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #F8FAFC;")

        p1 = QLabel("• <b>Google Gemini AI:</b> Used for holistic candidate entity extraction and multi-industry target job role prediction.")
        p1.setWordWrap(True)
        p1.setStyleSheet("font-size: 12px; color: #CBD5E1;")

        p2 = QLabel("• <b>On-Device spaCy NLP:</b> Extracts skills, contact info, and metrics locally with zero dependency when offline.")
        p2.setWordWrap(True)
        p2.setStyleSheet("font-size: 12px; color: #CBD5E1;")

        p3 = QLabel("• <b>MCDA & Report Engine:</b> Calculates transparent ATS matching scores and generates vector PDF evaluation reports.")
        p3.setWordWrap(True)
        p3.setStyleSheet("font-size: 12px; color: #CBD5E1;")

        mission_layout.addWidget(mission_badge)
        mission_layout.addWidget(mission_title)
        mission_layout.addWidget(p1)
        mission_layout.addWidget(p2)
        mission_layout.addWidget(p3)
        mission_layout.addStretch()

        top_grid.addWidget(dev_card, 1)
        top_grid.addWidget(mission_card, 1)
        content_layout.addLayout(top_grid)

        # Tech Stack Grid Section
        stack_card = QFrame()
        stack_card.setStyleSheet("background: #1E293B; border-radius: 12px; border: 1px solid #334155;")
        stack_layout = QVBoxLayout(stack_card)
        stack_layout.setContentsMargins(20, 20, 20, 20)
        stack_layout.setSpacing(15)

        stack_title = QLabel("🛠️ Technology Stack & Core Engines")
        stack_title.setStyleSheet("font-size: 15px; font-weight: bold; color: #F8FAFC;")
        stack_layout.addWidget(stack_title)

        tech_grid = QGridLayout()
        tech_grid.setSpacing(12)

        tech_items = [
            ("🤖 Google Gemini AI", "4-Part Profile Analysis & 50+ Role Prediction", "#F43F5E"),
            ("🧠 spaCy NLP", "Name & Skill Extraction Engine", "#A78BFA"),
            ("🐍 Python 3.11", "Core Runtime & Asynchronous Engine", "#38BDF8"),
            ("🖥️ PyQt6 GUI", "Glassmorphic Dark Interface", "#818CF8"),
            ("📑 ReportLab 5", "Single-Page Executive PDF Builder", "#F472B6"),
            ("🗄️ SQLite WAL", "Local Encrypted Database Storage", "#34D399")
        ]

        for i, (title, desc, color) in enumerate(tech_items):
            row = i // 3
            col = i % 3
            item_frame = QFrame()
            item_frame.setStyleSheet("background: rgba(255,255,255,0.03); border-radius: 8px; padding: 10px; border: 1px solid rgba(255,255,255,0.05);")
            item_layout = QVBoxLayout(item_frame)
            item_layout.setContentsMargins(10, 10, 10, 10)
            
            t_lbl = QLabel(title)
            t_lbl.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {color};")
            d_lbl = QLabel(desc)
            d_lbl.setStyleSheet("font-size: 11px; color: #94A3B8;")
            
            item_layout.addWidget(t_lbl)
            item_layout.addWidget(d_lbl)
            tech_grid.addWidget(item_frame, row, col)

        stack_layout.addLayout(tech_grid)
        content_layout.addWidget(stack_card)

        # Footer Version Details
        footer_lbl = QLabel("ResumeIQ v2.0 • Crafted with ❤️ by Pranab Chourasiya • All Rights Reserved")
        footer_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer_lbl.setStyleSheet("font-size: 11.5px; color: #64748B; margin-top: 10px;")
        content_layout.addWidget(footer_lbl)

        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)
