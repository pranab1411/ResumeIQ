# Project Rules & Build Workflow

## 1. Feature, Bug Fix & Regression Testing Workflow
Whenever a bug is reported, a feature is added, or a change is requested:
1. **Fix Code First & Inquire Before Building**:
   - Fix the bug in the codebase, verify correctness, and push to GitHub.
   - **MANDATORY**: ALWAYS ask the user whether to proceed with compiling the new test build installer right away or if they are explaining additional bugs/changes to bundle into this iteration.
2. **Installable Test Build via Inno Setup**:
   - When the user confirms to generate the test build, compile the package using `build_test.py` and place it into `test_builds/`.
   - **MANDATORY**: Test builds must ALWAYS be **installable Setup executables (Installers)** compiled via Inno Setup, NOT portable/standalone binaries.
3. **Auto-Incremented Test Build Naming Convention**:
   - Every test build installer package must be named with an automatically incrementing test build number:
     `ResumeIQ v<CURRENT_VERSION> test build <N>.exe` (e.g., `ResumeIQ v2.0.0 test build 1.exe`, `ResumeIQ v2.0.0 test build 2.exe`, `ResumeIQ v2.0.0 test build 3.exe`, etc.).
   - The test build script scans `test_builds/` and automatically increments `<N>` on each new test build installer.
4. **Commit & Push for Regression Testing**:
   - Push all changes and test build metadata to the GitHub repository.
   - Await the user's manual regression testing and feedback on the installer.
   - If bugs or adjustments are requested, repeat the flow with incremented test build numbers.

## 2. Final / Production Release Workflow
5. **Explicit Release Confirmation Only**:
   - Do NOT create or push an official final/production release build until the user explicitly confirms and instructs to push as a new build.
   - Upon confirmation, increment version if needed, compile the official installer/binaries via `build_installer.py`, and publish/commit the release.
