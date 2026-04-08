@echo off
REM Start Gold Tier Employee Service

echo Starting Gold Tier Employee service...
net start GoldTierEmployee

if %errorLevel% equ 0 (
    echo [SUCCESS] Service started successfully
    echo.
    echo Check status: sc query GoldTierEmployee
    echo View logs: service_logs\service_stdout.log
) else (
    echo [ERROR] Failed to start service
    echo Check service_logs\service_stderr.log for errors
)

pause
