@echo off
REM Schedule CEO Weekly Briefing (runs every Monday at 9 AM)

echo ============================================================
echo Gold Tier Employee - Schedule CEO Weekly Briefing
echo ============================================================
echo.

REM Check for admin privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] This script requires Administrator privileges
    echo Right-click and select "Run as Administrator"
    echo.
    pause
    exit /b 1
)

echo [INFO] Creating scheduled task for CEO briefing...
echo.

REM Get Python path
for /f "delims=" %%i in ('where python') do set PYTHON_PATH=%%i

REM Get project directory
set PROJECT_DIR=%~dp0
set SCRIPT_PATH=%PROJECT_DIR%reporting\scheduled_briefing.py

echo Python: %PYTHON_PATH%
echo Script: %SCRIPT_PATH%
echo.

REM Create scheduled task (runs every Monday at 9:00 AM)
schtasks /create /tn "GoldTierCEOBriefing" /tr "\"%PYTHON_PATH%\" \"%SCRIPT_PATH%\"" /sc weekly /d MON /st 09:00 /ru SYSTEM /f

if %errorLevel% equ 0 (
    echo.
    echo [SUCCESS] Scheduled task created successfully!
    echo.
    echo Task Name: GoldTierCEOBriefing
    echo Schedule: Every Monday at 9:00 AM
    echo Action: Generate and email weekly CEO briefing
    echo.
    echo Configuration:
    echo   Set CEO_BRIEFING_EMAIL_ENABLED=true in .env
    echo   Set CEO_BRIEFING_RECIPIENTS=email1@example.com,email2@example.com
    echo.
    echo To view task: schtasks /query /tn GoldTierCEOBriefing
    echo To run now: schtasks /run /tn GoldTierCEOBriefing
    echo To delete: schtasks /delete /tn GoldTierCEOBriefing /f
) else (
    echo.
    echo [ERROR] Failed to create scheduled task
)

pause
