@echo off
cd /d "C:\Users\valen\OneDrive\Desktop\Codes\new-project\backend\api"
set PYTHONPATH=C:\Users\valen\OneDrive\Desktop\Codes\new-project\backend
echo.
echo ========================================
echo   Backend Server - FastAPI
echo ========================================
echo.
echo Server: http://0.0.0.0:8000
echo Docs:   http://192.168.178.33:8000/docs
echo.
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
pause
