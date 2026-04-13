@echo off
REM NSSM Download and Installation Guide

echo ============================================================
echo NSSM Installation Instructions
echo ============================================================
echo.
echo NSSM (Non-Sucking Service Manager) is required to run the
echo autonomous employee as a Windows service.
echo.
echo STEP 1: Download NSSM
echo ----------------------
echo 1. Open your browser
echo 2. Go to: https://nssm.cc/download
echo 3. Download the latest version (nssm-2.24.zip or newer)
echo 4. Extract the ZIP file
echo.
echo STEP 2: Copy NSSM to Project
echo -----------------------------
echo 1. Open the extracted folder
echo 2. Navigate to: win64 folder (for 64-bit Windows)
echo 3. Copy nssm.exe
echo 4. Paste it here: %~dp0tools\nssm.exe
echo.
echo Creating tools directory...
mkdir "%~dp0tools" 2>nul
echo.
echo STEP 3: Verify Installation
echo ---------------------------
echo After copying nssm.exe, run:
echo   python verify_deployment.py
echo.
echo The NSSM check should pass.
echo.
echo ============================================================
echo.
echo Press any key when you've completed the steps above...
pause >nul
echo.
echo Verifying NSSM installation...
echo.

if exist "%~dp0tools\nssm.exe" (
    echo [SUCCESS] NSSM found at: %~dp0tools\nssm.exe
    echo.
    echo You can now proceed with service installation:
    echo   install_service.bat
) else (
    echo [ERROR] NSSM not found at: %~dp0tools\nssm.exe
    echo.
    echo Please follow the steps above to download and copy NSSM.
)

echo.
pause
