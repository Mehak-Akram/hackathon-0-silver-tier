@echo off
REM Production Setup Test Launcher

echo ============================================================
echo PRODUCTION SETUP TEST SUITE
echo ============================================================
echo.
echo This will test all components of your production setup:
echo   - Odoo CRM connection and operations
echo   - Email (IMAP + SMTP) connectivity
echo   - Health monitoring system
echo   - Metrics aggregation
echo   - CEO briefing generation
echo   - Task processing
echo.
echo Make sure you have configured your credentials first:
echo   Run: configure_production.bat
echo.
echo Press any key to start testing...
pause >nul

python test_production_setup.py

if %errorLevel% equ 0 (
    echo.
    echo ============================================================
    echo ALL TESTS PASSED - READY FOR PRODUCTION
    echo ============================================================
    echo.
    echo Next step: Start the autonomous loop
    echo   Development mode: start_autonomous_loop.bat
    echo   Production mode: install_service.bat (requires NSSM)
    echo.
) else (
    echo.
    echo ============================================================
    echo SOME TESTS FAILED - FIX ISSUES BEFORE PRODUCTION
    echo ============================================================
    echo.
    echo Review the test output above to identify issues.
    echo Common fixes:
    echo   - Email: Use Gmail App Password (not regular password)
    echo   - Odoo: Verify credentials in .env file
    echo   - Network: Check firewall and internet connection
    echo.
    echo After fixing, run this test again.
    echo.
)

pause
