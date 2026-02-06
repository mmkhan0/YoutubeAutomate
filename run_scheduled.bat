@echo off
REM ============================================================================
REM YouTube Kids Learning Video Automation - Windows Task Scheduler Runner
REM ============================================================================
REM
REM This batch file is designed to be run by Windows Task Scheduler.
REM It runs the YouTube automation in a fully automated mode with:
REM - No user interaction
REM - Absolute paths
REM - Comprehensive logging
REM - Graceful error handling
REM
REM SCHEDULE SETUP:
REM 1. Open Task Scheduler
REM 2. Create Basic Task
REM 3. Name: "YouTube Kids Video Generation"
REM 4. Trigger: Daily at 9:00 AM (or your preferred time)
REM 5. Action: Start a program
REM 6. Program: C:\Windows\System32\cmd.exe
REM 7. Arguments: /c "D:\Projects\YoutubeAutomate\run_scheduled.bat"
REM 8. Start in: D:\Projects\YoutubeAutomate
REM 9. Run whether user is logged on or not
REM 10. Run with highest privileges
REM ============================================================================

echo ============================================================================
echo YouTube Kids Learning Video Automation
echo Starting: %DATE% %TIME%
echo ============================================================================

REM Get the directory where this batch file is located
cd /d "%~dp0"

REM Activate virtual environment
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    exit /b 1
)

echo Virtual environment activated
echo Python: %VIRTUAL_ENV%

REM Run automation in early learning mode (ages 2-6)
echo.
echo Running automation for early learning content (ages 2-6)...
echo.

python run_automation.py --category kids --language en

set EXIT_CODE=%ERRORLEVEL%

echo.
echo ============================================================================
echo Automation completed with exit code: %EXIT_CODE%
echo Finished: %DATE% %TIME%
echo ============================================================================

REM Log the run
if %EXIT_CODE% EQU 0 (
    echo [SUCCESS] %DATE% %TIME% >> logs\scheduler_runs.log
) else (
    echo [FAILED] %DATE% %TIME% Exit Code: %EXIT_CODE% >> logs\scheduler_runs.log
)

REM Deactivate virtual environment
deactivate

REM Exit with the same code as the Python script
exit /b %EXIT_CODE%
