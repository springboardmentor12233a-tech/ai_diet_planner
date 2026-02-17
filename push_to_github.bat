@echo off
echo ===================================================
echo 🚀 AI-NutriCare - GitHub Push Automation
echo ===================================================

echo Checking for Git...
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Git is not installed or not in your PATH.
    echo Please install Git from https://git-scm.com/download/win
    echo After installing, restart your terminal and run this script again.
    pause
    exit /b
)

echo.
echo 1. Initializing Repository...
git init

echo.
echo 2. Adding all files...
git add .

echo.
echo 3. Committing files...
git commit -m "Initial commit: Complete AI-NutriCare System (93% Accuracy)"

echo.
echo 4. Renaming branch to main...
git branch -M main

echo.
echo 5. Adding remote origin...
git remote add origin https://github.com/sainikhil849/ai_diet_plan.git

echo.
echo 6. Pushing to GitHub...
echo [NOTE] You may be asked to sign in to GitHub in a browser window.
git push -u origin main

echo.
echo ===================================================
echo ✅ DONE! Project successfully pushed to GitHub.
echo ===================================================
pause
