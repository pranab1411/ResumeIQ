# Project Rules & Build Workflow

## 1. Feature, Bug Fix & Regression Testing Workflow
Whenever creating a build, adding a new feature, or fixing a bug:
1. **Installable Test Build First**:
   - Always generate and place the test build into the `test_builds/` directory before finalizing or releasing.
   - **MANDATORY**: Test builds must ALWAYS be **installable Setup executables (Installers)** compiled via Inno Setup, NOT portable/standalone binaries.
2. **Auto-Incremented Test Build Naming Convention**:
   - Every test build installer package must be named with an automatically incrementing test build number:
     `ResumeIQ v<CURRENT_VERSION> test build <N>.exe` (e.g., `ResumeIQ v2.0.0 test build 1.exe`, `ResumeIQ v2.0.0 test build 2.exe`, `ResumeIQ v2.0.0 test build 3.exe`, etc.).
   - The test build script scans `test_builds/` and automatically increments `<N>` on each new test build installer.
3. **Commit & Push for Regression Testing**:
   - Push all changes and test build metadata to the GitHub repository.
   - Await the user's manual regression testing and feedback on the installer.
   - If bugs or adjustments are requested, fix them in further test build installer iterations with incremented test build numbers.

## 2. Final / Production Release Workflow
4. **Explicit Release Confirmation Only**:
   - Do NOT create or push an official final/production release build until the user explicitly confirms and instructs to push as a new build.
   - Upon confirmation, increment version if needed, compile the official installer/binaries via `build_installer.py`, and publish/commit the release.
