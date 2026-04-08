@echo off
REM Startup script for Gold Tier Autonomous AI Employee (Windows)

echo ==========================================
echo Gold Tier Autonomous AI Employee
echo ==========================================
echo.

REM Check if virtual environment exists
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
    echo Virtual environment created
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM Install/update dependencies
echo Installing dependencies...
pip install -q -r requirements.txt

REM Check if .env exists
if not exist ".env" (
    echo .env file not found. Copying from .env.example...
    copy .env.example .env
    echo Please edit .env with your credentials before continuing
    pause
    exit /b 1
)

REM Create required directories
echo Creating required directories...
if not exist "Needs_Action" mkdir Needs_Action
if not exist "Plans" mkdir Plans
if not exist "Done" mkdir Done
if not exist "Pending_Approval" mkdir Pending_Approval
if not exist "Briefings" mkdir Briefings
if not exist "Audit_Logs" mkdir Audit_Logs
if not exist "logs" mkdir logs

echo.
echo ==========================================
echo Starting Gold Tier AI Employee...
echo ==========================================
echo.

REM Start MCP server in background
echo Starting MCP Server...
start /B python mcp_server\server.py > logs\mcp-server.log 2>&1

REM Wait for MCP server to start
timeout /t 2 /nobreak >nul

REM Start orchestrator
echo Starting Orchestrator...
python orchestrator\main.py

echo.
echo Shutting down...
echo Stopped
