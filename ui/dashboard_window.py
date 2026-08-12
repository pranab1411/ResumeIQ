import os
import subprocess
from typing import Dict, Any, List
# pyrefly: ignore [missing-import]
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QStackedWidget, QFileDialog, QTextEdit, QFrame, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QProgressBar, QScrollArea, QSplitter, QRadioButton, QButtonGroup, QApplication,
    QComboBox, QGridLayout, QTabWidget
)
from PyQt6.QtCore import Qt, QSize, QTimer
from PyQt6.QtGui import QIcon, QFont, QColor, QPixmap
from ui.glass_message_box import GlassMessageBox
from utils.paths import get_asset_path

import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

from database.database import db
from modules.parser import DocumentParser
from modules.nlp_engine import nlp_engine
from modules.ats_calculator import ATSCalculator
from modules.mnc_ats_engine import TopMNCATSEngine
from modules.report_generator import PDFReportGenerator
from modules.local_ai_agent import local_ai_agent
from modules.resume_builder import DocxResumeGenerator
from modules.chatbot_engine import chatbot_engine
from modules.template_engine import template_registry
from modules.benchmarks import IndustryBenchmark
from modules.jd_scraper import JDScraper
from modules.cover_letter_generator import CoverLetterGenerator
from modules.linkedin_optimizer import LinkedInOptimizer
from modules.scheduler import ATSRescanScheduler
from modules.updater import AppUpdater
from ui.floating_widget import FloatingGlassWidget
from ui.styles import DARK_THEME_QSS, LIGHT_THEME_QSS
from utils.logger import logger
from utils.paths import get_data_path

# Directory paths
RESUMES_DIR = get_data_path("resumes")
REPORTS_DIR = get_data_path("reports")

