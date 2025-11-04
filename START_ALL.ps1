# START_ALL.ps1 - Ξεκινάει Backend + Mobile App

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Financial Security - Startup Script  " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Βρες το IP
Write-Host "[1/4] Βρίσκω το IP address..." -ForegroundColor Yellow
$ip = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -like "192.168.*"} | Select-Object -First 1).IPAddress
if (-not $ip) {
    Write-Host "ERROR: Δεν βρέθηκε IP address!" -ForegroundColor Red
    exit 1
}
Write-Host "      IP: $ip" -ForegroundColor Green
Write-Host ""

# 2. Ενημέρωσε app.json
Write-Host "[2/4] Ενημερώνω app.json με IP $ip..." -ForegroundColor Yellow
$appJsonPath = "$PSScriptRoot\mobile-app\app.json"
$appJson = Get-Content $appJsonPath -Raw | ConvertFrom-Json
$appJson.expo.extra.apiUrl = "http://${ip}:8000"
$appJson | ConvertTo-Json -Depth 10 | Set-Content $appJsonPath
Write-Host "      Done!" -ForegroundColor Green
Write-Host ""

# 3. Ξεκίνα το Backend σε νέο παράθυρο
Write-Host "[3/4] Ξεκινάω Backend σε νέο terminal..." -ForegroundColor Yellow
$backendPath = "$PSScriptRoot\backend\api"
$pythonPath = "$PSScriptRoot\backend"

# Δημιούργησε batch file για backend
$backendBatch = @"
@echo off
cd /d "$backendPath"
set PYTHONPATH=$pythonPath
echo.
echo ========================================
echo   Backend Server - FastAPI
echo ========================================
echo.
echo Server: http://0.0.0.0:8000
echo Health: http://${ip}:8000/api/v1/health
echo Docs:   http://${ip}:8000/docs
echo.
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
pause
"@
$backendBatchPath = "$PSScriptRoot\run_backend.bat"
$backendBatch | Out-File -FilePath $backendBatchPath -Encoding ASCII

Start-Process cmd.exe -ArgumentList "/k", $backendBatchPath
Write-Host "      Backend ξεκίνησε!" -ForegroundColor Green
Write-Host ""

# 4. Περίμενε το backend να ξεκινήσει
Write-Host "[4/4] Περιμένω το backend να ξεκινήσει..." -ForegroundColor Yellow
Start-Sleep -Seconds 8
Write-Host "      Done!" -ForegroundColor Green
Write-Host ""

# 5. Ξεκίνα το Expo σε νέο παράθυρο
Write-Host "[5/4] Ξεκινάω Expo σε νέο terminal..." -ForegroundColor Yellow
$mobilePath = "$PSScriptRoot\mobile-app"

# Δημιούργησε batch file για expo
$expoBatch = @"
@echo off
cd /d "$mobilePath"
echo.
echo ========================================
echo   Expo Development Server
echo ========================================
echo.
echo Scan QR code με το Expo Go app!
echo.
echo Αν δεν βλέπεις QR code, πάτα: Shift+M
echo.
npm start
pause
"@
$expoBatchPath = "$PSScriptRoot\run_expo.bat"
$expoBatch | Out-File -FilePath $expoBatchPath -Encoding ASCII

Start-Process cmd.exe -ArgumentList "/k", $expoBatchPath
Write-Host "      Expo ξεκίνησε!" -ForegroundColor Green
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "           ALL READY!                   " -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Backend:  http://${ip}:8000/docs" -ForegroundColor White
Write-Host "Mobile:   Scan QR code in Expo terminal" -ForegroundColor White
Write-Host ""
Write-Host "INSTRUCTIONS:" -ForegroundColor Yellow
Write-Host "1. Open Expo Go app on phone" -ForegroundColor White
Write-Host "2. Scan QR code from Expo terminal" -ForegroundColor White
Write-Host "3. Wait to load (~30 sec)" -ForegroundColor White
Write-Host "4. Test Login/Register!" -ForegroundColor White
Write-Host ""
Write-Host "If NO QR code:" -ForegroundColor Yellow
Write-Host "- Press Shift+M in Expo terminal" -ForegroundColor White
Write-Host "- Or type: exp://${ip}:8081" -ForegroundColor White
Write-Host ""
Write-Host "Press any key to close..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
