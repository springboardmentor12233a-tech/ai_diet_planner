@echo off
REM AI Diet Planner - Backend Setup Script for Windows

echo ========================================
echo AI Diet Planner - Backend Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    exit /b 1
)

echo Step 1: Creating virtual environment...
if not exist "venv\" (
    python -m venv venv
    echo Virtual environment created successfully!
) else (
    echo Virtual environment already exists.
)

echo.
echo Step 2: Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Step 3: Installing dependencies...
pip install --upgrade pip
pip install -r backend\requirements.txt

echo.
echo Step 4: Creating .env file from template...
if not exist ".env" (
    copy .env.example .env
    echo .env file created. Please update it with your OpenAI API key!
) else (
    echo .env file already exists.
)

echo.
echo Step 5: Creating necessary directories...
python -c "import os; os.makedirs('backend/uploads', exist_ok=True); os.makedirs('backend/exports', exist_ok=True); os.makedirs('backend/model', exist_ok=True); print('Directories created successfully!')"

echo.
echo ========================================
echo Backend setup complete!
echo ========================================
echo.
echo To start the backend:
echo   1. Activate virtual environment: venv\Scripts\activate
echo   2. Run: python backend/main.py
echo.
pause