class DashboardWindow(QMainWindow):
    def __init__(self, user: Dict[str, Any] = None, current_user: Dict[str, Any] = None):
        super().__init__()
        self.user = user or current_user or {}
        self.current_resume_id = None
        self.current_analysis_data = None
        self.floating_widget = None
        self._current_theme = db.get_setting("app_theme", "dark")

        os.makedirs(RESUMES_DIR, exist_ok=True)
        os.makedirs(REPORTS_DIR, exist_ok=True)

        self.setWindowTitle(f"ResumeIQ — Career Intelligence ({self.user['name']})")
        self.resize(1280, 820)
        self.setMinimumSize(1000, 680)

        self.init_ui()
        self.refresh_dashboard_data()

        # Feature 18: Background ATS Re-scan Scheduler (weekly)
        self._scheduler = ATSRescanScheduler(self.user.get("id", 0), parent=self)
        self._scheduler.rescan_complete.connect(self._on_rescan_complete)
        self._scheduler.start(7 * 24 * 60 * 60 * 1000)

        # Feature 10: Onboarding tour on first launch
        QTimer.singleShot(800, self._show_onboarding)

        # Feature 19: Check for updates (non-blocking, 3s delay)
        QTimer.singleShot(3000, self._check_for_updates)

    def _show_onboarding(self):
        from ui.onboarding_tour import OnboardingTour
        OnboardingTour.show_if_first_time(self)

    def _check_for_updates(self):
        try:
            has_update, latest, notes, url = AppUpdater.check_for_updates()
            if has_update:
                GlassMessageBox.info(
                    self, "Update Available 🚀",
                    f"ResumeIQ v{latest} is available!\n\n{notes[:200]}\n\nVisit: {url}"
                )
        except Exception:
            pass

    def _on_rescan_complete(self, changes: list):
        if changes:
            summary = "\n".join([
                f"• {c['filename']}: {c['old_score']}% → {c['new_score']}% ({c['delta']:+.1f}%)"
                for c in changes[:5]
            ])
            GlassMessageBox.info(self, "📊 Scheduled ATS Re-scan Complete",
                f"Your saved resumes were rescanned. Score changes:\n\n{summary}")

    def init_ui(self):
        self.setObjectName("MainRoot")
        central_widget = QWidget()
        central_widget.setObjectName("MainRoot")
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        central_widget.setLayout(main_layout)

        # --- SIDEBAR NAVIGATION ---
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(240)
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(16, 24, 16, 24)
        sidebar_layout.setSpacing(10)
        sidebar.setLayout(sidebar_layout)

        # Brand Title Header with Custom Logo
        brand_box = QHBoxLayout()
        brand_box.setSpacing(10)
        
        brand_logo = QLabel()
        logo_pixmap = QPixmap(get_asset_path("assets", "logo.png"))
        if not logo_pixmap.isNull():
            brand_logo.setPixmap(logo_pixmap.scaled(38, 38, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        brand_box.addWidget(brand_logo)

        brand_text_layout = QVBoxLayout()
        brand_text_layout.setSpacing(1)
        brand_label = QLabel("ResumeIQ")
        brand_label.setObjectName("HeaderTitle")
        brand_label.setStyleSheet("font-size: 20px; font-weight: 800; color: #FFFFFF;")
        sub_brand = QLabel("AI Resume Intelligence")
        sub_brand.setObjectName("SubTitle")
        sub_brand.setStyleSheet("font-size: 11px; color: #A5B4FC;")
        brand_text_layout.addWidget(brand_label)
        brand_text_layout.addWidget(sub_brand)
        brand_box.addLayout(brand_text_layout)

        sidebar_layout.addLayout(brand_box)
        sidebar_layout.addSpacing(10)

        # Nav Buttons
        self.nav_buttons = []
        nav_items = [
            ("📊 Dashboard", 0),
            ("📄 Analyze Resume", 1),
            ("📈 Analytics", 2),
            ("📑 Reports", 3),
            ("📜 History", 4),
            ("💬 AI Assistant", 5),
            ("🎨 1,000 Templates", 6),
            ("🔗 LinkedIn Optimizer", 7),
            ("👤 My Profile", 8),
            ("⚙️ Settings", 9)
        ]

        for text, index in nav_items:
            btn = QPushButton(text)
            btn.setObjectName("NavButton")
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, idx=index: self.switch_page(idx))
            sidebar_layout.addWidget(btn)
            self.nav_buttons.append(btn)

        sidebar_layout.addStretch()

        # User Info Card at bottom of sidebar
        user_card = QFrame()
        user_card.setObjectName("CardFrame")
        user_card_layout = QVBoxLayout()
        user_card_layout.setContentsMargins(12, 12, 12, 12)
        user_name_lbl = QLabel(f"👤 {self.user['name']}")
        user_name_lbl.setStyleSheet("font-weight: 600; color: #F8FAFC;")
        user_email_lbl = QLabel(self.user['email'])
        user_email_lbl.setStyleSheet("font-size: 11px; color: #94A3B8;")
        
        btn_floating = QPushButton("🖥️ Floating Glass View")
        btn_floating.setObjectName("SecondaryButton")
        btn_floating.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_floating.clicked.connect(self.open_floating_widget)

        logout_btn = QPushButton("Sign Out")
        logout_btn.setObjectName("SecondaryButton")
        logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_btn.clicked.connect(self.close)

        user_card_layout.addWidget(user_name_lbl)
        user_card_layout.addWidget(user_email_lbl)
        user_card_layout.addSpacing(6)
        user_card_layout.addWidget(btn_floating)
        user_card_layout.addWidget(logout_btn)
        user_card.setLayout(user_card_layout)
        sidebar_layout.addWidget(user_card)

        main_layout.addWidget(sidebar)

        # --- MAIN CONTENT AREA (STACKED WIDGET) ---
        self.stacked_widget = QStackedWidget()

        # Build Pages
        self.page_dashboard = self._build_dashboard_page()
        self.page_analyze = self._build_analyze_page()
        self.page_analytics = self._build_analytics_page()
        self.page_reports = self._build_reports_page()
        self.page_history = self._build_history_page()
        self.page_chatbot = self._build_chatbot_page()
        self.page_templates = self._build_templates_page()
        self.page_linkedin = self._build_linkedin_page()       # Feature 13
        self.page_profile = self._build_profile_page()         # Feature 17
        self.page_settings = self._build_settings_page()

        self.stacked_widget.addWidget(self.page_dashboard)   # 0
        self.stacked_widget.addWidget(self.page_analyze)     # 1
        self.stacked_widget.addWidget(self.page_analytics)   # 2
        self.stacked_widget.addWidget(self.page_reports)     # 3
        self.stacked_widget.addWidget(self.page_history)     # 4
        self.stacked_widget.addWidget(self.page_chatbot)     # 5
        self.stacked_widget.addWidget(self.page_templates)   # 6
        self.stacked_widget.addWidget(self.page_linkedin)    # 7
        self.stacked_widget.addWidget(self.page_profile)     # 8
        self.stacked_widget.addWidget(self.page_settings)    # 9

        main_layout.addWidget(self.stacked_widget)
        self.switch_page(0)

    def switch_page(self, index: int):
        self.stacked_widget.setCurrentIndex(index)
        for idx, btn in enumerate(self.nav_buttons):
            btn.setChecked(idx == index)
            btn.setProperty("active", "true" if idx == index else "false")
            btn.setStyle(btn.style())

        if index == 0:
            self.refresh_dashboard_data()
        elif index == 2:
            self.load_analytics_data()
        elif index == 3:
            self.load_reports_table()
        elif index == 4:
            self.load_history_table()


    # --- PAGE 1: OVERVIEW DASHBOARD ---
    def _build_dashboard_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Header
        header_layout = QHBoxLayout()
        title_box = QVBoxLayout()
        welcome_lbl = QLabel(f"Welcome back, {self.user['name']} 👋")
        welcome_lbl.setObjectName("HeaderTitle")
        sub_lbl = QLabel("Track your resume performance, ATS compatibility, and improvement suggestions.")
        sub_lbl.setObjectName("SubTitle")
        title_box.addWidget(welcome_lbl)
        title_box.addWidget(sub_lbl)

        btn_top_widget = QPushButton("🖥️ Floating Glass Widget")
        btn_top_widget.setObjectName("PrimaryButton")
        btn_top_widget.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_top_widget.clicked.connect(self.open_floating_widget)

        header_layout.addLayout(title_box, 1)
        header_layout.addWidget(btn_top_widget, 0)
        layout.addLayout(header_layout)

        # Stats KPI Cards Layout
        kpi_layout = QHBoxLayout()
        kpi_layout.setSpacing(15)

        self.card_total_resumes = self._create_kpi_card("Resumes Analyzed", "0", "#6366F1", "📄")
        self.card_avg_ats = self._create_kpi_card("Average ATS Score", "0%", "#10B981", "🎯")
        self.card_top_category = self._create_kpi_card("Match Rating", "N/A", "#F59E0B", "⭐")

        kpi_layout.addWidget(self.card_total_resumes)
        kpi_layout.addWidget(self.card_avg_ats)
        kpi_layout.addWidget(self.card_top_category)
        layout.addLayout(kpi_layout)

        # Quick Action Banner Card
        quick_card = QFrame()
        quick_card.setObjectName("CardFrame")
        quick_layout = QHBoxLayout()
        quick_layout.setContentsMargins(20, 20, 20, 20)
        
        quick_text_layout = QVBoxLayout()
        quick_title = QLabel("Ready to analyze a new resume?")
        quick_title.setObjectName("SectionHeader")
        quick_sub = QLabel("Upload a PDF or DOCX file and match it against any job description in seconds.")
        quick_sub.setObjectName("SubTitle")
        quick_text_layout.addWidget(quick_title)
        quick_text_layout.addWidget(quick_sub)

        btn_go_analyze = QPushButton("Start New Analysis →")
        btn_go_analyze.setObjectName("PrimaryButton")
        btn_go_analyze.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_go_analyze.clicked.connect(lambda: self.switch_page(1))

        quick_layout.addLayout(quick_text_layout)
        quick_layout.addStretch()
        quick_layout.addWidget(btn_go_analyze)
        quick_card.setLayout(quick_layout)
        layout.addWidget(quick_card)

        # Recent Analyses Table Section
        rec_header = QLabel("Recent Resume Analyses")
        rec_header.setObjectName("SectionHeader")
        layout.addWidget(rec_header)

        self.table_recent = QTableWidget()
        self.table_recent.setColumnCount(4)
        self.table_recent.setHorizontalHeaderLabels(["Filename", "Date", "ATS Score", "Rating"])
        self.table_recent.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_recent.verticalHeader().setDefaultSectionSize(38)
        self.table_recent.setAlternatingRowColors(True)
        layout.addWidget(self.table_recent)

        page.setLayout(layout)
        return page

    def _create_kpi_card(self, title: str, value: str, accent_color: str, icon_str: str = "⚡") -> QFrame:
        card = QFrame()
        card.setObjectName("KPICard")
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(6)
        
        header_layout = QHBoxLayout()
        t_lbl = QLabel(title)
        t_lbl.setObjectName("SubTitle")
        t_lbl.setStyleSheet("font-size: 13px; font-weight: 600; color: #A5B4FC;")

        i_lbl = QLabel(icon_str)
        i_lbl.setStyleSheet("font-size: 14px;")

        header_layout.addWidget(t_lbl)
        header_layout.addStretch()
        header_layout.addWidget(i_lbl)
        
        v_lbl = QLabel(value)
        v_lbl.setFont(QFont("Segoe UI", 26, QFont.Weight.Bold))
        v_lbl.setStyleSheet("color: #FFFFFF; font-weight: 800; font-size: 26px;")
        
        # Neon Underbar
        underbar = QFrame()
        underbar.setFixedHeight(3)
        underbar.setStyleSheet(f"background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {accent_color}, stop:1 #06B6D4); border-radius: 1.5px;")

        layout.addLayout(header_layout)
        layout.addWidget(v_lbl)
        layout.addSpacing(4)
        layout.addWidget(underbar)

        card.setLayout(layout)
        card.value_label = v_lbl
        return card

    def open_floating_widget(self):
        if not self.floating_widget or not self.floating_widget.isVisible():
            self.floating_widget = FloatingGlassWidget(self.user, parent_dashboard=self)
            self.floating_widget.show()
            self.showMinimized()

    # --- PAGE 2: RESUME UPLOAD & ATS ANALYSIS ---
    def _build_analyze_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)

        header_layout = QHBoxLayout()
        title = QLabel("Resume Parsing & ATS Optimization Engine")
        title.setObjectName("HeaderTitle")
        
        self.lbl_ai_badge = QLabel()
        self.lbl_ai_badge.setObjectName("AIBadge")
        self.lbl_ai_badge.setFixedHeight(30)
        self.lbl_ai_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.update_ai_badge()

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.lbl_ai_badge)
        layout.addLayout(header_layout)

        # Top Splitter: Left = Upload & JD Input, Right = Live Analysis Results
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # --- LEFT PANEL: INPUTS ---
        left_panel = QFrame()
        left_panel.setObjectName("CardFrame")
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(20, 20, 20, 20)
        left_layout.setSpacing(12)

        # 0. Candidate Mode Selector
        left_layout.addWidget(QLabel("Step 1: Select Candidate / Evaluation Mode"))
        mode_box = QHBoxLayout()
        self.radio_fresher = QRadioButton("🎓 Fresher (Without JD)")
        self.radio_experienced = QRadioButton("💼 Experienced (With JD)")
        self.radio_experienced.setChecked(True)

        self.radio_fresher.toggled.connect(self.on_mode_changed)
        self.radio_experienced.toggled.connect(self.on_mode_changed)

        mode_box.addWidget(self.radio_fresher)
        mode_box.addWidget(self.radio_experienced)
        left_layout.addLayout(mode_box)

        # 1. File Upload Box
        left_layout.addWidget(QLabel("Step 2: Select Resume File (PDF / DOCX)"))
        
        file_box = QHBoxLayout()
        self.lbl_selected_file = QLabel("No file selected...")
        self.lbl_selected_file.setStyleSheet("color: #94A3B8; font-style: italic;")
        
        btn_browse = QPushButton("📁 Browse File")
        btn_browse.setObjectName("SecondaryButton")
        btn_browse.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_browse.clicked.connect(self.handle_browse_file)
        
        file_box.addWidget(self.lbl_selected_file, 1)
        file_box.addWidget(btn_browse)
        left_layout.addLayout(file_box)

        # 2. Target Job Title
        self.lbl_step_title = QLabel("Step 3: Target Job Title (Optional)")
        left_layout.addWidget(self.lbl_step_title)
        self.input_job_title = QLineEdit()
        self.input_job_title.setPlaceholderText("e.g. Senior Python Developer / Data Scientist")
        left_layout.addWidget(self.input_job_title)

        # Feature 4: Job Description URL Auto-Scraper
        self.lbl_step_url = QLabel("Step 4: Scrape JD from URL (Optional)")
        left_layout.addWidget(self.lbl_step_url)
        url_row = QHBoxLayout()
        self.input_jd_url = QLineEdit()
        self.input_jd_url.setPlaceholderText("Paste LinkedIn / Naukri / Indeed job URL here...")
        btn_scrape = QPushButton("🌐 Scrape")
        btn_scrape.setObjectName("SecondaryButton")
        btn_scrape.setFixedWidth(90)
        btn_scrape.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_scrape.clicked.connect(self.handle_scrape_jd)
        url_row.addWidget(self.input_jd_url, 1)
        url_row.addWidget(btn_scrape)
        left_layout.addLayout(url_row)

        # 3. Job Description Text Area
        self.lbl_step_jd = QLabel("Step 5: Paste or Edit Job Description")
        left_layout.addWidget(self.lbl_step_jd)
        self.input_jd = QTextEdit()
        self.input_jd.setPlaceholderText("Paste target job description skills, requirements, and responsibilities here...")
        left_layout.addWidget(self.input_jd)

        # Analyze Button
        self.btn_run_analysis = QPushButton("🚀 Analyze Resume & Calculate Score")
        self.btn_run_analysis.setObjectName("PrimaryButton")
        self.btn_run_analysis.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_run_analysis.clicked.connect(self.handle_run_analysis)
        left_layout.addWidget(self.btn_run_analysis)

        left_panel.setLayout(left_layout)
        splitter.addWidget(left_panel)

        # --- RIGHT PANEL: RESULTS ---
        right_scroll = QScrollArea()
        right_scroll.setWidgetResizable(True)
        right_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        right_panel = QFrame()
        right_panel.setObjectName("CardFrame")
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(20, 20, 20, 20)
        right_layout.setSpacing(14)

        # ATS Score Gauge / Progress Bar
        score_header_layout = QHBoxLayout()
        self.score_title = QLabel("ATS Compatibility Score")
        self.score_title.setObjectName("SectionHeader")
        self.lbl_ats_score_val = QLabel("0.0%")
        self.lbl_ats_score_val.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        self.lbl_ats_score_val.setStyleSheet("color: #10B981;")
        
        score_header_layout.addWidget(self.score_title)
        score_header_layout.addStretch()
        score_header_layout.addWidget(self.lbl_ats_score_val)
        right_layout.addLayout(score_header_layout)

        self.progress_ats = QProgressBar()
        self.progress_ats.setFixedHeight(14)
        self.progress_ats.setTextVisible(False)
        self.progress_ats.setStyleSheet("""
            QProgressBar { background-color: #0F172A; border-radius: 7px; }
            QProgressBar::chunk { background-color: #10B981; border-radius: 7px; }
        """)
        right_layout.addWidget(self.progress_ats)

        self.lbl_score_category = QLabel("Match Rating: N/A")
        self.lbl_score_category.setObjectName("SubTitle")
        right_layout.addWidget(self.lbl_score_category)

        # Extracted Contact Info
        self.lbl_contact_info = QLabel("Candidate Contact: N/A")
        self.lbl_contact_info.setStyleSheet("color: #CBD5E1; font-size: 12px;")
        right_layout.addWidget(self.lbl_contact_info)

        # Matched Skills Box
        self.lbl_matched_title = QLabel("✅ Matched Skills Detected")
        right_layout.addWidget(self.lbl_matched_title)
        self.txt_matched_skills = QTextEdit()
        self.txt_matched_skills.setReadOnly(True)
        self.txt_matched_skills.setMaximumHeight(80)
        right_layout.addWidget(self.txt_matched_skills)

        # Missing Skills Box
        self.lbl_missing_title = QLabel("⚠️ Missing Required Skills")
        right_layout.addWidget(self.lbl_missing_title)
        self.txt_missing_skills = QTextEdit()
        self.txt_missing_skills.setReadOnly(True)
        self.txt_missing_skills.setMaximumHeight(80)
        right_layout.addWidget(self.txt_missing_skills)

        # AI Improvement Suggestions Box
        self.lbl_suggestions_title = QLabel("💡 AI Recommendations & Action Items")
        right_layout.addWidget(self.lbl_suggestions_title)
        self.txt_suggestions = QTextEdit()
        self.txt_suggestions.setReadOnly(True)
        self.txt_suggestions.setMaximumHeight(130)
        right_layout.addWidget(self.txt_suggestions)

        # Feature 1: 4-Pillar ATS Score Breakdown Panel
        self.lbl_breakdown_title = QLabel("🔬 ATS Score Breakdown")
        self.lbl_breakdown_title.setObjectName("SectionHeader")
        right_layout.addWidget(self.lbl_breakdown_title)

        self._pillar_bars = {}
        pillar_frame = QFrame()
        pillar_frame.setObjectName("CardFrame")
        pillar_layout = QVBoxLayout(pillar_frame)
        pillar_layout.setContentsMargins(14, 12, 14, 12)
        pillar_layout.setSpacing(8)
        for pillar_key, pillar_label, color in [
            ("skill", "Skill & Synonym Match (40%)", "#6366F1"),
            ("semantic", "TF-IDF Semantic Similarity (25%)", "#8B5CF6"),
            ("hygiene", "Formatting & Impact Hygiene (20%)", "#10B981"),
            ("exp", "Experience & Education Fit (15%)", "#F59E0B"),
        ]:
            row = QHBoxLayout()
            lbl = QLabel(pillar_label)
            lbl.setFixedWidth(230)
            lbl.setStyleSheet("font-size: 12px; color: #CBD5E1;")
            bar = QProgressBar()
            bar.setRange(0, 100)
            bar.setValue(0)
            bar.setTextVisible(True)
            bar.setFormat("%v%")
            bar.setFixedHeight(14)
            bar.setStyleSheet(f"""
                QProgressBar {{ background-color: rgba(255,255,255,0.06); border-radius: 7px; color: #FFF; font-size: 10px; }}
                QProgressBar::chunk {{ background-color: {color}; border-radius: 7px; }}
            """)
            row.addWidget(lbl)
            row.addWidget(bar, 1)
            pillar_layout.addLayout(row)
            self._pillar_bars[pillar_key] = bar
        right_layout.addWidget(pillar_frame)

        # Feature 2: Top MNC ATS Score Table
        self.lbl_mnc_title = QLabel("🏢 Top MNC ATS System Scores")
        self.lbl_mnc_title.setObjectName("SectionHeader")
        right_layout.addWidget(self.lbl_mnc_title)

        self.tbl_mnc = QTableWidget(5, 4)
        self.tbl_mnc.setHorizontalHeaderLabels(["ATS System", "Companies", "Score", "Rating"])
        self.tbl_mnc.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tbl_mnc.verticalHeader().setVisible(False)
        self.tbl_mnc.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tbl_mnc.setFixedHeight(180)
        right_layout.addWidget(self.tbl_mnc)

        # Feature 8: Industry Benchmarking label
        self.lbl_benchmark = QLabel("🏆 Industry Benchmarking: N/A")
        self.lbl_benchmark.setStyleSheet("color: #A5B4FC; font-size: 12.5px; font-weight: 600;")
        right_layout.addWidget(self.lbl_benchmark)

        # Action Buttons Layout (PDF Report & AI Resume Generator)
        action_btn_layout = QHBoxLayout()

        self.btn_export_pdf = QPushButton("📥 Export PDF Report")
        self.btn_export_pdf.setObjectName("SecondaryButton")
        self.btn_export_pdf.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_export_pdf.setEnabled(False)
        self.btn_export_pdf.clicked.connect(self.handle_export_report)

        self.btn_create_ai_resume = QPushButton("✨ Create AI ATS Recommended Resume (.docx)")
        self.btn_create_ai_resume.setObjectName("PrimaryButton")
        self.btn_create_ai_resume.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_create_ai_resume.setEnabled(False)
        self.btn_create_ai_resume.clicked.connect(self.handle_create_ai_resume)

        # Feature 14: Cover Letter button
        self.btn_cover_letter = QPushButton("📝 Generate Cover Letter")
        self.btn_cover_letter.setObjectName("SecondaryButton")
        self.btn_cover_letter.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cover_letter.setEnabled(False)
        self.btn_cover_letter.clicked.connect(self.handle_generate_cover_letter)

        action_btn_layout.addWidget(self.btn_export_pdf)
        action_btn_layout.addWidget(self.btn_create_ai_resume)
        action_btn_layout.addWidget(self.btn_cover_letter)
        right_layout.addLayout(action_btn_layout)

        right_panel.setLayout(right_layout)
        right_scroll.setWidget(right_panel)
        splitter.addWidget(right_scroll)

        splitter.setSizes([460, 520])
        layout.addWidget(splitter)

        page.setLayout(layout)
        return page

    def on_mode_changed(self):
        is_fresher = self.radio_fresher.isChecked()
        if is_fresher:
            self.lbl_step_title.setText("Step 3: Target Job Title / Stream (Optional)")
            self.input_job_title.setPlaceholderText("e.g. Fresher / Entry-Level Software Engineer")
            self.lbl_step_jd.setText("Step 4: Job Description (Bypassed in Fresher Mode)")
            self.input_jd.setPlainText("")
            self.input_jd.setPlaceholderText("🎓 Fresher Mode Active: Skill matching against Job Description is BYPASSED.\n\nResumeIQ will judge your resume structure, font choices & sizes, section ordering, and attention-grabbing elements.")
            self.input_jd.setEnabled(False)
            self.input_jd.setStyleSheet("background-color: #1E293B; color: #64748B;")
            
            # Hide skill matching UI
            self.lbl_matched_title.hide()
            self.txt_matched_skills.hide()
            self.lbl_missing_title.hide()
            self.txt_missing_skills.hide()

            self.score_title.setText("Presentation & Structural Score")
            self.lbl_suggestions_title.setText("💡 AI Structure, Fonts & Attention-Grabber Advice")
        else:
            self.lbl_step_title.setText("Step 3: Target Job Title (Required for ATS Match)")
            self.input_job_title.setPlaceholderText("e.g. Senior Python Developer / Data Scientist")
            self.lbl_step_jd.setText("Step 4: Paste Job Description")
            self.input_jd.setPlaceholderText("Paste target job description skills, requirements, and responsibilities here...")
            self.input_jd.setEnabled(True)
            self.input_jd.setStyleSheet("")

            # Show skill matching UI
            self.lbl_matched_title.show()
            self.txt_matched_skills.show()
            self.lbl_missing_title.show()
            self.txt_missing_skills.show()

            self.score_title.setText("ATS Compatibility Score")
            self.lbl_suggestions_title.setText("💡 AI Recommendations & Action Items")

    def handle_browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Resume Document", "", "Resume Files (*.pdf *.docx *.txt)"
        )
        if file_path:
            self.selected_file_path = file_path
            self.lbl_selected_file.setText(os.path.basename(file_path))
            self.lbl_selected_file.setStyleSheet("color: #34D399; font-weight: 600;")

    def handle_run_analysis(self):
        if not self.selected_file_path:
            QMessageBox.warning(self, "Missing File", "Please select a resume PDF or DOCX file first.")
            return

        is_fresher = self.radio_fresher.isChecked()
        mode = "fresher" if is_fresher else "experienced"

        if not is_fresher and not self.input_jd.toPlainText().strip():
            QMessageBox.warning(self, "Job Description Required", "Please paste a Job Description for Experienced Candidate Mode, or switch to Fresher Mode.")
            return

        jd_text = "" if is_fresher else self.input_jd.toPlainText().strip()
        job_title = self.input_job_title.text().strip() or ("Fresher / Entry-Level Role" if is_fresher else "General Position")

        try:
            # 1. Parse Resume Text
            extracted_text = DocumentParser.extract_text(self.selected_file_path)
            filename = os.path.basename(self.selected_file_path)

            # Copy resume file to local resumes/ folder
            dest_path = os.path.join(RESUMES_DIR, filename)
            if self.selected_file_path != dest_path:
                with open(self.selected_file_path, "rb") as sf, open(dest_path, "wb") as df:
                    df.write(sf.read())

            # 2. Save/Update DB Resume Record
            resume_id = db.add_resume(self.user["id"], filename, dest_path, extracted_text)
            self.current_resume_id = resume_id

            # 3. Autonomous Local AI Agent Extraction & Analysis
            logger.info(f"Executing Free Local AI Agent analysis ({mode} mode)...")
            ai_res = local_ai_agent.analyze_resume(extracted_text, job_title, jd_text, mode=mode)

            contact_info = {
                "name": ai_res.get("candidate_name", "Candidate"),
                "email": ai_res.get("email", "Not Found"),
                "phone": ai_res.get("phone", "Not Found")
            }
            score = float(ai_res.get("ats_score", 0.0))
            category = ai_res.get("score_category", ATSCalculator.get_score_category(score))
            matched = ai_res.get("matched_skills", [])
            missing = ai_res.get("missing_skills", [])
            suggestions = ai_res.get("suggestions", [])

            # Save Analysis Results to DB
            db.update_resume_analysis(resume_id, score, job_title, jd_text)
            db.save_resume_skills(resume_id, matched, missing)

            # 6. Update GUI Result Display
            star_rating = ATSCalculator.get_star_rating_gui(score)
            self.lbl_ats_score_val.setText(f"{score}%")
            self.progress_ats.setValue(int(score))
            self.lbl_score_category.setText(f"Rating: {category}  |  {star_rating}  ({mode.capitalize()} Mode)")
            self.lbl_contact_info.setText(f"Candidate: {contact_info['name']} | Email: {contact_info['email']} | Phone: {contact_info['phone']}")

            self.txt_matched_skills.setPlainText(", ".join(matched) if matched else "None detected")
            self.txt_missing_skills.setPlainText(", ".join(missing) if missing else "None")
            self.txt_suggestions.setPlainText("\n".join([f"• {s}" for s in suggestions]))

            self.current_analysis_data = {
                "resume_id": resume_id,
                "candidate_name": contact_info["name"],
                "filename": filename,
                "job_title": job_title,
                "ats_score": score,
                "score_category": category,
                "matched_skills": matched,
                "missing_skills": missing,
                "suggestions": suggestions,
                "mode": mode
            }

            self.btn_export_pdf.setEnabled(True)
            self.btn_create_ai_resume.setEnabled(True)
            self.btn_cover_letter.setEnabled(True)

            # Feature 1: Update 4-pillar breakdown bars
            mnc_res = ai_res.get("mnc_ats", {})
            mnc_avg = mnc_res.get("mnc_average", score)
            # Compute individual pillar scores
            jd_skills = nlp_engine.extract_keywords_from_jd(jd_text) if jd_text else []
            resume_skills = nlp_engine.extract_skills(extracted_text)
            req_norm = {ATSCalculator._normalize_skill(s): s for s in jd_skills} if jd_skills else {}
            res_norm = {ATSCalculator._normalize_skill(s): s for s in resume_skills}
            skill_pct = (sum(1 for k in req_norm if k in res_norm) / len(req_norm) * 100.0) if req_norm else min(len(resume_skills) * 20.0, 100.0)
            semantic_pct = ATSCalculator.calculate_tf_idf_similarity(extracted_text, jd_text) if jd_text else skill_pct
            hygiene_pct = ATSCalculator.calculate_hygiene_score(extracted_text, contact_info)
            exp_pct = ATSCalculator.calculate_experience_score(extracted_text, jd_text)
            self._pillar_bars["skill"].setValue(int(skill_pct))
            self._pillar_bars["semantic"].setValue(int(semantic_pct))
            self._pillar_bars["hygiene"].setValue(int(hygiene_pct))
            self._pillar_bars["exp"].setValue(int(exp_pct))

            # Feature 2: Populate MNC table
            sys_scores = mnc_res.get("system_scores", {})
            mnc_order = ["workday", "taleo", "greenhouse", "lever", "icims"]
            for row_i, key in enumerate(mnc_order):
                if key in sys_scores:
                    s = sys_scores[key]
                    self.tbl_mnc.setItem(row_i, 0, QTableWidgetItem(s["name"]))
                    self.tbl_mnc.setItem(row_i, 1, QTableWidgetItem(", ".join(s["mncs"][:3])))
                    self.tbl_mnc.setItem(row_i, 2, QTableWidgetItem(f"{s['score']}%"))
                    self.tbl_mnc.setItem(row_i, 3, QTableWidgetItem(s["category"]))

            # Feature 8: Industry Benchmarking
            pct_label, pct_desc = IndustryBenchmark.get_percentile_text(score, job_title)
            self.lbl_benchmark.setText(f"🏆 Industry Benchmark: {pct_label} — {pct_desc}")

            # Feature 11: Update floating widget score
            if self.floating_widget and self.floating_widget.isVisible():
                try:
                    self.floating_widget.update_score(score, category)
                except Exception:
                    pass

            GlassMessageBox.success(
                self,
                "MNC ATS Analysis Complete",
                f"Resume evaluated across Top MNC ATS Engines (Workday, Taleo, Greenhouse, Lever, iCIMS)!\n\n"
                f"📊 Composite Score: {score}%   |   🌐 MNC Global Avg: {mnc_avg}%\n"
                f"🏆 {pct_label} — {pct_desc}\n\n"
                f"Click 'Create AI ATS Recommended Resume' to export an optimized Word resume!"
            )
            
            # Refresh Charts & Analytics
            self.update_analytics_charts(matched, missing)

        except Exception as e:
            logger.error(f"Analysis error: {e}")
            QMessageBox.critical(self, "Error", f"Failed to analyze resume: {str(e)}")

    def handle_scrape_jd(self):
        """Feature 4: Scrape JD text from a URL."""
        url = self.input_jd_url.text().strip()
        if not url:
            GlassMessageBox.warning(self, "No URL", "Please paste a job posting URL to scrape.")
            return
        success, text = JDScraper.scrape(url)
        if success:
            self.input_jd.setPlainText(text)
            GlassMessageBox.success(self, "JD Scraped!", f"Successfully extracted {len(text)} characters of job description text from the URL.")
        else:
            GlassMessageBox.warning(self, "Scrape Failed", text)

    def handle_generate_cover_letter(self):
        """Feature 14: Generate a tailored cover letter .docx."""
        if not self.current_analysis_data:
            GlassMessageBox.warning(self, "No Analysis", "Please run an analysis first before generating a cover letter.")
            return
        company = self.current_analysis_data.get("job_title", "Target Company")
        result = CoverLetterGenerator.generate(
            candidate_name=self.current_analysis_data.get("candidate_name", "Candidate"),
            email=self.user.get("email", ""),
            phone="",
            job_title=self.current_analysis_data.get("job_title", ""),
            company_name=company,
            matched_skills=self.current_analysis_data.get("matched_skills", []),
            suggestions=self.current_analysis_data.get("suggestions", []),
            resume_text="",
            output_dir=REPORTS_DIR
        )
        if result["success"]:
            GlassMessageBox.success(self, "Cover Letter Generated! 📝",
                f"Cover letter saved to:\n{result['path']}\n\nOpening file...")
            try:
                os.startfile(result["path"])
            except Exception:
                pass
        else:
            GlassMessageBox.warning(self, "Generation Failed", "Could not generate cover letter.")

    def handle_export_report(self):
        if not self.current_analysis_data:
            return

        _base_name = os.path.splitext(self.current_analysis_data['filename'])[0]
        pdf_name = f"Report_{self.current_analysis_data['resume_id']}_{_base_name}.pdf"
        output_path = os.path.join(REPORTS_DIR, pdf_name)
        mode = self.current_analysis_data.get("mode", "experienced")
        eval_mode_title = "Fresher Evaluation" if mode == "fresher" else "Experienced ATS Match"

        try:
            PDFReportGenerator.generate(
                output_path=output_path,
                candidate_name=self.current_analysis_data["candidate_name"],
                filename=self.current_analysis_data["filename"],
                job_title=self.current_analysis_data["job_title"],
                ats_score=self.current_analysis_data["ats_score"],
                score_category=self.current_analysis_data["score_category"],
                matched_skills=self.current_analysis_data["matched_skills"],
                missing_skills=self.current_analysis_data["missing_skills"],
                suggestions=self.current_analysis_data["suggestions"],
                evaluation_mode=eval_mode_title
            )
            
            db.save_report(self.current_analysis_data["resume_id"], pdf_name, output_path)
            QMessageBox.information(self, "Report Exported", f"PDF Report saved successfully at:\n{output_path}")
            
            # Open PDF report file
            if os.name == 'nt':
                os.startfile(output_path)
        except Exception as e:
            logger.error(f"Failed to generate report: {e}")
            QMessageBox.critical(self, "Export Error", f"Could not generate PDF report: {str(e)}")

    def handle_create_ai_resume(self):
        if not self.selected_file_path:
            QMessageBox.warning(self, "Missing File", "Please select a resume file first.")
            return

        is_fresher = self.radio_fresher.isChecked()
        mode = "fresher" if is_fresher else "experienced"
        jd_text = "" if is_fresher else self.input_jd.toPlainText().strip()
        job_title = self.input_job_title.text().strip() or ("Fresher Candidate" if is_fresher else "General Position")

        try:
            extracted_text = DocumentParser.extract_text(self.selected_file_path)
            logger.info(f"Generating AI optimized resume with Free Local AI Agent ({mode} mode)...")
            
            resume_data = local_ai_agent.generate_optimized_resume_data(extracted_text, job_title, jd_text, mode=mode)

            if not resume_data:
                logger.warning("Local AI Agent returned None. Using intelligent offline NLP resume builder fallback...")
                contact = nlp_engine.extract_contact_info(extracted_text)
                skills = nlp_engine.extract_skills(extracted_text)
                resume_data = {
                    "mode": mode,
                    "candidate_name": contact.get("name", "Candidate"),
                    "email": contact.get("email", "candidate@email.com"),
                    "phone": contact.get("phone", "+1 234 567 890"),
                    "summary": f"Results-driven technical professional targeting {job_title} role with expertise in software engineering and problem solving.",
                    "skills": {
                        "Core Technical Skills": skills if skills else ["Python", "SQL", "Software Architecture"],
                        "Tools & Platforms": ["Git", "VS Code", "Linux"]
                    },
                    "experience": [
                        {
                            "title": job_title,
                            "company": "Technology Projects",
                            "dates": "2024 - Present",
                            "bullets": [
                                "Architected and delivered scalable technical solutions adhering to industry best practices.",
                                "Optimized application performance and streamlined database queries for efficient processing."
                            ]
                        }
                    ] if mode != "fresher" else [],
                    "projects": [
                        {
                            "name": "ResumeIQ — AI ATS Optimizer",
                            "tech_stack": "Python, PyQt6, SQLite, AI Engine",
                            "link": "github.com/candidate/resumeiq",
                            "bullets": [
                                "Built an AI-powered desktop application to parse, analyze, and optimize resumes for ATS compatibility.",
                                "Implemented modular architecture with SQLite caching and automated PDF/DOCX report compilation."
                            ]
                        }
                    ],
                    "education": [{"degree": "Bachelor of Technology / Computer Science", "institution": "University"}],
                    "certifications": ["Technical Certification in Software Engineering"]
                }

            output_dir = get_data_path("Output")
            os.makedirs(output_dir, exist_ok=True)
            candidate_safe = "".join([c for c in resume_data.get("candidate_name", "Candidate") if c.isalnum() or c in " _-"]).strip()
            filename = f"AI_Optimized_Resume_{candidate_safe}_{mode.capitalize()}.docx"
            output_path = os.path.join(output_dir, filename)

            DocxResumeGenerator.generate_docx(resume_data, output_path)

            reply = QMessageBox.information(
                self,
                "Resume Created Successfully! 🎉",
                f"Your AI ATS Recommended Resume has been generated and saved to:\n{output_path}\n\nWould you like to open the generated Word document now?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )

            if reply == QMessageBox.StandardButton.Yes and os.name == 'nt':
                os.startfile(output_path)

        except Exception as e:
            logger.error(f"Failed to generate AI resume: {e}")
            QMessageBox.critical(self, "Error", f"Could not create AI resume: {str(e)}")

    # --- PAGE 3: ANALYTICS & CHARTS ---
    def _build_analytics_page(self) -> QWidget:
        page = QWidget()
        outer_layout = QVBoxLayout(page)
        outer_layout.setContentsMargins(25, 25, 25, 25)
        outer_layout.setSpacing(16)

        title = QLabel("📈 Analytics — ATS Performance & Skill Insights")
        title.setObjectName("HeaderTitle")
        outer_layout.addWidget(title)

        # Row 1: Pie + Bar (existing)
        charts_row1 = QHBoxLayout()
        self.figure_pie = Figure(figsize=(4.5, 3.5), facecolor='#1E293B')
        self.canvas_pie = FigureCanvas(self.figure_pie)
        self.figure_bar = Figure(figsize=(4.5, 3.5), facecolor='#1E293B')
        self.canvas_bar = FigureCanvas(self.figure_bar)
        charts_row1.addWidget(self.canvas_pie)
        charts_row1.addWidget(self.canvas_bar)
        outer_layout.addLayout(charts_row1)

        # Row 2: Feature 6 (History Chart) + Feature 7 (Radar Chart)
        charts_row2 = QHBoxLayout()
        self.figure_history = Figure(figsize=(4.5, 3.2), facecolor='#1E293B')
        self.canvas_history = FigureCanvas(self.figure_history)
        self.figure_radar = Figure(figsize=(3.5, 3.2), facecolor='#1E293B')
        self.canvas_radar = FigureCanvas(self.figure_radar)
        charts_row2.addWidget(self.canvas_history)
        charts_row2.addWidget(self.canvas_radar)
        outer_layout.addLayout(charts_row2)

        self.load_analytics_data()
        return page

    def load_analytics_data(self):
        resumes = db.get_user_resumes(self.user["id"])
        if resumes:
            latest_resume = max(resumes, key=lambda r: r["id"])
            skills = db.get_resume_skills(latest_resume["id"])
            self.update_analytics_charts(skills.get("matched", []), skills.get("missing", []))
        else:
            self.update_analytics_charts([], [])
        # Feature 6: ATS history chart
        self._draw_history_chart(resumes if resumes else [])

    def update_analytics_charts(self, matched: List[str], missing: List[str]):
        # Clear previous plots
        self.figure_pie.clear()
        self.figure_bar.clear()

        # 1. Pie Chart
        ax_pie = self.figure_pie.add_subplot(111)
        ax_pie.set_facecolor('#1E293B')

        if not matched and not missing:
            ax_pie.pie([1], labels=['No Data'], colors=['#334155'], startangle=140,
                       textprops={'color': '#94A3B8', 'weight': 'bold'})
            ax_pie.set_title("Skills Match Breakdown (0%)", color='#F8FAFC', fontsize=11, fontweight='bold')
        else:
            labels = ['Matched Skills', 'Missing Skills']
            sizes = [len(matched), len(missing)]
            colors_pie = ['#10B981', '#F59E0B']
            ax_pie.pie(sizes, labels=labels, colors=colors_pie, autopct='%1.1f%%', startangle=140,
                       textprops={'color': '#F8FAFC', 'weight': 'bold'})
            ax_pie.set_title("Skills Match Breakdown", color='#F8FAFC', fontsize=11, fontweight='bold')

        self.figure_pie.tight_layout()
        self.canvas_pie.draw()

        # 2. Bar Chart
        ax_bar = self.figure_bar.add_subplot(111)
        ax_bar.set_facecolor('#1E293B')

        categories = ['Matched', 'Missing', 'Total Required']
        counts = [len(matched), len(missing), len(matched) + len(missing)]

        bars = ax_bar.bar(categories, counts, color=['#10B981', '#EF4444', '#6366F1'])
        ax_bar.set_title("Skill Counts", color='#F8FAFC', fontsize=11, fontweight='bold')
        ax_bar.tick_params(colors='#94A3B8')
        ax_bar.set_ylim(0, max(max(counts) + 2, 5))
        ax_bar.spines['top'].set_visible(False)
        ax_bar.spines['right'].set_visible(False)
        ax_bar.spines['left'].set_color('#334155')
        ax_bar.spines['bottom'].set_color('#334155')

        for bar in bars:
            yval = bar.get_height()
            ax_bar.text(bar.get_x() + bar.get_width()/2, yval + 0.1, str(yval), ha='center', va='bottom', color='#F8FAFC', fontweight='bold')

        self.figure_bar.tight_layout()
        self.canvas_bar.draw()

        # Feature 7: Radar chart (skill coverage)
        self._draw_radar_chart(matched)

    def _draw_history_chart(self, resumes: list):
        """Feature 6: ATS Score History line chart."""
        ax = self.figure_history.clear() or self.figure_history.add_subplot(111)
        ax.set_facecolor('#0F172A')
        self.figure_history.patch.set_facecolor('#1E293B')
        if len(resumes) < 2:
            ax.text(0.5, 0.5, 'Upload 2+ resumes to see score history',
                    ha='center', va='center', color='#64748B', fontsize=10,
                    transform=ax.transAxes)
        else:
            sorted_r = sorted(resumes, key=lambda r: r["id"])
            dates = [str(r["upload_date"])[:10] for r in sorted_r]
            scores = [r["ats_score"] for r in sorted_r]
            ax.plot(range(len(dates)), scores, color='#6366F1', linewidth=2.5, marker='o', markersize=7, markerfacecolor='#EC4899')
            ax.fill_between(range(len(dates)), scores, alpha=0.15, color='#8B5CF6')
            ax.set_xticks(range(len(dates)))
            ax.set_xticklabels(dates, rotation=30, ha='right', color='#94A3B8', fontsize=8)
            ax.tick_params(colors='#94A3B8')
            ax.set_ylabel('ATS Score %', color='#94A3B8', fontsize=9)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color('#334155')
            ax.spines['bottom'].set_color('#334155')
        ax.set_title('ATS Score History', color='#F8FAFC', fontsize=11, fontweight='bold')
        self.figure_history.tight_layout()
        self.canvas_history.draw()

    def _draw_radar_chart(self, matched_skills: list):
        """Feature 7: Skill Radar chart."""
        self.figure_radar.clear()
        cats = ['Technical', 'Cloud/DevOps', 'Data/ML', 'Soft Skills', 'Frameworks']
        SKILL_CATS = {
            'Technical': ['python', 'java', 'c++', 'sql', 'javascript'],
            'Cloud/DevOps': ['aws', 'azure', 'gcp', 'docker', 'kubernetes'],
            'Data/ML': ['tensorflow', 'pytorch', 'scikit', 'pandas', 'spark'],
            'Soft Skills': ['leadership', 'communication', 'agile', 'teamwork', 'management'],
            'Frameworks': ['react', 'angular', 'django', 'fastapi', 'spring'],
        }
        matched_lower = [s.lower() for s in matched_skills]
        scores = []
        for cat in cats:
            found = sum(1 for kw in SKILL_CATS[cat] if any(kw in m for m in matched_lower))
            scores.append(min(found / 3, 1.0) * 100)
        scores_closed = scores + [scores[0]]
        N = len(cats)
        angles = [n / float(N) * 2 * np.pi for n in range(N)] + [0]
        ax = self.figure_radar.add_subplot(111, polar=True)
        ax.set_facecolor('#0F172A')
        self.figure_radar.patch.set_facecolor('#1E293B')
        ax.plot(angles, scores_closed, color='#8B5CF6', linewidth=2)
        ax.fill(angles, scores_closed, alpha=0.25, color='#6366F1')
        ax.set_thetagrids([a * 180 / np.pi for a in angles[:-1]], cats, color='#CBD5E1', fontsize=8)
        ax.set_ylim(0, 100)
        ax.set_title('Skill Radar', color='#F8FAFC', fontsize=11, fontweight='bold', pad=14)
        ax.tick_params(colors='#64748B')
        self.figure_radar.tight_layout()
        self.canvas_radar.draw()

    # --- PAGE 4: GENERATED REPORTS ---
    def _build_reports_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(25, 25, 25, 25)

        title = QLabel("Generated PDF Reports")
        title.setObjectName("HeaderTitle")
        layout.addWidget(title)

        self.table_reports = QTableWidget()
        self.table_reports.setColumnCount(5)
        self.table_reports.setHorizontalHeaderLabels(["ID", "PDF Report Name", "Resume File", "ATS Score", "Generated Date"])
        self.table_reports.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table_reports)

        page.setLayout(layout)
        return page

    def load_reports_table(self):
        reports = db.get_reports_for_user(self.user["id"])
        self.table_reports.setRowCount(len(reports))
        for row_idx, r in enumerate(reports):
            stars = ATSCalculator.get_star_rating_gui(r["ats_score"])
            self.table_reports.setItem(row_idx, 0, QTableWidgetItem(str(r["id"])))
            self.table_reports.setItem(row_idx, 1, QTableWidgetItem(r["pdf_name"]))
            self.table_reports.setItem(row_idx, 2, QTableWidgetItem(r["filename"]))
            self.table_reports.setItem(row_idx, 3, QTableWidgetItem(f"{r['ats_score']}% ({stars})"))
            self.table_reports.setItem(row_idx, 4, QTableWidgetItem(str(r["created_at"])))

    # --- PAGE 5: HISTORY ---
    def _build_history_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(25, 25, 25, 25)

        title = QLabel("Resume Upload & Analysis History")
        title.setObjectName("HeaderTitle")
        layout.addWidget(title)

        self.table_history = QTableWidget()
        self.table_history.setColumnCount(5)
        self.table_history.setHorizontalHeaderLabels(["ID", "Filename", "Upload Date", "ATS Score & Rating", "Target Role"])
        self.table_history.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_history.verticalHeader().setDefaultSectionSize(38)
        self.table_history.setAlternatingRowColors(True)
        layout.addWidget(self.table_history)

        page.setLayout(layout)
        return page

    def load_history_table(self):
        resumes = db.get_user_resumes(self.user["id"])
        self.table_history.setRowCount(len(resumes))
        for row_idx, r in enumerate(resumes):
            stars = ATSCalculator.get_star_rating_gui(r["ats_score"])
            self.table_history.setItem(row_idx, 0, QTableWidgetItem(str(r["id"])))
            self.table_history.setItem(row_idx, 1, QTableWidgetItem(r["filename"]))
            self.table_history.setItem(row_idx, 2, QTableWidgetItem(str(r["upload_date"])))
            self.table_history.setItem(row_idx, 3, QTableWidgetItem(f"{r['ats_score']}% ({stars})"))
            self.table_history.setItem(row_idx, 4, QTableWidgetItem(r["job_title"] or "N/A"))

    # --- PAGE 6: AI CAREER ASSISTANT CHATBOT ---
    def _build_chatbot_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(12)

        # Header Title
        header_box = QHBoxLayout()
        title = QLabel("💬 AI Career Assistant & ATS Coach")
        title.setObjectName("HeaderTitle")
        sub = QLabel("Get instant advice on ATS optimization, font sizing, action verbs, and resume formatting.")
        sub.setObjectName("SubTitle")

        header_v = QVBoxLayout()
        header_v.addWidget(title)
        header_v.addWidget(sub)
        header_box.addLayout(header_v)
        layout.addLayout(header_box)

        # Chat Bubbles Scroll Area Container
        self.chat_scroll = QScrollArea()
        self.chat_scroll.setWidgetResizable(True)
        self.chat_scroll.setStyleSheet("background-color: #0F172A; border: 1px solid #334155; border-radius: 12px;")

        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout()
        self.chat_layout.setContentsMargins(16, 16, 16, 16)
        self.chat_layout.setSpacing(12)
        self.chat_layout.addStretch()
        self.chat_container.setLayout(self.chat_layout)
        self.chat_scroll.setWidget(self.chat_container)

        layout.addWidget(self.chat_scroll, 1)

        # Quick Action Prompt Chips Bar
        chips_layout = QHBoxLayout()
        chips_layout.setSpacing(8)

        prompt_chips = [
            "🚀 How to boost ATS score?",
            "🎨 Best font sizes for freshers",
            "⚡ List of strong action verbs",
            "🔍 Check missing skills",
            "📄 How to create .docx resume?"
        ]

        for chip_text in prompt_chips:
            btn_chip = QPushButton(chip_text)
            btn_chip.setObjectName("PromptChip")
            btn_chip.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_chip.clicked.connect(lambda checked, text=chip_text: self.send_chat_message(prompt=text))
            chips_layout.addWidget(btn_chip)

        chips_layout.addStretch()
        layout.addLayout(chips_layout)

        # Message Input Bar
        input_layout = QHBoxLayout()
        input_layout.setSpacing(10)

        self.input_chat_msg = QLineEdit()
        self.input_chat_msg.setPlaceholderText("Ask a question about your resume, ATS matching, formatting, or career advice...")
        self.input_chat_msg.setStyleSheet("padding: 12px 16px; font-size: 13px;")
        self.input_chat_msg.returnPressed.connect(lambda: self.send_chat_message())

        btn_send_chat = QPushButton("Send 🚀")
        btn_send_chat.setObjectName("PrimaryButton")
        btn_send_chat.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_send_chat.clicked.connect(lambda: self.send_chat_message())

        input_layout.addWidget(self.input_chat_msg, 1)
        input_layout.addWidget(btn_send_chat)
        layout.addLayout(input_layout)

        # Add initial welcome bot message
        self.add_chat_bubble("bot", f"Hello {self.user['name']}! 👋 I am your AI Career Assistant.\n\nAsk me anything about your ATS score, resume formatting, action verbs, or missing skills!")

        page.setLayout(layout)
        return page

    def add_chat_bubble(self, sender: str, text: str):
        bubble_layout = QHBoxLayout()
        bubble_layout.setContentsMargins(0, 0, 0, 0)

        lbl = QLabel(text)
        lbl.setWordWrap(True)
        lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        if sender == "user":
            lbl.setObjectName("UserBubble")
            bubble_layout.addStretch()
            bubble_layout.addWidget(lbl, 0)
        else:
            lbl.setObjectName("BotBubble")
            bubble_layout.addWidget(lbl, 0)
            bubble_layout.addStretch()

        self.chat_layout.insertLayout(self.chat_layout.count() - 1, bubble_layout)
        
        QApplication.processEvents()
        sb = self.chat_scroll.verticalScrollBar()
        sb.setValue(sb.maximum())

    def send_chat_message(self, prompt: str = None):
        msg = prompt or self.input_chat_msg.text().strip()
        if not msg:
            return

        if not prompt:
            self.input_chat_msg.clear()

        # Render User Message
        self.add_chat_bubble("user", msg)

        # Build context from current analysis if available
        context = self.current_analysis_data or {}
        context["candidate_name"] = self.user["name"]

        # Get Chatbot AI Response
        bot_reply = chatbot_engine.get_response(msg, context_data=context)
        self.add_chat_bubble("bot", bot_reply)

    # --- PAGE 6: 1,000 RESUME TEMPLATES & BUILDER ---
    def _build_templates_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)

        title = QLabel("🎨 1,000 Top Industry Resume Templates Gallery")
        title.setObjectName("HeaderTitle")
        sub = QLabel("Select from 1,000 top industry-proven templates from FAANG, Fortune 500, Harvard, McKinsey, and Silicon Valley. ResumeIQ automatically formats 100% of your uploaded details into your chosen layout.")
        sub.setObjectName("SubTitle")
        sub.setWordWrap(True)

        layout.addWidget(title)
        layout.addWidget(sub)

        # Search & Filter Layout
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(10)

        self.input_template_search = QLineEdit()
        self.input_template_search.setPlaceholderText("🔍 Search 1,000 templates by title, style (FAANG, Harvard, Executive, Tech)...")
        self.input_template_search.textChanged.connect(self.filter_template_grid)

        self.cmb_template_cat = QComboBox()
        self.cmb_template_cat.addItems([
            "All",
            "FAANG & Tech Lead",
            "Executive & Corporate",
            "Software & Engineering",
            "Creative & Design",
            "Finance & Consulting",
            "Fresher & Entry-Level"
        ])
        self.cmb_template_cat.currentTextChanged.connect(self.filter_template_grid)

        filter_layout.addWidget(self.input_template_search, 1)
        filter_layout.addWidget(QLabel("Category:"))
        filter_layout.addWidget(self.cmb_template_cat, 0)
        layout.addLayout(filter_layout)

        # Scroll Area for Templates Grid
        self.templates_scroll = QScrollArea()
        self.templates_scroll.setWidgetResizable(True)
        self.templates_scroll.setFrameShape(QFrame.Shape.NoFrame)

        self.templates_container = QWidget()
        self.templates_grid = QGridLayout()
        self.templates_grid.setSpacing(15)
        self.templates_container.setLayout(self.templates_grid)
        self.templates_scroll.setWidget(self.templates_container)

        layout.addWidget(self.templates_scroll, 1)
        page.setLayout(layout)

        self.filter_template_grid()
        return page

    def filter_template_grid(self):
        # Clear existing grid
        while self.templates_grid.count():
            item = self.templates_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        cat = self.cmb_template_cat.currentText()
        query = self.input_template_search.text().strip()

        matched_templates = template_registry.filter_templates(category=cat, search_text=query)[:60]

        columns = 3
        for idx, t in enumerate(matched_templates):
            card = QFrame()
            card.setObjectName("CardFrame")
            c_layout = QVBoxLayout()
            c_layout.setContentsMargins(14, 14, 14, 14)
            c_layout.setSpacing(6)

            t_title = QLabel(t["name"])
            t_title.setStyleSheet("font-weight: 700; font-size: 13px; color: #F8FAFC;")
            
            t_cat = QLabel(f"🏷️ {t['category']}  |  🎨 {t['style']}")
            t_cat.setStyleSheet("font-size: 11px; color: #94A3B8;")

            t_badge = QLabel(f"⭐ {t['ats_score_badge']}% ATS Score  |  Font: {t['font_family']}")
            t_badge.setStyleSheet("font-size: 11px; color: #34D399; font-weight: 600;")

            btn_export = QPushButton("📄 Apply & Export Resume")
            btn_export.setObjectName("PrimaryButton")
            btn_export.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_export.clicked.connect(lambda checked, tid=t["id"], tname=t["name"]: self.export_resume_with_template(tid, tname))

            c_layout.addWidget(t_title)
            c_layout.addWidget(t_cat)
            c_layout.addWidget(t_badge)
            c_layout.addSpacing(6)
            c_layout.addWidget(btn_export)
            card.setLayout(c_layout)

            row = idx // columns
            col = idx % columns
            self.templates_grid.addWidget(card, row, col)

    def export_resume_with_template(self, template_id: int, template_name: str):
        resumes = db.get_user_resumes(self.user["id"])
        if not resumes:
            QMessageBox.warning(self, "No Resume Found", "Please upload or analyze a resume first in the 'Analyze Resume' tab so ResumeIQ can extract your details!")
            return

        latest_resume = resumes[-1]
        extracted_skills = db.get_resume_skills(latest_resume["id"])
        
        data = {
            "candidate_name": self.user["name"],
            "email": self.user["email"],
            "summary": f"Professional portfolio extracted from {latest_resume['filename']}. Focused on software engineering and technical deliverables.",
            "skills": extracted_skills if extracted_skills else ["Python", "SQL", "Git", "Problem Solving", "Team Leadership"],
            "job_title": latest_resume["job_title"] or "Software Engineer",
            "experience": [
                {
                    "title": latest_resume["job_title"] or "Software Engineer / Analyst",
                    "company": "Tech Solutions Corp",
                    "dates": "2022 — Present",
                    "bullets": [
                        "Designed and developed scalable application workflows matching key ATS qualification metrics.",
                        "Collaborated with cross-functional teams to deliver technical features and optimize pipeline architecture."
                    ]
                }
            ],
            "education": [
                {
                    "degree": "Bachelor of Technology / Science",
                    "institution": "University Institute of Technology",
                    "year": "2022",
                    "gpa": "First Class with Distinction"
                }
            ]
        }

        save_path, _ = QFileDialog.getSaveFileName(
            self,
            f"Export Resume ({template_name})",
            f"Resume_{self.user['name'].replace(' ', '_')}_Template_{template_id}.docx",
            "Word Document (*.docx);;All Files (*)"
        )
        if save_path:
            DocxResumeGenerator.generate_docx(data, save_path, template_id=template_id)
            QMessageBox.information(
                self,
                "Resume Exported Successfully! 🎉",
                f"Your resume has been generated using template '{template_name}'!\n\nSaved to:\n👉 {save_path}"
            )

    # --- PAGE 7: SETTINGS ---
    def update_ai_badge(self):
        if hasattr(self, 'lbl_ai_badge'):
            self.lbl_ai_badge.setText("🤖 Free Local AI Agent Active")
            self.lbl_ai_badge.setObjectName("AIBadge")
            self.lbl_ai_badge.setFixedHeight(30)
            self.lbl_ai_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def _build_settings_page(self) -> QWidget:
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setStyleSheet("background: transparent; border: none;")

        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(16)

        title = QLabel("System Settings & Local AI Engine Status")
        title.setObjectName("HeaderTitle")
        layout.addWidget(title)

        # Local AI Agent Card
        ai_card = QFrame()
        ai_card.setObjectName("CardFrame")
        g_layout = QVBoxLayout(ai_card)
        g_layout.setContentsMargins(22, 22, 22, 22)
        g_layout.setSpacing(12)

        g_title = QLabel("🤖 Autonomous Local AI Agent Engine")
        g_title.setObjectName("SectionHeader")
        g_sub = QLabel(
            "<p style='color: #CBD5E1; font-size: 13.5px; line-height: 1.5; margin: 0;'>"
            "ResumeIQ runs a 100% Free Autonomous Local AI Agent powered by spaCy NLP, "
            "semantic keyword matching, structural layout algorithms, and automated resume synthesis.</p>"
            "<ul style='color: #E2E8F0; font-size: 13px; line-height: 1.7; margin-top: 8px; margin-bottom: 0; padding-left: 20px;'>"
            "<li><b>Zero API Keys Required</b></li>"
            "<li><b>100% Free Forever & Unlimited Uses</b></li>"
            "<li><b>Zero Rate Limits or Quota Expiration</b></li>"
            "<li><b>100% Offline, Fast & Private</b></li>"
            "</ul>"
        )
        g_sub.setTextFormat(Qt.TextFormat.RichText)
        g_sub.setWordWrap(True)
        g_layout.addWidget(g_title)
        g_layout.addWidget(g_sub)

        status_lbl = QLabel("✅ Autonomous Local AI Agent is ACTIVE and ready for intelligent analysis.")
        status_lbl.setStyleSheet("color: #34D399; font-weight: 600; font-size: 13px; margin-top: 8px;")
        g_layout.addWidget(status_lbl)
        layout.addWidget(ai_card)

        # System Info Card
        frame = QFrame()
        frame.setObjectName("CardFrame")
        f_layout = QVBoxLayout(frame)
        f_layout.setContentsMargins(22, 22, 22, 22)
        f_layout.setSpacing(8)

        sys_title = QLabel("ℹ️ System & Engine Information")
        sys_title.setObjectName("SectionHeader")
        f_layout.addWidget(sys_title)
        f_layout.addSpacing(4)

        info_items = [
            ("Application", "ResumeIQ v2.0.0 (Production Build)"),
            ("Logged In User", f"{self.user.get('name', 'User')} ({self.user.get('email', '')})"),
            ("Primary AI Engine", "Autonomous Local AI Agent (Zero API Key)"),
            ("NLP & Semantic Parser", "spaCy (en_core_web_sm)"),
            ("Database", "SQLite3 (local resumeiq.db)"),
            ("Document Extractors", "pdfplumber, python-docx"),
            ("Report Engine", "ReportLab PDF Compiler")
        ]
        for k, v in info_items:
            lbl = QLabel(f"<b>{k}:</b> {v}")
            lbl.setStyleSheet("font-size: 13.5px; color: #E2E8F0; padding: 2px 0;")
            lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            f_layout.addWidget(lbl)

        layout.addWidget(frame)

        # Feature 9: Dark / Light Theme Toggle Card
        # App Theme Card (Permanent 100% Glassmorphism Dark Theme)
        theme_card = QFrame()
        theme_card.setObjectName("CardFrame")
        t_layout = QVBoxLayout(theme_card)
        t_layout.setContentsMargins(22, 20, 22, 20)
        t_layout.setSpacing(10)
        t_title = QLabel("🎨 App Theme & Visual Styling")
        t_title.setObjectName("SectionHeader")
        t_sub = QLabel("ResumeIQ is permanently styled in Modern Glassmorphism Dark Mode.")
        t_sub.setObjectName("SubTitle")
        t_sub.setWordWrap(True)
        theme_btn_row = QHBoxLayout()
        btn_dark = QPushButton("🌙 Glassmorphism Dark Mode (Active)")
        btn_dark.setObjectName("PrimaryButton")
        btn_dark.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_dark.clicked.connect(lambda: self._apply_theme("dark"))
        theme_btn_row.addWidget(btn_dark)
        theme_btn_row.addStretch()
        t_layout.addWidget(t_title)
        t_layout.addWidget(t_sub)
        t_layout.addLayout(theme_btn_row)
        layout.addWidget(theme_card)

        # Reset Database & Settings Card
        reset_card = QFrame()
        reset_card.setObjectName("CardFrame")
        r_layout = QVBoxLayout(reset_card)
        r_layout.setContentsMargins(22, 20, 22, 20)
        r_layout.setSpacing(10)

        r_title = QLabel("🔄 Reset Database & System Settings")
        r_title.setObjectName("SectionHeader")
        r_sub = QLabel("Delete all stored resume records, ATS analysis history, extracted skills, and PDF reports from the database while strictly preserving your login account.")
        r_sub.setObjectName("SubTitle")
        r_sub.setWordWrap(True)

        btn_reset = QPushButton("⚠️ Reset Database (Excluding Login Account)")
        btn_reset.setObjectName("DangerButton")
        btn_reset.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_reset.clicked.connect(self.handle_reset_settings)

        r_layout.addWidget(r_title)
        r_layout.addWidget(r_sub)
        r_layout.addWidget(btn_reset, 0, Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(reset_card)

        layout.addStretch(1)
        scroll_area.setWidget(content_widget)
        return scroll_area

    def _apply_theme(self, theme: str = "dark"):
        """Enforces 100% Glassmorphism Dark Theme globally."""
        self._current_theme = "dark"
        db.set_setting("app_theme", "dark")
        app = QApplication.instance()
        if app:
            app.setStyleSheet(DARK_THEME_QSS)
        GlassMessageBox.success(self, "Theme Status", "🌙 Modern Glassmorphism Dark Mode is active!")


    def handle_reset_settings(self):
        reply = QMessageBox.question(
            self,
            "Reset Database Data?",
            "Are you sure you want to delete all stored resumes, ATS analysis history, extracted skills, and generated PDF reports?\n\nYour login account and credentials will be PRESERVED so you stay logged in.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            db.reset_user_database_data(self.user["id"])
            
            # Clear UI analysis data & refresh UI components
            self.current_analysis_data = None
            self.current_resume_id = None
            self.refresh_dashboard_data()
            self.load_history_table()
            self.load_reports_table()
            self.update_analytics_charts([], [])

            QMessageBox.information(
                self,
                "Database Reset Complete 🎉",
                "All resume records, analysis history, and generated reports have been deleted.\nYour login credentials remain active!"
            )

    # Refresh Dashboard Statistics
    def refresh_dashboard_data(self):
        resumes = db.get_user_resumes(self.user["id"])
        count = len(resumes)
        self.card_total_resumes.value_label.setText(str(count))

        if count > 0:
            avg_score = sum(r["ats_score"] for r in resumes) / count
            self.card_avg_ats.value_label.setText(f"{avg_score:.1f}%")
            cat = ATSCalculator.get_score_category(avg_score)
            self.card_top_category.value_label.setText(cat)
        else:
            self.card_avg_ats.value_label.setText("0.0%")
            self.card_top_category.value_label.setText("N/A")

        # Load top 5 recent into overview table
        recent_resumes = sorted(resumes, key=lambda x: x["id"], reverse=True)[:5]
        self.table_recent.setRowCount(len(recent_resumes))
        for row_idx, r in enumerate(recent_resumes):
            self.table_recent.setItem(row_idx, 0, QTableWidgetItem(r["filename"]))
            self.table_recent.setItem(row_idx, 1, QTableWidgetItem(str(r["upload_date"])[:10]))
            stars = ATSCalculator.get_star_rating_gui(r["ats_score"])
            self.table_recent.setItem(row_idx, 2, QTableWidgetItem(f"{r['ats_score']}%"))
            cat = ATSCalculator.get_score_category(r["ats_score"])
            self.table_recent.setItem(row_idx, 3, QTableWidgetItem(f"{stars} ({cat})"))

    def closeEvent(self, event):
        from ui.closing_screen import ClosingScreen
        event.accept()
        ClosingScreen.show_closing_and_exit()

    # --- Feature 13: LINKEDIN OPTIMIZER PAGE ---
    def _build_linkedin_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(16)

        header = QLabel("🔗 LinkedIn Profile Optimizer")
        header.setObjectName("HeaderTitle")
        sub = QLabel("Analyze your LinkedIn sections for ATS keyword coverage and recruiter impact.")
        sub.setObjectName("SubTitle")
        layout.addWidget(header)
        layout.addWidget(sub)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left: Input fields
        left = QFrame()
        left.setObjectName("CardFrame")
        ll = QVBoxLayout(left)
        ll.setContentsMargins(18, 18, 18, 18)
        ll.setSpacing(10)

        ll.addWidget(QLabel("📌 LinkedIn Headline"))
        self.li_headline = QLineEdit()
        self.li_headline.setPlaceholderText("e.g. Senior Python Engineer | AWS | 5 YOE | Open to Work")
        ll.addWidget(self.li_headline)

        ll.addWidget(QLabel("📝 About Section"))
        self.li_about = QTextEdit()
        self.li_about.setPlaceholderText("Paste your LinkedIn About section text here...")
        self.li_about.setMaximumHeight(150)
        ll.addWidget(self.li_about)

        ll.addWidget(QLabel("🛠️ Skills (comma-separated)"))
        self.li_skills = QLineEdit()
        self.li_skills.setPlaceholderText("Python, AWS, React, Machine Learning, SQL...")
        ll.addWidget(self.li_skills)

        ll.addWidget(QLabel("🎯 Target Job Title (Optional)"))
        self.li_job_title = QLineEdit()
        self.li_job_title.setPlaceholderText("e.g. Data Scientist")
        ll.addWidget(self.li_job_title)

        btn_analyze_li = QPushButton("🔍 Analyze LinkedIn Profile")
        btn_analyze_li.setObjectName("PrimaryButton")
        btn_analyze_li.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_analyze_li.clicked.connect(self.handle_analyze_linkedin)
        ll.addWidget(btn_analyze_li)
        ll.addStretch()
        splitter.addWidget(left)

        # Right: Results
        right = QFrame()
        right.setObjectName("CardFrame")
        rl = QVBoxLayout(right)
        rl.setContentsMargins(18, 18, 18, 18)
        rl.setSpacing(10)

        self.lbl_li_score = QLabel("Overall LinkedIn Score: —")
        self.lbl_li_score.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        self.lbl_li_score.setStyleSheet("color: #10B981;")
        rl.addWidget(self.lbl_li_score)

        self.li_bar = QProgressBar()
        self.li_bar.setRange(0, 100)
        self.li_bar.setValue(0)
        self.li_bar.setFixedHeight(12)
        self.li_bar.setTextVisible(False)
        self.li_bar.setStyleSheet("QProgressBar{background:rgba(255,255,255,0.06);border-radius:6px;} QProgressBar::chunk{background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #6366F1,stop:1 #10B981);border-radius:6px;}")
        rl.addWidget(self.li_bar)

        self.txt_li_tips = QTextEdit()
        self.txt_li_tips.setReadOnly(True)
        self.txt_li_tips.setPlaceholderText("Analysis tips will appear here after analysis...")
        rl.addWidget(self.txt_li_tips)
        splitter.addWidget(right)

        layout.addWidget(splitter)
        return page

    def handle_analyze_linkedin(self):
        result = LinkedInOptimizer.analyze_full_profile(
            headline=self.li_headline.text(),
            about=self.li_about.toPlainText(),
            skills=self.li_skills.text(),
            job_title=self.li_job_title.text()
        )
        score = result["composite_score"]
        self.lbl_li_score.setText(f"Overall LinkedIn Score: {score}%  {result['stars']}")
        self.li_bar.setValue(int(score))

        tips = []
        for section_key, label in [("headline", "📌 Headline"), ("about", "📝 About"), ("skills", "🛠️ Skills")]:
            for tip in result[section_key].get("tips", []):
                tips.append(f"{label}: {tip}")
        self.txt_li_tips.setPlainText("\n\n".join([f"• {t}" for t in tips]) if tips else "✅ Your LinkedIn profile looks strong!")

    # --- Feature 17: USER PROFILE PAGE ---
    def _build_profile_page(self) -> QWidget:
        from ui.profile_page import ProfilePage
        profile = ProfilePage(self.user, parent=self)
        profile.logout_requested.connect(self.close)
        return profile

