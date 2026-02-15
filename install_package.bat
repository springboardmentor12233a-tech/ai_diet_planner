@echo off
REM Quick fix script to install ai_diet_planner package

echo ===================================
echo Installing AI NutriCare Package
echo ===================================
echo.

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
)

REM Install package in development mode
echo Installing ai_diet_planner package in development mode...
pip install -e .

echo.
echo ===================================
echo Installation Complete!
echo ===================================
echo.
echo You can now run: streamlit run ai_diet_planner\ui\app.py
echo Or use: start.bat
echo.
pause
