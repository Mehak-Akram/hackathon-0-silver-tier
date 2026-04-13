@echo off
REM Production Configuration Launcher

echo ============================================================
echo PRODUCTION CONFIGURATION WIZARD
echo ============================================================
echo.
echo This wizard will help you configure:
echo   - Odoo CRM credentials
echo   - Gmail email (IMAP + SMTP)
echo   - Health monitoring
echo   - Alerting system
echo   - CEO briefing system
echo.
echo Your credentials will be saved to .env file (not in Git).
echo.
echo Press any key to start the wizard...
pause >nul

python configure_production.py

if %errorLevel% equ 0 (
    echo.
    echo ============================================================
    echo CONFIGURATION SUCCESSFUL
    echo ============================================================
    echo.
    echo Next step: Test your configuration
    echo   Run: test_production_setup.bat
    echo.
) else (
    echo.
    echo ============================================================
    echo CONFIGURATION FAILED OR CANCELLED
    echo ============================================================
    echo.
    echo You can run the wizard again anytime:
    echo   python configure_production.py
    echo.
)

pause
