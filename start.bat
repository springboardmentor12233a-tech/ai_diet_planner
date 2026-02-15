@echo off
REM AI NutriCare System - Startup Script for Windows

echo ===================================
echo AI NutriCare System - Starting
echo ===================================
echo.

REM Check if .env file exists
if not exist .env (
    echo Warning: .env file not found. Using .env.example as template...
    if exist .env.example (
        copy .env.example .env
        echo Created .env file. Please edit it with your API keys.
        pause
        exit /b 1
    ) else (
        echo Error: .env.example not found
        pause
        exit /b 1
    )
)

REM Load environment variables
for /f "tokens=*" %%a in (.env) do (
    echo %%a | findstr /v "^#" > nul
    if not errorlevel 1 set %%a
)

REM Check required environment variables
if "%OPENAI_API_KEY%"=="sk-your-openai-api-key-here" (
    echo Error: Please set OPENAI_API_KEY in .env file
    pause
    exit /b 1
)

if "%USDA_API_KEY%"=="your-usda-api-key-here" (
    echo Error: Please set USDA_API_KEY in .env file
    pause
    exit /b 1
)

if "%NUTRICARE_ENCRYPTION_KEY%"=="your-32-character-encryption-key-here" (
    echo Generating encryption key...
    for /f %%i in ('python -c "import secrets; print(secrets.token_hex(16))"') do set NEW_KEY=%%i
    powershell -Command "(Get-Content .env) -replace 'NUTRICARE_ENCRYPTION_KEY=.*', 'NUTRICARE_ENCRYPTION_KEY=%NEW_KEY%' | Set-Content .env"
    set NUTRICARE_ENCRYPTION_KEY=%NEW_KEY%
    echo Generated new encryption key
)

REM Create necessary directories
if not exist data mkdir data
if not exist models mkdir models
if not exist exports mkdir exports
if not exist logs mkdir logs

REM Run database migrations
echo Running database migrations...
if "%NUTRICARE_DB_PATH%"=="" set NUTRICARE_DB_PATH=data\nutricare.db
python migrations\migrate.py --db-path %NUTRICARE_DB_PATH%
echo.

REM Check if virtual environment exists
if not exist venv (
    if not exist .venv (
        echo Virtual environment not found. Creating one...
        python -m venv venv
        call venv\Scripts\activate.bat
        pip install -r requirements.txt
        echo Installing ai_diet_planner package in development mode...
        pip install -e .
    ) else (
        call .venv\Scripts\activate.bat
    )
) else (
    call venv\Scripts\activate.bat
)

REM Install package in development mode if not already installed
python -c "import ai_diet_planner" 2>nul
if errorlevel 1 (
    echo Installing ai_diet_planner package in development mode...
    pip install -e .
)

REM Start the application
echo Starting AI NutriCare System...
echo Access the application at: http://localhost:8501
echo.
streamlit run ai_diet_planner\ui\app.py
