@echo off
REM AI Diet Planner - Frontend Setup Script for Windows

echo ========================================
echo AI Diet Planner - Frontend Setup
echo ========================================
echo.

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo Error: Node.js is not installed or not in PATH
    exit /b 1
)

REM Check if npm is installed
npm --version >nul 2>&1
if errorlevel 1 (
    echo Error: npm is not installed or not in PATH
    exit /b 1
)

cd frontend

echo.
echo Step 1: Installing dependencies...
call npm install

echo.
echo Step 2: Creating .env file...
if not exist ".env" (
    (
        echo REACT_APP_API_URL=http://127.0.0.1:8000
    ) > .env
    echo .env file created successfully!
) else (
    echo .env file already exists.
)

echo.
echo ========================================
echo Frontend setup complete!
echo ========================================
echo.
echo To start the frontend:
echo   1. Navigate to frontend directory: cd frontend
echo   2. Run: npm start
echo.
pause
