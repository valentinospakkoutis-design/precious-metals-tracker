@echo off
cd /d "C:\Users\valen\OneDrive\Desktop\Codes\new-project\backend\api"
set PYTHONPATH=C:\Users\valen\OneDrive\Desktop\Codes\new-project\backend
echo.
echo ========================================
echo   Backend Server - FastAPI
echo ========================================
echo.
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
pause
