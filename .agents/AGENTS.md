# Project Rules & Build Workflow

## 1. Feature, Bug Fix & Regression Testing Workflow
Whenever creating a build, adding a new feature, or fixing a bug:
1. **Test Build First**: Always generate and place the test build into the `test_builds/` directory before finalizing or releasing.
2. **Standard Test Build Naming Convention**:
   - Every test build artifact and package must be named with the format:
     `ResumeIQ v<CURRENT_VERSION> test build` (e.g., `ResumeIQ v2.0.0 test build.exe` or `ResumeIQ_v2.0.0_test_build.exe`).
3. **Commit & Push for Regression Testing**:
   - Push all changes and test build metadata to the GitHub repository.
   - Await the user's manual regression testing and feedback.
   - If bugs or adjustments are requested, fix them in further test build iterations.

## 2. Final / Production Release Workflow
4. **Explicit Release Confirmation Only**:
   - Do NOT create or push an official final/production release build until the user explicitly confirms and instructs to push as a new build.
   - Upon confirmation, increment version if needed, compile the official installer/binaries via `build_installer.py`, and publish/commit the release.
