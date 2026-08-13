import sys
import os
import ctypes
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

from ui.styles import DARK_THEME_QSS
from ui.splash_screen import SplashScreen
from ui.login_window import LoginWindow
from ui.dashboard_window import DashboardWindow
from database.database import db
from utils.logger import logger
from utils.paths import get_asset_path

def is_admin() -> bool:
    """Checks if the current process is running with administrator privileges."""
    if sys.platform != "win32":
        return True
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False

def ensure_admin():
    """Forces the application to prompt and run as Administrator on Windows."""
    if sys.platform == "win32" and not is_admin():
        try:
            params = " ".join([f'"{arg}"' for arg in sys.argv[1:]])
            if getattr(sys, 'frozen', False):
                executable = sys.executable
            else:
                executable = sys.executable
                params = f'"{os.path.abspath(sys.argv[0])}" {params}'.strip()

            ret = ctypes.windll.shell32.ShellExecuteW(
                None, "runas", executable, params, None, 1
            )
            if ret > 32:
                sys.exit(0)
        except Exception as e:
            logger.warning(f"Administrator elevation request failed: {e}")

def main():
    # Enforce administrator privileges on launch
    ensure_admin()

    # Enable High DPI scaling
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    
    app = QApplication(sys.argv)
    app.setApplicationName("ResumeIQ")
    app.setOrganizationName("ResumeIQ AI Systems")
    app.setWindowIcon(QIcon(get_asset_path("assets", "logo.png")))
    app.setQuitOnLastWindowClosed(False)

    # Apply global Dark Mode QSS Stylesheet
    app.setStyleSheet(DARK_THEME_QSS)

    # Initialize Database Schema
    db.init_db()
    logger.info("ResumeIQ application started.")

    login_win = LoginWindow()
    dashboard_win = None

    def on_login_success(user_dict: dict):
        nonlocal dashboard_win
        logger.info(f"Launching Dashboard for user: {user_dict['email']}")
        try:
            dashboard_win = DashboardWindow(current_user=user_dict)
            dashboard_win.show()
            login_win.hide()
        except Exception as e:
            logger.error(f"Error launching DashboardWindow: {e}", exc_info=True)

    login_win.login_success.connect(on_login_success)

    # Launch Startup Loading Splash Screen
    splash = SplashScreen()
    screen_geo = app.primaryScreen().geometry()
    splash.center_on_screen(screen_geo)

    def launch_main_app():
        login_win.show()
        splash.close()

    splash.loading_complete.connect(launch_main_app)
    splash.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
