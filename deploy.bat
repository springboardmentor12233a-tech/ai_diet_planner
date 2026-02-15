@echo off
REM AI NutriCare System - Deployment Script for Windows

echo ===================================
echo AI NutriCare System - Deployment
echo ===================================
echo.

REM Check if .env file exists
if not exist .env (
    echo Error: .env file not found!
    echo Please create a .env file with required environment variables:
    echo   OPENAI_API_KEY=your-key
    echo   USDA_API_KEY=your-key
    echo   NUTRICARE_ENCRYPTION_KEY=your-key
    exit /b 1
)

REM Load environment variables from .env
for /f "tokens=*" %%a in (.env) do set %%a

REM Check required environment variables
if "%OPENAI_API_KEY%"=="" (
    echo Error: OPENAI_API_KEY not set in .env file
    exit /b 1
)

if "%USDA_API_KEY%"=="" (
    echo Error: USDA_API_KEY not set in .env file
    exit /b 1
)

if "%NUTRICARE_ENCRYPTION_KEY%"=="" (
    echo Warning: NUTRICARE_ENCRYPTION_KEY not set. Generating new key...
    for /f %%i in ('python -c "import secrets; print(secrets.token_hex(16))"') do set NEW_KEY=%%i
    echo NUTRICARE_ENCRYPTION_KEY=%NEW_KEY% >> .env
    set NUTRICARE_ENCRYPTION_KEY=%NEW_KEY%
    echo Generated and saved new encryption key to .env
)

REM Create necessary directories
echo Creating directories...
if not exist data mkdir data
if not exist models mkdir models
if not exist exports mkdir exports
if not exist logs mkdir logs

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo Error: Docker is not installed
    echo Please install Docker Desktop: https://docs.docker.com/desktop/install/windows-install/
    exit /b 1
)

REM Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo Error: Docker Compose is not installed
    echo Please install Docker Compose or use Docker Desktop which includes it
    exit /b 1
)

REM Build Docker image
echo.
echo Building Docker image...
docker-compose build

REM Start services
echo.
echo Starting services...
docker-compose up -d

REM Wait for services to start
echo.
echo Waiting for services to start...
timeout /t 10 /nobreak >nul

REM Check service status
echo.
echo Checking service status...
docker-compose ps

REM Display logs
echo.
echo Recent logs:
docker-compose logs --tail=20

echo.
echo ===================================
echo Deployment Complete!
echo ===================================
echo.
echo Access the application at: http://localhost:8501
echo.
echo Useful commands:
echo   View logs:        docker-compose logs -f
echo   Stop services:    docker-compose down
echo   Restart services: docker-compose restart
echo   View status:      docker-compose ps
echo.
pause
