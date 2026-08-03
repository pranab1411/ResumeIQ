# UI Style Tokens & Glassmorphism QSS Stylesheet for ResumeIQ
import os
from utils.paths import get_data_path

# Ensure SVG checkmark asset exists
CHECK_ICON_PATH = os.path.abspath(get_data_path("assets", "check.svg")).replace("\\", "/")
if not os.path.exists(CHECK_ICON_PATH):
    os.makedirs(os.path.dirname(CHECK_ICON_PATH), exist_ok=True)
    with open(CHECK_ICON_PATH, "w", encoding="utf-8") as f:
        f.write('<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>')

DARK_THEME_QSS = f"""
/* Global Base & Glassmorphism Mesh Background */
QWidget {{
    background: transparent;
    color: #F8FAFC;
    font-family: 'Segoe UI', 'SF Pro Display', Roboto, sans-serif;
    font-size: 13px;
}}

QMainWindow, QWidget#MainRoot {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0B0819, stop:0.4 #161233, stop:0.8 #1E1038, stop:1 #281246);
}}

/* Frosted Glass Panels & Containers */
QFrame#CardFrame, QFrame.card {{
    background-color: rgba(28, 25, 58, 0.65);
    border: 1px solid rgba(255, 255, 255, 0.14);
    border-radius: 18px;
}}

QFrame#GlassCard {{
    background-color: rgba(35, 30, 70, 0.65);
    border: 1px solid rgba(255, 255, 255, 0.18);
    border-radius: 20px;
}}

QFrame#KPICard {{
    background-color: rgba(30, 27, 62, 0.70);
    border: 1px solid rgba(255, 255, 255, 0.16);
    border-radius: 18px;
}}

/* Sidebar Glass Container */
QFrame#Sidebar {{
    background-color: rgba(18, 15, 38, 0.75);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 20px;
    margin: 8px;
}}

/* Navigation Items */
QPushButton#NavButton {{
    background-color: transparent;
    color: #A5B4FC;
    border: none;
    border-radius: 12px;
    padding: 12px 18px;
    text-align: left;
    font-weight: 600;
    font-size: 14px;
}}

QPushButton#NavButton:hover {{
    background-color: rgba(255, 255, 255, 0.08);
    color: #FFFFFF;
}}

QPushButton#NavButton:checked, QPushButton#NavButton[active="true"] {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 rgba(99, 102, 241, 0.5), stop:1 rgba(168, 85, 247, 0.5));
    color: #FFFFFF;
    border: 1px solid rgba(255, 255, 255, 0.25);
}}

/* Inputs & Text Fields */
QLineEdit, QTextEdit, QPlainTextEdit, QComboBox {{
    background-color: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.16);
    border-radius: 10px;
    padding: 5px 14px;
    min-height: 28px;
    font-size: 14.5px;
    font-weight: 500;
    color: #FFFFFF;
    selection-background-color: #8B5CF6;
}}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QComboBox:focus {{
    border: 1.5px solid #C084FC;
    background-color: rgba(255, 255, 255, 0.10);
}}

QComboBox::drop-down {{
    border: none;
    padding-right: 10px;
}}

QComboBox QAbstractItemView {{
    background-color: #1A1635;
    border: 1px solid rgba(255, 255, 255, 0.2);
    selection-background-color: #8B5CF6;
    color: #FFFFFF;
    border-radius: 8px;
}}

/* Password Eye Button */
QPushButton#IconButton, QPushButton#btn_toggle_pw {{
    background-color: rgba(255, 255, 255, 0.08);
    color: #A5B4FC;
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 10px;
    font-size: 15px;
    padding: 4px;
    min-height: 28px;
}}

QPushButton#IconButton:hover, QPushButton#btn_toggle_pw:hover {{
    background-color: rgba(255, 255, 255, 0.15);
    color: #FFFFFF;
    border-color: #C084FC;
}}

/* Checkboxes */
QCheckBox {{
    color: #E2E8F0;
    font-size: 13.5px;
    font-weight: 500;
    spacing: 8px;
}}

QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border: 1px solid rgba(255, 255, 255, 0.25);
    border-radius: 5px;
    background-color: rgba(255, 255, 255, 0.06);
}}

QCheckBox::indicator:hover {{
    border-color: #A855F7;
}}

QCheckBox::indicator:checked {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6366F1, stop:1 #A855F7);
    border-color: #C084FC;
    image: url("{CHECK_ICON_PATH}");
}}

/* Radio Buttons */
QRadioButton {{
    color: #E2E8F0;
    font-weight: 500;
    spacing: 8px;
}}

QRadioButton::indicator {{
    width: 16px;
    height: 16px;
    border: 1px solid rgba(255, 255, 255, 0.25);
    border-radius: 8px;
    background-color: rgba(255, 255, 255, 0.06);
}}

QRadioButton::indicator:checked {{
    background-color: #A855F7;
    border-color: #C084FC;
}}

/* Neon Gradient Action Buttons */
QPushButton#PrimaryButton {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6366F1, stop:0.5 #8B5CF6, stop:1 #EC4899);
    color: #FFFFFF;
    border: none;
    border-radius: 10px;
    padding: 8px 20px;
    min-height: 28px;
    font-weight: 700;
    font-size: 15px;
}}

QPushButton#PrimaryButton:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4F46E5, stop:0.5 #7C3AED, stop:1 #DB2777);
}}

QPushButton#PrimaryButton:pressed {{
    background: #4338CA;
}}

QPushButton#SecondaryButton {{
    background-color: rgba(255, 255, 255, 0.08);
    color: #F8FAFC;
    border: 1px solid rgba(255, 255, 255, 0.18);
    border-radius: 10px;
    padding: 7px 18px;
    min-height: 26px;
    font-weight: 600;
}}

QPushButton#SecondaryButton:hover {{
    background-color: rgba(255, 255, 255, 0.15);
    border-color: #A855F7;
}}

QPushButton#SuccessButton {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #059669, stop:1 #10B981);
    color: #FFFFFF;
    border: none;
    border-radius: 10px;
    padding: 7px 18px;
    min-height: 26px;
    font-weight: 600;
}}

QPushButton#SuccessButton:hover {{
    background: #047857;
}}

QPushButton#DangerButton {{
    background-color: rgba(127, 29, 29, 0.65);
    color: #FEE2E2;
    border: 1px solid rgba(239, 68, 68, 0.4);
    border-radius: 10px;
    padding: 7px 18px;
    min-height: 26px;
    font-weight: 600;
}}

QPushButton#DangerButton:hover {{
    background-color: rgba(153, 27, 27, 0.85);
    border-color: #EF4444;
}}

/* Tab Bar & Pane */
QTabWidget::pane {{
    border: none;
    background: transparent;
    padding: 0px;
}}

QTabWidget::tab-bar {{
    alignment: center;
}}

QTabBar::tab {{
    background-color: transparent;
    color: #94A3B8;
    padding: 6px 16px;
    font-weight: 700;
    font-size: 14px;
    border-bottom: 2px solid transparent;
}}

QTabBar::tab:selected {{
    color: #C084FC;
    border-bottom: 2.5px solid #A855F7;
}}

QTabBar::tab:hover {{
    color: #F8FAFC;
}}

/* Table Widget */
QTableWidget {{
    background-color: rgba(25, 22, 50, 0.65);
    gridline-color: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.14);
    border-radius: 12px;
}}

QTableWidget::item {{
    padding: 10px;
    color: #F8FAFC;
}}

QTableWidget::item:selected {{
    background-color: rgba(139, 92, 246, 0.35);
    color: #FFFFFF;
}}

QHeaderView::section {{
    background-color: rgba(15, 12, 32, 0.8);
    color: #A5B4FC;
    padding: 10px;
    font-weight: 600;
    border: none;
    border-bottom: 1px solid rgba(255, 255, 255, 0.14);
}}

/* Scroll Bars */
QScrollBar:vertical {{
    background-color: transparent;
    width: 8px;
    border-radius: 4px;
}}

QScrollBar::handle:vertical {{
    background-color: rgba(255, 255, 255, 0.2);
    border-radius: 4px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: rgba(255, 255, 255, 0.35);
}}

/* Labels & Typography */
QLabel#HeaderTitle {{
    font-size: 24px;
    font-weight: 700;
    color: #FFFFFF;
}}

QLabel#SubTitle {{
    font-size: 14px;
    color: #A5B4FC;
}}

QLabel#SectionHeader {{
    font-size: 16px;
    font-weight: 600;
    color: #F1F5F9;
}}

QLabel#StatusError {{
    color: #F87171;
    font-weight: 600;
}}

QLabel#StatusSuccess {{
    color: #34D399;
    font-weight: 600;
}}

/* Compact AI Badge Pill */
QLabel#AIBadge {{
    background-color: rgba(6, 95, 70, 0.65);
    color: #34D399;
    padding: 5px 14px;
    border-radius: 14px;
    font-weight: 600;
    font-size: 12px;
    border: 1px solid rgba(52, 211, 153, 0.4);
}}

/* Interactive Chatbot Styling */
QLabel#UserBubble {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6366F1, stop:1 #A855F7);
    color: #FFFFFF;
    border-radius: 14px;
    padding: 10px 16px;
    font-size: 13px;
}}

QLabel#BotBubble {{
    background-color: rgba(30, 27, 60, 0.85);
    border: 1px solid rgba(255, 255, 255, 0.16);
    color: #F8FAFC;
    border-radius: 14px;
    padding: 12px 18px;
    font-size: 13px;
}}

QPushButton#PromptChip {{
    background-color: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.18);
    color: #C084FC;
    border-radius: 16px;
    padding: 6px 14px;
    font-size: 12px;
    font-weight: 500;
}}

QPushButton#PromptChip:hover {{
    background-color: rgba(255, 255, 255, 0.16);
    color: #FFFFFF;
    border-color: #A855F7;
}}

/* Glass Dialog & QMessageBox Styling */
QDialog, QMessageBox {{
    background-color: #16132C;
    color: #FFFFFF;
}}

QMessageBox QLabel {{
    color: #F1F5F9;
    font-size: 13.5px;
    font-weight: 500;
    background: transparent;
}}

QMessageBox QPushButton {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6366F1, stop:0.5 #8B5CF6, stop:1 #EC4899);
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    padding: 7px 22px;
    min-width: 80px;
    min-height: 26px;
    font-weight: 700;
    font-size: 13.5px;
}}

QMessageBox QPushButton:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4F46E5, stop:0.5 #7C3AED, stop:1 #DB2777);
}}
"""

