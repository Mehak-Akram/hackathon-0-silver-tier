@echo off
REM Install Gold Tier Employee as Windows Service
REM Requires Administrator privileges

echo ============================================================
echo Gold Tier Employee - Service Installation
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

echo [INFO] Installing service...
echo.

REM Run service manager
python deployment\service_manager.py install

if %errorLevel% equ 0 (
    echo.
    echo ============================================================
    echo Service installed successfully!
    echo ============================================================
    echo.
    echo To start the service:
    echo   net start GoldTierEmployee
    echo.
    echo To check status:
    echo   sc query GoldTierEmployee
    echo.
    echo To view logs:
    echo   service_logs\service_stdout.log
    echo.
    echo The service will start automatically on system boot.
    echo ============================================================
) else (
    echo.
    echo [ERROR] Service installation failed
    echo.
    echo Troubleshooting:
    echo 1. Ensure NSSM is downloaded to tools\nssm.exe
    echo 2. Download from: https://nssm.cc/download
    echo 3. Check Python path is correct
    echo.
)

pause
