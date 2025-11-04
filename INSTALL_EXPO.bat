@echo off
echo.
echo ========================================
echo   Installing Expo SDK 54
echo ========================================
echo.
cd /d "C:\Users\valen\OneDrive\Desktop\Codes\new-project\mobile-app"
echo Installing with legacy peer deps...
echo This will take 2-3 minutes...
echo.
npm install --legacy-peer-deps
echo.
echo ========================================
echo   Installation Complete!
echo ========================================
echo.
echo Now run OPEN_EXPO.bat to start the app
echo.
pause
