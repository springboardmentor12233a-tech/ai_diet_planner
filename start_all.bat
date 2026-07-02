@echo off
REM AI Diet Planner - Complete Startup Script for Windows

echo.
echo ========================================
echo AI Diet Planner - Complete Startup
echo ========================================
echo.

REM Check if both setups are done
if not exist "venv" (
    echo Virtual environment not found!
    echo Please run: setup_backend.bat first
    pause
    exit /b 1
)

if not exist "frontend\node_modules" (
    echo Frontend dependencies not installed!
    echo Please run: setup_frontend.bat first
    pause
    exit /b 1
)

REM Check for .env file
if not exist ".env" (
    echo Creating .env file from template...
    copy .env.example .env
    echo Please update .env with your OpenAI API key!
)

echo.
echo ========================================
echo Starting Backend and Frontend...
echo ========================================
echo.
echo IMPORTANT:
echo - Backend will start on http://127.0.0.1:8000
echo - Frontend will start on http://localhost:3000
echo - Both windows will open. Keep them running!
echo.
pause

REM Activate virtual environment and start backend
start cmd /k "cd /d %cd% && call venv\Scripts\activate && python backend/main.py"

timeout /t 3

REM Start frontend
start cmd /k "cd /d %cd%\frontend && npm start"

echo.
echo ========================================
echo Application starting...
echo Check both console windows for status
echo ========================================
echo.
pause
