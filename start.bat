@echo off
REM Startup script for Agentic SQL Data Analyst on Windows

echo.
echo ====================================================================
echo  Agentic SQL Data Analyst - Startup Script
echo ====================================================================
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo [INFO] Virtual environment not found. Creating...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        exit /b 1
    )
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/upgrade dependencies
echo [INFO] Checking dependencies...
pip install -q -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    exit /b 1
)

REM Check .env file
if not exist ".env" (
    echo [WARNING] .env file not found
    echo [INFO] Creating .env from .env.example...
    copy .env.example .env
    echo [INFO] Please edit .env with your actual credentials
    echo.
    pause
)

REM Display startup info
set "CHAINLIT_PORT=%CHAINLIT_PORT%"
if not defined CHAINLIT_PORT set "CHAINLIT_PORT=8000"

for /L %%P in (8000,1,8100) do (
    powershell -NoProfile -Command "$p = %%P; if (-not (Get-NetTCPConnection -LocalPort $p -ErrorAction SilentlyContinue)) { exit 0 } else { exit 1 }" >nul 2>&1
    if not errorlevel 1 (
        set "CHAINLIT_PORT=%%P"
        goto port_found
    )
)

echo [ERROR] No free port found between 8000 and 8100.
exit /b 1

:port_found
echo.
echo ====================================================================
echo [SUCCESS] All checks passed!
echo.
echo Starting Chainlit application...
echo The UI will open at: http://localhost:%CHAINLIT_PORT%
echo.
echo Press Ctrl+C to stop the server
echo ====================================================================
echo.

REM Start Chainlit
chainlit run app.py -w --port %CHAINLIT_PORT%

pause
