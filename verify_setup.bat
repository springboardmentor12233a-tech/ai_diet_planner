@echo off
REM AI Diet Planner - Verification Script

echo.
echo ========================================
echo AI Diet Planner - Verification
echo ========================================
echo.

python verify_setup.py

if errorlevel 1 (
    echo.
    echo Issues detected. Please fix above errors.
) else (
    echo.
    echo Setup verified successfully!
)

pause
