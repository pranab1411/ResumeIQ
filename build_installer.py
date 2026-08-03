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

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_dir)

    print("============================================================")
    print("      ResumeIQ — Building Standalone Executable & Setup")
    print("============================================================")

    # 1. Clean previous build artifacts
    dist_dir = os.path.join(base_dir, "dist")
    build_dir = os.path.join(base_dir, "build")
    if os.path.exists(build_dir):
        print("Cleaning previous build folder...")
        shutil.rmtree(build_dir, ignore_errors=True)

    # 2. Run PyInstaller using main.spec
    pyi_cmd = f'"{sys.executable}" -m PyInstaller --noconfirm main.spec'
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
        run_step("Compiling Inno Setup Executable (ResumeIQ_Setup_v1.0.0.exe)", iscc_cmd, cwd=base_dir)
        setup_exe = os.path.join(base_dir, "Output", "ResumeIQ_Setup_v1.0.0.exe")
        if os.path.exists(setup_exe):
            print(f"\n[SUCCESS] Installer created at: {setup_exe}")
    else:
        print("\n" + "="*60)
        print(" [INFO] Inno Setup Compiler (ISCC.exe) not found on system PATH.")
        print("        To build the single ResumeIQ_Setup_v1.0.0.exe file:")
        print("        1. Download free Inno Setup 6 from: https://jrsoftware.org/isdl.php")
        print("        2. Right-click 'installer_setup.iss' and click 'Compile'.")
        print("="*60)

if __name__ == "__main__":
    main()
