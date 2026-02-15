@echo off
REM AI NutriCare System - Demo Runner for Windows
REM This script runs the interactive demonstration

echo.
echo ========================================
echo   AI NutriCare System - Demo Runner
echo ========================================
echo.

REM Set encryption key for demo
set NUTRICARE_ENCRYPTION_KEY=demo-encryption-key-for-testing

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

echo Python found!
echo.

REM Run the demo
echo Starting demo...
echo.
python demo.py

echo.
echo Demo completed!
echo.
pause
