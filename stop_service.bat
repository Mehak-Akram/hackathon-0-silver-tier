@echo off
REM Stop Gold Tier Employee Service

echo Stopping Gold Tier Employee service...
net stop GoldTierEmployee

if %errorLevel% equ 0 (
    echo [SUCCESS] Service stopped successfully
) else (
    echo [ERROR] Failed to stop service
    echo The service may not be running
)

pause
