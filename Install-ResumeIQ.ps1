# ==============================================================================
# ResumeIQ — Automated Windows Setup & Dependency Installer
# ==============================================================================
# This script checks for system prerequisites (Python 3.10+, VC++ Redistributable),
# automatically downloads missing components from official sources, sets up the
# Python virtual environment, installs all required packages & NLP models, and
# creates Desktop & Start Menu shortcuts.
# ==============================================================================

$ErrorActionPreference = "Stop"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "         ResumeIQ — Automated System & Dependency Setup" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $ScriptDir

# ------------------------------------------------------------------------------
# 1. Check & Install Python 3.10+
# ------------------------------------------------------------------------------
Write-Host "[1/5] Checking Python installation on target OS..." -ForegroundColor Yellow

$PythonCmd = Get-Command python -ErrorAction SilentlyContinue
$HasValidPython = $false

if ($PythonCmd) {
    try {
        $PyVersionRaw = & python --version 2>&1
        if ($PyVersionRaw -match "Python (\d+)\.(\d+)") {
            $Major = [int]$Matches[1]
            $Minor = [int]$Matches[2]
            if ($Major -ge 3 -and $Minor -ge 10) {
                $HasValidPython = $true
                Write-Host "  -> Python $Major.$Minor detected on PATH ($($PythonCmd.Source))." -ForegroundColor Green
            }
        }
    } catch {}
}

if (-not $HasValidPython) {
    Write-Host "  -> Python 3.10+ not found! Downloading Python 3.12 64-bit installer..." -ForegroundColor Red
    $PythonUrl = "https://www.python.org/ftp/python/3.12.9/python-3.12.9-amd64.exe"
    $PythonInstallerPath = "$env:TEMP\python-3.12.9-amd64.exe"
    
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    Invoke-WebRequest -Uri $PythonUrl -OutFile $PythonInstallerPath
    
    Write-Host "  -> Installing Python 3.12 silently (with PATH enabled)..." -ForegroundColor Yellow
    Start-Process -FilePath $PythonInstallerPath -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1 Include_pip=1" -Wait
    
    # Refresh PATH environment variable
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    Write-Host "  -> Python 3.12 installed successfully!" -ForegroundColor Green
}

# ------------------------------------------------------------------------------
# 2. Check & Install Visual C++ Redistributable 2015-2022
# ------------------------------------------------------------------------------
Write-Host "[2/5] Checking Visual C++ Redistributable requirement..." -ForegroundColor Yellow

$VCRedistInstalled = Test-Path "HKLM:\SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64"
if (-not $VCRedistInstalled) {
    Write-Host "  -> VC++ Redistributable missing! Downloading official Microsoft package..." -ForegroundColor Red
    $VCUrl = "https://aka.ms/vs/17/release/vc_redist.x64.exe"
    $VCInstallerPath = "$env:TEMP\vc_redist.x64.exe"
    
    Invoke-WebRequest -Uri $VCUrl -OutFile $VCInstallerPath
    Write-Host "  -> Installing Visual C++ Redistributable..." -ForegroundColor Yellow
    Start-Process -FilePath $VCInstallerPath -ArgumentList "/passive /norestart" -Wait
    Write-Host "  -> Visual C++ Redistributable installed successfully!" -ForegroundColor Green
} else {
    Write-Host "  -> Visual C++ Redistributable is already present." -ForegroundColor Green
}

# ------------------------------------------------------------------------------
# 3. Create / Verify Python Virtual Environment
# ------------------------------------------------------------------------------
Write-Host "[3/5] Setting up isolated Python virtual environment (.venv)..." -ForegroundColor Yellow

$VenvDir = Join-Path $ScriptDir ".venv"
$VenvPy = Join-Path $VenvDir "Scripts\python.exe"
$VenvPip = Join-Path $VenvDir "Scripts\pip.exe"

if (-not (Test-Path $VenvPy)) {
    Write-Host "  -> Creating virtual environment in: $VenvDir" -ForegroundColor Gray
    & python -m venv ".venv"
}

Write-Host "  -> Upgrading pip to latest version..." -ForegroundColor Gray
& $VenvPy -m pip install --upgrade pip --quiet

# ------------------------------------------------------------------------------
# 4. Install / Update Requirements & spaCy Model
# ------------------------------------------------------------------------------
Write-Host "[4/5] Installing/Upgrading required packages from requirements.txt..." -ForegroundColor Yellow

if (Test-Path "$ScriptDir\requirements.txt") {
    & $VenvPip install -r "$ScriptDir\requirements.txt" --quiet
    Write-Host "  -> All Python packages installed successfully." -ForegroundColor Green
}

Write-Host "  -> Checking spaCy English NLP model (en_core_web_sm)..." -ForegroundColor Yellow
$HasModel = & $VenvPy -c "import en_core_web_sm; print(True)" 2>$null
if ($HasModel -ne "True") {
    Write-Host "  -> Downloading latest en_core_web_sm spaCy model..." -ForegroundColor Gray
    & $VenvPy -m spacy download en_core_web_sm
    Write-Host "  -> spaCy model downloaded." -ForegroundColor Green
} else {
    Write-Host "  -> spaCy model 'en_core_web_sm' is already loaded." -ForegroundColor Green
}

# ------------------------------------------------------------------------------
# 5. Create Desktop & Start Menu Shortcuts
# ------------------------------------------------------------------------------
Write-Host "[5/5] Creating Windows Desktop and Start Menu shortcuts..." -ForegroundColor Yellow

$WScriptShell = New-Object -ComObject WScript.Shell

# Desktop Shortcut
$DesktopPath = [System.Environment]::GetFolderPath("Desktop")
$ShortcutDesktop = $WScriptShell.CreateShortcut("$DesktopPath\ResumeIQ.lnk")
$ShortcutDesktop.TargetPath = "$VenvDir\Scripts\pythonw.exe"
$ShortcutDesktop.Arguments = "`"$ScriptDir\main.py`""
$ShortcutDesktop.WorkingDirectory = "$ScriptDir"
$ShortcutDesktop.Description = "ResumeIQ — AI Resume Analyzer & ATS Suite"
$ShortcutDesktop.Save()

# Start Menu Shortcut
$StartMenuPath = [System.Environment]::GetFolderPath("Programs")
$ShortcutStart = $WScriptShell.CreateShortcut("$StartMenuPath\ResumeIQ.lnk")
$ShortcutStart.TargetPath = "$VenvDir\Scripts\pythonw.exe"
$ShortcutStart.Arguments = "`"$ScriptDir\main.py`""
$ShortcutStart.WorkingDirectory = "$ScriptDir"
$ShortcutStart.Description = "ResumeIQ — AI Resume Analyzer & ATS Suite"
$ShortcutStart.Save()

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host " 🎉 Setup Complete! ResumeIQ is ready to run." -ForegroundColor Green
Write-Host " You can now launch ResumeIQ from your Desktop shortcut." -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
