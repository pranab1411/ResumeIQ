#!/usr/bin/env python3
"""
ResumeIQ Automated Packaging & Installer Compiler Script
Compiles the standalone PyInstaller distribution and builds the Inno Setup installer executable.
"""

import os
import sys
import subprocess
import shutil

# Fix Windows console UTF-8 output encoding
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def run_step(title, command, cwd=None):
    print(f"\n{'='*60}\n -> {title}\n{'='*60}")
    res = subprocess.run(command, cwd=cwd, shell=True)
    if res.returncode != 0:
        print(f"[ERROR] Error during: {title}")
        sys.exit(1)
    print(f"[OK] Completed: {title}")

def run_pre_build_code_check(base_dir: str):
    """
    Mandatory Pre-Build Code Check:
    Performs full AST syntax verification on every Python file in the repository,
    and executes module import validation across all application modules before building.
    """
    print("\n============================================================")
    print(" 🔍 Executing Mandatory Pre-Build Full Codebase Verification Check")
    print("============================================================")
    
    import ast
    import importlib

    if base_dir not in sys.path:
        sys.path.insert(0, base_dir)
    errors = []

    py_count = 0
    for root, dirs, files in os.walk(base_dir):
        if any(skip in root for skip in ['venv', '.git', '__pycache__', 'build', 'dist', 'scratch']):
            continue
        for file in files:
            if file.endswith('.py'):
                py_count += 1
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, base_dir)
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        ast.parse(f.read(), filename=rel_path)
                except SyntaxError as se:
                    errors.append(f"Syntax Error in {rel_path}: line {se.lineno}: {se.msg}")

    print(f" [OK] Verified AST syntax across {py_count} Python files.")

    modules_to_verify = [
        'main',
        'config.version',
        'database.database',
        'modules.nlp_engine',
        'modules.local_ai_agent',
        'modules.report_generator',
        'modules.ats_calculator',
        'modules.ats_benchmark',
        'modules.otp_service',
        'modules.jd_scraper',
        'modules.chatbot_engine',
        'modules.mnc_ats_engine',
        'utils.paths',
        'utils.logger',
        'utils.gemini_client',
        'utils.security',
        'ui.dashboard_window',
        'ui.login_window',
        'ui.splash_screen',
        'ui.closing_screen',
        'ui.about_developer_page',
        'ui.profile_page',
        'ui.floating_widget',
    ]

    for mod in modules_to_verify:
        try:
            importlib.import_module(mod)
            print(f" [OK] Verified module import: {mod}")
        except Exception as e:
            errors.append(f"Import/Runtime Error in {mod}: {e}")

    if errors:
        print("\n[CRITICAL ERROR] Pre-build code verification failed with errors:")
        for err in errors:
            print(f"  ❌ {err}")
        print("\nBuild aborted to prevent generating a broken installer package.")
        sys.exit(1)

    print(" [SUCCESS] Pre-build code check passed cleanly with 0 errors!\n")


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_dir)

    # MANDATORY PRE-BUILD CODE & ERROR VERIFICATION
    run_pre_build_code_check(base_dir)

    print("============================================================")
    print("      ResumeIQ — Building Standalone Executable & Setup")
    print("============================================================")

    # 1. Ensure Production build type in config/version.py
    version_file = os.path.join(base_dir, "config", "version.py")
    if os.path.exists(version_file):
        with open(version_file, "r", encoding="utf-8") as f:
            v_content = f.read()
        import re
        v_content = re.sub(r'BUILD_TYPE\s*=\s*"[^"]*"', 'BUILD_TYPE = "Production"', v_content)
        with open(version_file, "w", encoding="utf-8") as f:
            f.write(v_content)

    # 2. Clean previous build artifacts
    dist_dir = os.path.join(base_dir, "dist")
    build_dir = os.path.join(base_dir, "build")
    if os.path.exists(build_dir):
        print("Cleaning previous build folder...")
        shutil.rmtree(build_dir, ignore_errors=True)

    # 3. Run PyInstaller using main.spec with --clean
    pyi_cmd = f'"{sys.executable}" -m PyInstaller --clean --noconfirm main.spec'
    run_step("Compiling Standalone Binary with PyInstaller", pyi_cmd, cwd=base_dir)

    exe_path = os.path.join(dist_dir, "ResumeIQ.exe")
    if os.path.exists(exe_path):
        print(f"  [OK] PyInstaller binary generated at: {exe_path} ({os.path.getsize(exe_path) / (1024*1024):.1f} MB)")
    else:
        print("  [ERROR] PyInstaller did not output ResumeIQ.exe!")
        sys.exit(1)

    # 3. Look for Inno Setup Compiler (ISCC)
    iscc_paths = [
        "iscc",
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe",
        os.path.expandvars(r"%LocalAppData%\Programs\Inno Setup 6\ISCC.exe")
    ]

    iscc_found = None
    for path in iscc_paths:
        if shutil.which(path) or os.path.exists(path):
            iscc_found = path
            break

    if iscc_found:
        iscc_cmd = f'"{iscc_found}" installer_setup.iss'
        run_step("Compiling Inno Setup Executable (ResumeIQ_Setup_v2.0.exe)", iscc_cmd, cwd=base_dir)
        setup_exe = os.path.join(base_dir, "Output", "ResumeIQ_Setup_v2.0.exe")
        if os.path.exists(setup_exe):
            print(f"\n[SUCCESS] Installer created at: {setup_exe}")
    else:
        print("\n" + "="*60)
        print(" [INFO] Inno Setup Compiler (ISCC.exe) not found on system PATH.")
        print("        To build the single ResumeIQ_Setup_v2.0.exe file:")
        print("        1. Download free Inno Setup 6 from: https://jrsoftware.org/isdl.php")
        print("        2. Right-click 'installer_setup.iss' and click 'Compile'.")
        print("="*60)

if __name__ == "__main__":
    main()
