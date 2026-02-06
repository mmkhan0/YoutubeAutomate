@echo off
REM Windows Batch Script to Run YouTube Automation
REM This script is designed to be run by Windows Task Scheduler

REM Set the working directory to the project root
cd /d %~dp0

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

REM Run the Python script
echo Starting YouTube Automation at %date% %time%
python run_automation.py

REM Log the exit code
echo YouTube Automation finished with exit code %ERRORLEVEL% at %date% %time%

REM If you want to keep the window open for debugging, uncomment the next line
REM pause

exit /b %ERRORLEVEL%
