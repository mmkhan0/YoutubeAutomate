@echo off
REM Setup script for YouTube Automation project

echo ========================================
echo YouTube Automation Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://www.python.org/
    pause
    exit /b 1
)

echo Step 1: Creating virtual environment...
python -m venv venv
if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo Step 2: Activating virtual environment...
call venv\Scripts\activate.bat

echo Step 3: Upgrading pip...
python -m pip install --upgrade pip

echo Step 4: Installing dependencies...
pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Copy config\config.example.yaml to config\config.yaml
echo 2. Fill in your API keys in config\config.yaml
echo 3. Download FFmpeg and update the path in config.yaml
echo 4. Set up YouTube API credentials (client_secrets.json)
echo 5. Add some royalty-free music to assets\music\
echo 6. Run: python main.py (or use run_automation.bat)
echo.
echo For Windows Task Scheduler setup, see SETUP.md
echo.
pause