# Feature 9: Light Theme QSS
LIGHT_THEME_QSS = """
QWidget {
    background: transparent;
    color: #1E293B;
    font-family: 'Segoe UI', 'SF Pro Display', Roboto, sans-serif;
    font-size: 13px;
}

QMainWindow, QWidget#MainRoot {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #F0F4FF, stop:0.5 #EEF2FF, stop:1 #F5F3FF);
}

QFrame#CardFrame, QFrame.card {
    background-color: rgba(255, 255, 255, 0.85);
    border: 1px solid rgba(0, 0, 0, 0.10);
    border-radius: 18px;
}

QFrame#GlassCard {
    background-color: rgba(255, 255, 255, 0.80);
    border: 1px solid rgba(0, 0, 0, 0.12);
    border-radius: 20px;
}

QFrame#KPICard {
    background-color: rgba(255, 255, 255, 0.88);
    border: 1px solid rgba(99, 102, 241, 0.25);
    border-radius: 18px;
}

QFrame#Sidebar {
    background-color: rgba(238, 242, 255, 0.92);
    border: 1px solid rgba(99, 102, 241, 0.20);
    border-radius: 20px;
    margin: 8px;
}

QLabel {
    color: #1E293B;
    background: transparent;
}

QLabel#HeaderTitle {
    font-size: 22px;
    font-weight: 800;
    color: #1E1B4B;
}

QLabel#SubTitle {
    font-size: 13px;
    color: #475569;
}

QLabel#SectionHeader {
    font-size: 15px;
    font-weight: 700;
    color: #312E81;
}

QLineEdit, QTextEdit, QComboBox {
    background-color: rgba(255, 255, 255, 0.90);
    border: 1.5px solid rgba(99, 102, 241, 0.35);
    border-radius: 10px;
    padding: 8px 12px;
    color: #1E293B;
    font-size: 13.5px;
}

QLineEdit:focus, QTextEdit:focus {
    border-color: #6366F1;
    background-color: #FFFFFF;
}

QPushButton#PrimaryButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6366F1, stop:0.5 #8B5CF6, stop:1 #EC4899);
    color: #FFFFFF;
    border: none;
    border-radius: 10px;
    padding: 10px 24px;
    font-weight: 700;
    font-size: 14px;
}

QPushButton#SecondaryButton {
    background: rgba(99, 102, 241, 0.12);
    color: #6366F1;
    border: 1.5px solid rgba(99, 102, 241, 0.4);
    border-radius: 10px;
    padding: 9px 20px;
    font-weight: 600;
}

QPushButton#NavButton {
    background: transparent;
    color: #334155;
    border: none;
    border-radius: 12px;
    padding: 11px 16px;
    font-size: 13.5px;
    font-weight: 600;
    text-align: left;
}

QPushButton#NavButton:hover, QPushButton#NavButton:checked {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 rgba(99,102,241,0.20), stop:1 rgba(139,92,246,0.12));
    color: #4338CA;
}

QTableWidget {
    background: rgba(255, 255, 255, 0.80);
    border: 1px solid rgba(0, 0, 0, 0.08);
    border-radius: 12px;
    gridline-color: rgba(0,0,0,0.06);
    color: #1E293B;
}

QTableWidget::item:selected {
    background: rgba(99, 102, 241, 0.18);
    color: #312E81;
}

QProgressBar {
    background-color: rgba(0,0,0,0.06);
    border-radius: 6px;
    border: 1px solid rgba(0,0,0,0.08);
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6366F1, stop:1 #8B5CF6);
    border-radius: 6px;
}

QScrollBar:vertical {
    background: rgba(0,0,0,0.04);
    width: 6px;
    border-radius: 3px;
}

QScrollBar::handle:vertical {
    background: rgba(99,102,241,0.4);
    border-radius: 3px;
}
"""

