@echo off
REM Schedule automatic log rotation (runs daily at 2 AM)

echo ============================================================
echo Gold Tier Employee - Schedule Log Rotation
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

echo [INFO] Creating scheduled task for log rotation...
echo.

REM Get Python path
for /f "delims=" %%i in ('where python') do set PYTHON_PATH=%%i

REM Get project directory
set PROJECT_DIR=%~dp0
set SCRIPT_PATH=%PROJECT_DIR%deployment\log_rotator.py

echo Python: %PYTHON_PATH%
echo Script: %SCRIPT_PATH%
echo.

REM Create scheduled task
schtasks /create /tn "GoldTierLogRotation" /tr "\"%PYTHON_PATH%\" \"%SCRIPT_PATH%\" rotate" /sc daily /st 02:00 /ru SYSTEM /f

if %errorLevel% equ 0 (
    echo.
    echo [SUCCESS] Scheduled task created successfully!
    echo.
    echo Task Name: GoldTierLogRotation
    echo Schedule: Daily at 2:00 AM
    echo Action: Rotate and compress old logs
    echo.
    echo To view task: schtasks /query /tn GoldTierLogRotation
    echo To run now: schtasks /run /tn GoldTierLogRotation
    echo To delete: schtasks /delete /tn GoldTierLogRotation /f
) else (
    echo.
    echo [ERROR] Failed to create scheduled task
)

pause
