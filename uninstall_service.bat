@echo off
REM Uninstall Gold Tier Employee Windows Service
REM Requires Administrator privileges

echo ============================================================
echo Gold Tier Employee - Service Uninstallation
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

echo [WARNING] This will remove the Gold Tier Employee service
echo.
set /p confirm="Are you sure? (Y/N): "

if /i not "%confirm%"=="Y" (
    echo Uninstallation cancelled
    pause
    exit /b 0
)

echo.
echo [INFO] Uninstalling service...
echo.

REM Run service manager
python deployment\service_manager.py uninstall

if %errorLevel% equ 0 (
    echo.
    echo ============================================================
    echo Service uninstalled successfully!
    echo ============================================================
    echo.
    echo The service has been removed from Windows Services.
    echo Service logs are preserved in service_logs\ folder.
    echo ============================================================
) else (
    echo.
    echo [ERROR] Service uninstallation failed
    echo.
)

pause
