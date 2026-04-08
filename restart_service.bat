@echo off
REM Restart Gold Tier Employee Service

echo Restarting Gold Tier Employee service...
echo.

echo [1/2] Stopping service...
net stop GoldTierEmployee

timeout /t 3 /nobreak >nul

echo [2/2] Starting service...
net start GoldTierEmployee

if %errorLevel% equ 0 (
    echo.
    echo [SUCCESS] Service restarted successfully
    echo.
    echo Check status: sc query GoldTierEmployee
) else (
    echo.
    echo [ERROR] Failed to restart service
    echo Check service_logs\service_stderr.log for errors
)

pause
