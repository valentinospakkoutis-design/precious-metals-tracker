@echo off
REM Financial Prediction API Server Launcher
REM Ensures stable server startup

echo ========================================
echo  Financial Prediction API Server
echo ========================================
echo.

REM Kill any existing Python processes
echo [1/4] Stopping existing Python processes...
taskkill /F /IM python.exe 2>nul
timeout /t 2 /nobreak >nul

REM Check if PostgreSQL is running
echo [2/4] Checking PostgreSQL...
docker ps | findstr financial-postgres >nul
if errorlevel 1 (
    echo   ERROR: PostgreSQL container not running!
    echo   Run: docker start financial-postgres
    pause
    exit /b 1
)
echo   PostgreSQL: OK

REM Check if Redis is running
echo [3/4] Checking Redis...
docker ps | findstr redis >nul
if errorlevel 1 (
    echo   WARNING: Redis container not running
    echo   Starting Redis...
    docker start redis 2>nul
    timeout /t 3 /nobreak >nul
)
echo   Redis: OK

REM Start the server
echo [4/4] Starting FastAPI server...
echo.
echo Server will start on: http://127.0.0.1:8001
echo Press Ctrl+C to stop the server
echo.
echo ========================================
echo.

cd /d "%~dp0backend\api"
python -m uvicorn main:app --host 127.0.0.1 --port 8001

pause
