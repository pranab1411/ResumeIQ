import random
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTabWidget, QFrame, QMessageBox, QGraphicsDropShadowEffect, QCheckBox
)
from PyQt6.QtCore import pyqtSignal, Qt, QTimer
from PyQt6.QtGui import QColor, QFont, QIcon, QPixmap, QIntValidator
from modules.auth import AuthManager
from modules.otp_service import otp_service
from database.database import db
from utils.logger import logger
from utils.paths import get_asset_path
from ui.glass_message_box import GlassMessageBox

class LoginWindow(QWidget):
    login_success = pyqtSignal(dict) # Emits user dict on successful login

    def __init__(self):
        super().__init__()
        self.generated_otp = None
        self.otp_email = None
        self.reset_token = None
        self.cooldown_remaining = 0
        self.resend_timer = QTimer(self)
        self.resend_timer.setInterval(1000)
        self.resend_timer.timeout.connect(self._update_cooldown_timer)
        self.setWindowTitle("ResumeIQ — Sign In")
        self.resize(480, 580)
        self.setMinimumSize(420, 520)
        self.init_ui()

    def init_ui(self):
        self.setObjectName("MainRoot")
        
        # Outer Horizontal Centering Layout
        outer_layout = QHBoxLayout()
        outer_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(outer_layout)

        # Card Container Frame (Fixed 440px width)
        self.card = QFrame()
        self.card.setObjectName("GlassCard")
        self.card.setFixedWidth(440)
        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(28, 22, 28, 22)
        card_layout.setSpacing(10)
        self.card.setLayout(card_layout)

        # Vertical Centering Column
        v_box = QVBoxLayout()
        v_box.setContentsMargins(0, 0, 0, 0)
        v_box.addStretch(1)
        v_box.addWidget(self.card, 0, Qt.AlignmentFlag.AlignCenter)
        v_box.addStretch(1)

        outer_layout.addStretch(1)
        outer_layout.addLayout(v_box, 0)
        outer_layout.addStretch(1)

        # App Logo & Branding Header
        brand_layout = QVBoxLayout()
        brand_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        brand_layout.setSpacing(4)
        
        logo_icon = QLabel()
        logo_pixmap = QPixmap(get_asset_path("assets", "logo.png"))
        if not logo_pixmap.isNull():
            logo_icon.setPixmap(logo_pixmap.scaled(76, 76, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        logo_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.title_label = QLabel("ResumeIQ")
        self.title_label.setObjectName("HeaderTitle")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("font-size: 24px; font-weight: 800; color: #FFFFFF;")
        
        self.subtitle_label = QLabel("Access Your Career Intelligence")
        self.subtitle_label.setObjectName("SubTitle")
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle_label.setStyleSheet("font-size: 13px; font-weight: 600; color: #A5B4FC;")

        brand_layout.addWidget(logo_icon)
        brand_layout.addWidget(self.title_label)
        brand_layout.addWidget(self.subtitle_label)
        card_layout.addLayout(brand_layout)

        # Status Alert Message Label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setWordWrap(True)
        self.status_label.hide()
        card_layout.addWidget(self.status_label)

        # Helper for Center Aligned Form Labels
        def make_center_label(text: str) -> QLabel:
            lbl = QLabel(text)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet("font-weight: 700; color: #E2E8F0; font-size: 14px; margin-bottom: 1px;")
            return lbl

        # Tabs Widget (Sign In / Register / Reset Password)
        self.tabs = QTabWidget()
            # --- TAB 1: SIGN IN ---
        self.signin_tab = QWidget()
        signin_layout = QVBoxLayout()
        signin_layout.setSpacing(5)
        signin_layout.setContentsMargins(0, 8, 0, 0)

        self.login_username = QLineEdit()
        self.login_username.setPlaceholderText("Username (e.g. riq_john_4829)")
        
        self.login_password = QLineEdit()
        self.login_password.setPlaceholderText("Password")
        self.login_password.setEchoMode(QLineEdit.EchoMode.Password)

        # Password show/hide layout
        pwd_layout = QHBoxLayout()
        pwd_layout.setContentsMargins(0, 0, 0, 0)
        pwd_layout.setSpacing(6)
        pwd_layout.addWidget(self.login_password)
        
        self.toggle_login_pwd_btn = QPushButton("👁️")
        self.toggle_login_pwd_btn.setFixedSize(36, 36)
        self.toggle_login_pwd_btn.setObjectName("IconButton")
        self.toggle_login_pwd_btn.setToolTip("Show / Hide Password")
        self.toggle_login_pwd_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle_login_pwd_btn.clicked.connect(lambda: self._toggle_pwd_visibility(self.login_password, self.toggle_login_pwd_btn))
        pwd_layout.addWidget(self.toggle_login_pwd_btn)

        # Remember Me Checkbox (Centered)
        self.chk_remember_me = QCheckBox("Remember Me")
        self.chk_remember_me.setCursor(Qt.CursorShape.PointingHandCursor)

        chk_box = QHBoxLayout()
        chk_box.addStretch()
        chk_box.addWidget(self.chk_remember_me)
        chk_box.addStretch()

        # Load saved username if Remember Me was enabled previously
        saved_username = db.get_setting("remembered_username", "")
        if saved_username:
            self.login_username.setText(saved_username)
            self.chk_remember_me.setChecked(True)

        self.btn_signin = QPushButton("Sign In")
        self.btn_signin.setObjectName("PrimaryButton")
        self.btn_signin.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_signin.clicked.connect(self.handle_signin)

        signin_layout.addWidget(make_center_label("Username"))
        signin_layout.addWidget(self.login_username)
        signin_layout.addSpacing(6)
        signin_layout.addWidget(make_center_label("Password"))
        signin_layout.addLayout(pwd_layout)
        signin_layout.addSpacing(6)
        signin_layout.addLayout(chk_box)
        signin_layout.addSpacing(8)
        signin_layout.addWidget(self.btn_signin)

        signin_layout.addStretch(1)
        self.signin_tab.setLayout(signin_layout)


        # --- TAB 2: REGISTER ---
        self.register_tab = QWidget()
        reg_layout = QVBoxLayout()
        reg_layout.setSpacing(4)
        reg_layout.setContentsMargins(0, 8, 0, 0)

        self.reg_name = QLineEdit()
        self.reg_name.setPlaceholderText("Full Name")

        self.reg_email = QLineEdit()
        self.reg_email.setPlaceholderText("Email Address")

        self.reg_password = QLineEdit()
        self.reg_password.setPlaceholderText("Password (min. 6 characters)")
        self.reg_password.setEchoMode(QLineEdit.EchoMode.Password)

        self.reg_confirm_password = QLineEdit()
        self.reg_confirm_password.setPlaceholderText("Confirm Password")
        self.reg_confirm_password.setEchoMode(QLineEdit.EchoMode.Password)

        self.btn_register = QPushButton("Create Account")
        self.btn_register.setObjectName("PrimaryButton")
        self.btn_register.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_register.clicked.connect(self.handle_register)

        reg_layout.addWidget(make_center_label("Full Name"))
        reg_layout.addWidget(self.reg_name)
        reg_layout.addSpacing(4)
        reg_layout.addWidget(make_center_label("Email Address"))
        reg_layout.addWidget(self.reg_email)
        reg_layout.addSpacing(4)
        reg_layout.addWidget(make_center_label("Password"))
        reg_layout.addWidget(self.reg_password)
        reg_layout.addSpacing(4)
        reg_layout.addWidget(make_center_label("Confirm Password"))
        reg_layout.addWidget(self.reg_confirm_password)
        reg_layout.addSpacing(8)
        reg_layout.addWidget(self.btn_register)
        reg_layout.addStretch(1)
        self.register_tab.setLayout(reg_layout)

        # --- TAB 3: RESET PASSWORD (REAL EMAIL OTP) ---
        self.reset_tab = QWidget()
        reset_layout = QVBoxLayout()
        reset_layout.setSpacing(4)
        reset_layout.setContentsMargins(0, 8, 0, 0)

        self.reset_email = QLineEdit()
        self.reset_email.setPlaceholderText("Registered Email Address")

        email_otp_layout = QHBoxLayout()
        email_otp_layout.setSpacing(6)
        email_otp_layout.addWidget(self.reset_email)
        
        self.btn_send_otp = QPushButton("📧 Send Email OTP")
        self.btn_send_otp.setObjectName("SecondaryButton")
        self.btn_send_otp.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_send_otp.clicked.connect(self.handle_send_otp)
        email_otp_layout.addWidget(self.btn_send_otp)

        self.reset_otp = QLineEdit()
        self.reset_otp.setPlaceholderText("6-Digit Email Verification OTP")
        self.reset_otp.setMaxLength(6)
        self.reset_otp.setValidator(QIntValidator(0, 999999))

        self.reset_new_pwd = QLineEdit()
        self.reset_new_pwd.setPlaceholderText("New Password (min. 6 chars)")
        self.reset_new_pwd.setEchoMode(QLineEdit.EchoMode.Password)

        self.reset_confirm_pwd = QLineEdit()
        self.reset_confirm_pwd.setPlaceholderText("Confirm New Password")
        self.reset_confirm_pwd.setEchoMode(QLineEdit.EchoMode.Password)

        self.btn_reset_pwd = QPushButton("🔑 Reset Password")
        self.btn_reset_pwd.setObjectName("PrimaryButton")
        self.btn_reset_pwd.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_reset_pwd.clicked.connect(self.handle_reset_password)

        reset_layout.addWidget(make_center_label("Registered Account Email"))
        reset_layout.addLayout(email_otp_layout)
        reset_layout.addSpacing(4)
        reset_layout.addWidget(make_center_label("6-Digit Verification OTP"))
        reset_layout.addWidget(self.reset_otp)
        reset_layout.addSpacing(4)
        reset_layout.addWidget(make_center_label("New Password"))
        reset_layout.addWidget(self.reset_new_pwd)
        reset_layout.addSpacing(4)
        reset_layout.addWidget(make_center_label("Confirm Password"))
        reset_layout.addWidget(self.reset_confirm_pwd)
        reset_layout.addSpacing(8)
        reset_layout.addWidget(self.btn_reset_pwd)
        reset_layout.addStretch(1)
        self.reset_tab.setLayout(reset_layout)

        self.tabs.addTab(self.signin_tab, "Sign In")
        self.tabs.addTab(self.register_tab, "Create Account")
        self.tabs.addTab(self.reset_tab, "Reset Password")
        card_layout.addWidget(self.tabs)

    def _toggle_pwd_visibility(self, field: QLineEdit, button: QPushButton):
        if field.echoMode() == QLineEdit.EchoMode.Password:
            field.setEchoMode(QLineEdit.EchoMode.Normal)
            button.setText("🙈")
        else:
            field.setEchoMode(QLineEdit.EchoMode.Password)
            button.setText("👁️")

    def show_message(self, message: str, is_error: bool = True):
        self.status_label.setText(message)
        self.status_label.setObjectName("StatusError" if is_error else "StatusSuccess")
        self.status_label.setStyle(self.status_label.style())
        self.status_label.show()

    def handle_signin(self):
        username = self.login_username.text().strip()
        password = self.login_password.text()

        user, message = AuthManager.login(username, password)
        if user:
            # Save or clear remembered username
            if self.chk_remember_me.isChecked():
                db.set_setting("remembered_username", username)
            else:
                db.set_setting("remembered_username", "")

            self.show_message("Login successful!", is_error=False)
            logger.info(f"User logged in: {user.get('username', user['email'])}")
            self.login_success.emit(user)
        else:
            self.show_message(message, is_error=True)

    def handle_register(self):
        name = self.reg_name.text().strip()
        email = self.reg_email.text().strip()
        password = self.reg_password.text()
        confirm_pwd = self.reg_confirm_password.text()

        success, message, auto_username = AuthManager.register(name, email, password, confirm_pwd)
        if success:
            self.show_message(f"Account created! System Username: {auto_username}", is_error=False)
            GlassMessageBox.success(
                self,
                "Account Created Successfully!",
                f"Your account has been created!\n\nYour System Generated Username is:\n👉 {auto_username}\n\nPlease use this Username to Sign In."
            )
            self.tabs.setCurrentIndex(0) # Switch to Sign In tab
            self.login_username.setText(auto_username)
            self.login_password.setText(password)
        else:
            self.show_message(message, is_error=True)

    def _update_cooldown_timer(self):
        if self.cooldown_remaining > 1:
            self.cooldown_remaining -= 1
            self.btn_send_otp.setText(f"Resend OTP in {self.cooldown_remaining}s")
            self.btn_send_otp.setEnabled(False)
        else:
            self.cooldown_remaining = 0
            self.resend_timer.stop()
            self.btn_send_otp.setText("📧 Resend OTP")
            self.btn_send_otp.setEnabled(True)

    def handle_send_otp(self):
        email = self.reset_email.text().strip()

        if not email:
            self.show_message("Please enter your registered Email Address.", is_error=True)
            return

        self.btn_send_otp.setEnabled(False)
        self.show_message("Requesting verification OTP...", is_error=False)

        success, msg, details = otp_service.generate_and_send_email_otp(email)
        if success and details:
            self.reset_token = None
            self.otp_email = email
            self.reset_otp.clear()
            self.show_message("Verification OTP sent to your email inbox.", is_error=False)
            
            # Start 60s cooldown timer
            self.cooldown_remaining = details.get("cooldown_seconds", 60)
            self.btn_send_otp.setText(f"Resend OTP in {self.cooldown_remaining}s")
            self.resend_timer.start()

            GlassMessageBox.information(
                self,
                "Email OTP Dispatched",
                f"Your 6-digit verification code has been sent to:\n👉 {details['masked_email']}\n\n"
                f"The code is valid for 5 minutes and can be attempted up to 5 times. Please check your inbox/spam folder."
            )
        else:
            self.btn_send_otp.setEnabled(True)
            self.show_message(msg, is_error=True)

    def handle_reset_password(self):
        email = self.reset_email.text().strip()
        otp = "".join(filter(str.isdigit, self.reset_otp.text()))
        new_pwd = self.reset_new_pwd.text()
        confirm_pwd = self.reset_confirm_pwd.text()

        if not email:
            self.show_message("Please enter your registered Email Address.", is_error=True)
            return

        # Step 1: If reset authorization token is not yet issued, verify OTP first
        if not self.reset_token:
            if not otp:
                self.show_message("Please enter the 6-digit OTP code received in your email.", is_error=True)
                return
            if len(otp) != 6:
                self.show_message("Invalid verification code. OTP must be exactly 6 numeric digits.", is_error=True)
                return

            self.btn_reset_pwd.setEnabled(False)
            self.show_message("Validating verification code...", is_error=False)
            otp_valid, otp_msg, token = otp_service.verify_otp(email, otp)
            self.btn_reset_pwd.setEnabled(True)

            if not otp_valid:
                self.reset_otp.clear()
                self.show_message(otp_msg, is_error=True)
                return

            self.reset_token = token
            self.show_message("OTP verified! Please enter your new password below.", is_error=False)
            self.reset_new_pwd.setFocus()
            return

        # Step 2: Reset Password using server-side reset authorization token
        if not new_pwd or not confirm_pwd:
            self.show_message("Please fill in both New Password and Confirm Password fields.", is_error=True)
            return

        self.btn_reset_pwd.setEnabled(False)
        self.show_message("Updating password...", is_error=False)
        success, message = AuthManager.reset_password(email, self.reset_token, new_pwd, confirm_pwd)
        self.btn_reset_pwd.setEnabled(True)

        if success:
            self.reset_token = None
            self.otp_email = None
            self.reset_email.clear()
            self.reset_otp.clear()
            self.reset_new_pwd.clear()
            self.reset_confirm_pwd.clear()
            if self.resend_timer.isActive():
                self.resend_timer.stop()
            self.btn_send_otp.setText("📧 Send Email OTP")
            self.btn_send_otp.setEnabled(True)

            self.show_message("Password Reset Successfully", is_error=False)
            GlassMessageBox.success(
                self,
                "Password Reset Successfully",
                "Your password has been changed successfully. A confirmation email has been sent to your registered email address."
            )
            self.tabs.setCurrentIndex(0) # Switch to Sign In tab
            self.login_password.setText(new_pwd)
        else:
            if "expired" in message.lower() or "authorization" in message.lower():
                self.reset_token = None
            self.show_message(message, is_error=True)

    def closeEvent(self, event):
        from ui.closing_screen import ClosingScreen
        event.accept()
        ClosingScreen.show_closing_and_exit()
