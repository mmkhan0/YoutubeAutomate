@echo off
REM Environment Setup Tool - Generates .env file interactively
REM Run this to configure your API keys and settings

echo.
echo ========================================================================
echo   YOUTUBE AUTOMATION - ENVIRONMENT SETUP
echo ========================================================================
echo.
echo This will help you configure your .env file with API keys.
echo.

REM Activate virtual environment if it exists
if exist ".venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call .venv\Scripts\activate.bat
) else (
    echo Warning: Virtual environment not found. Run setup.bat first.
    pause
    exit /b 1
)

REM Run setup script
python setup_env.py

REM Check if successful
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================================================
    echo   Setup completed successfully!
    echo ========================================================================
    echo.
) else (
    echo.
    echo ========================================================================
    echo   Setup failed. Please check the error messages above.
    echo ========================================================================
    echo.
)

pause
