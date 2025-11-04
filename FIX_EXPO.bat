@echo off
echo.
echo ========================================
echo   Upgrading to Expo SDK 54
echo ========================================
echo.
cd /d "C:\Users\valen\OneDrive\Desktop\Codes\new-project\mobile-app"
echo Running Expo upgrade command...
echo.
npx expo install --fix
echo.
echo ========================================
echo   Upgrade Complete!
echo ========================================
echo.
pause
