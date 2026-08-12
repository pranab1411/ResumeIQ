# Project Rules & Build Workflow

## 1. Feature, Bug Fix & Build Release Workflow
Whenever creating a new build, adding a new feature, or fixing a bug:
1. **Test Build First**: Always generate and place the test build into the `test_builds/` directory before finalizing or releasing.
2. **Standard Build Naming Convention**:
   - Every test build artifact and package must be named with the format:
     `ResumeIQ v<CURRENT_VERSION> test build` (e.g., `ResumeIQ v2.0.0 test build.exe` or `ResumeIQ_v2.0.0_test_build.exe`).
3. **Push to Repository**:
   - Push all changes and test build tracking / logs / metadata to the GitHub repository (`main` or test build tracking in `test_builds/`).
