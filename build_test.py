#!/usr/bin/env python3
"""
ResumeIQ Automated Test Build Script
Compiles the test build executable named according to the standard convention:
'ResumeIQ v<version> test build <N>.exe' with an auto-incrementing build counter <N>
and places it inside the test_builds directory.
"""

import os
import sys
import re
import shutil
import subprocess

# Fix Windows console UTF-8 output encoding
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def get_current_version(base_dir: str) -> str:
    iss_path = os.path.join(base_dir, "installer_setup.iss")
    if os.path.exists(iss_path):
        try:
            with open(iss_path, "r", encoding="utf-8") as f:
                content = f.read()
                m = re.search(r'#define\s+MyAppVersion\s+"([^"]+)"', content)
                if m:
                    return m.group(1)
        except Exception:
            pass
    return "2.0.0"

def get_next_test_build_number(test_builds_dir: str, version: str) -> int:
    """Scans test_builds directory and determines the next sequential test build number."""
    pattern = re.compile(rf"^ResumeIQ v{re.escape(version)} test build(?:\s+(\d+))?\.exe$", re.IGNORECASE)
    highest_num = 0
    
    # Check project test_builds and parent workspace test_builds if available
    search_dirs = [test_builds_dir]
    parent_test_builds = os.path.abspath(os.path.join(test_builds_dir, "..", "..", "test_builds"))
    if os.path.exists(parent_test_builds) and parent_test_builds not in search_dirs:
        search_dirs.append(parent_test_builds)

    for d in search_dirs:
        if os.path.exists(d):
            for f in os.listdir(d):
                m = pattern.match(f)
                if m:
                    if m.group(1):
                        highest_num = max(highest_num, int(m.group(1)))
                    else:
                        highest_num = max(highest_num, 1)

    return highest_num + 1

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

    version = get_current_version(base_dir)
    test_builds_dir = os.path.join(base_dir, "test_builds")
    os.makedirs(test_builds_dir, exist_ok=True)

    build_num = get_next_test_build_number(test_builds_dir, version)
    build_name = f"ResumeIQ v{version} test build {build_num}"

    print("============================================================")
    print(f"      Building Test Build: {build_name}")
    print("============================================================")

    # 1. Clean previous build directory
    build_dir = os.path.join(base_dir, "build")
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir, ignore_errors=True)

    # 2. Run PyInstaller
    pyi_cmd = f'"{sys.executable}" -m PyInstaller --clean --noconfirm main.spec'
    run_step("Compiling Binary with PyInstaller", pyi_cmd, cwd=base_dir)

    dist_exe = os.path.join(base_dir, "dist", "ResumeIQ.exe")
    if not os.path.exists(dist_exe):
        print("  [ERROR] PyInstaller failed to generate dist/ResumeIQ.exe")
        sys.exit(1)

    # 3. Copy to test_builds with incremented name
    target_exe = os.path.join(test_builds_dir, f"{build_name}.exe")
    shutil.copy2(dist_exe, target_exe)

    # Also copy to root workspace test_builds if present
    root_test_builds = os.path.abspath(os.path.join(base_dir, "..", "test_builds"))
    if os.path.exists(root_test_builds):
        root_target_exe = os.path.join(root_test_builds, f"{build_name}.exe")
        try:
            shutil.copy2(dist_exe, root_target_exe)
        except Exception as e:
            print(f"  [NOTE] Could not copy to {root_target_exe}: {e}")

    size_mb = os.path.getsize(target_exe) / (1024 * 1024)
    print(f"\n[SUCCESS] Test build successfully created:")
    print(f"  Target File : {target_exe}")
    print(f"  Build Size  : {size_mb:.1f} MB")
    print(f"  Build Name  : {build_name}")
    print("============================================================")

if __name__ == "__main__":
    main()
