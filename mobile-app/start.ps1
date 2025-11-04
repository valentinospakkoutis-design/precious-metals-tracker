# Quick Start Script για Mobile App

Write-Host "🚀 Financial Security Mobile App - Quick Start" -ForegroundColor Green
Write-Host "=" -ForegroundColor Green -NoNewline; Write-Host ("=" * 50) -ForegroundColor Green
Write-Host ""

# Step 1: Check Node.js
Write-Host "📋 Step 1: Checking Node.js installation..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version
    $npmVersion = npm --version
    Write-Host "✅ Node.js: $nodeVersion" -ForegroundColor Green
    Write-Host "✅ npm: $npmVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js not found! Install from: https://nodejs.org/" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 2: Get local IP
Write-Host "📋 Step 2: Getting your IP address..." -ForegroundColor Yellow
$ip = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -like "192.168.*" -or $_.IPAddress -like "10.*"}).IPAddress | Select-Object -First 1

if ($ip) {
    Write-Host "✅ Your IP: $ip" -ForegroundColor Green
    Write-Host "   ⚠️  Make sure your phone is on the same WiFi!" -ForegroundColor Cyan
} else {
    Write-Host "⚠️  Could not detect IP automatically" -ForegroundColor Yellow
    $ip = Read-Host "   Please enter your IP address manually (e.g., 192.168.1.100)"
}
Write-Host ""

# Step 3: Update app.json
Write-Host "📋 Step 3: Updating app.json with your IP..." -ForegroundColor Yellow
$appJsonPath = "app.json"
if (Test-Path $appJsonPath) {
    $appJson = Get-Content $appJsonPath -Raw | ConvertFrom-Json
    $appJson.expo.extra.apiUrl = "http://${ip}:8000"
    $appJson | ConvertTo-Json -Depth 10 | Set-Content $appJsonPath
    Write-Host "✅ Updated API URL to: http://${ip}:8000" -ForegroundColor Green
} else {
    Write-Host "❌ app.json not found!" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 4: Check if node_modules exists
Write-Host "📋 Step 4: Checking dependencies..." -ForegroundColor Yellow
if (Test-Path "node_modules") {
    Write-Host "✅ Dependencies already installed" -ForegroundColor Green
    $install = Read-Host "   Do you want to reinstall? (y/n)"
    if ($install -eq "y") {
        Write-Host "   Installing dependencies..." -ForegroundColor Cyan
        npm install
    }
} else {
    Write-Host "   Installing dependencies (this will take 2-5 minutes)..." -ForegroundColor Cyan
    npm install
    Write-Host "✅ Dependencies installed" -ForegroundColor Green
}
Write-Host ""

# Step 5: Check backend
Write-Host "📋 Step 5: Checking backend connection..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://${ip}:8000/api/v1/health" -Method GET -TimeoutSec 3
    Write-Host "✅ Backend is running!" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Backend not responding at http://${ip}:8000" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "   Start backend with:" -ForegroundColor Cyan
    Write-Host "   cd ..\backend\api" -ForegroundColor White
    Write-Host "   python -m uvicorn main:app --host 0.0.0.0 --port 8000" -ForegroundColor White
    Write-Host ""
    $continue = Read-Host "   Continue anyway? (y/n)"
    if ($continue -ne "y") {
        exit 1
    }
}
Write-Host ""

# Step 6: Instructions
Write-Host "📋 Step 6: Ready to start!" -ForegroundColor Yellow
Write-Host ""
Write-Host "=" -ForegroundColor Green -NoNewline; Write-Host ("=" * 50) -ForegroundColor Green
Write-Host "NEXT STEPS:" -ForegroundColor Green -BackgroundColor Black
Write-Host "=" -ForegroundColor Green -NoNewline; Write-Host ("=" * 50) -ForegroundColor Green
Write-Host ""
Write-Host "1. Open Expo Go app on your phone" -ForegroundColor White
Write-Host "   📱 Android: https://play.google.com/store/apps/details?id=host.exp.exponent" -ForegroundColor Cyan
Write-Host "   📱 iOS: https://apps.apple.com/app/expo-go/id982107779" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. Make sure your phone is on the same WiFi as this computer" -ForegroundColor White
Write-Host "   Your IP: $ip" -ForegroundColor Cyan
Write-Host ""
Write-Host "3. Starting Expo server..." -ForegroundColor White
Write-Host ""
Write-Host "=" -ForegroundColor Green -NoNewline; Write-Host ("=" * 50) -ForegroundColor Green
Write-Host ""

# Step 7: Start Expo
Start-Sleep -Seconds 2
Write-Host "🚀 Starting Expo..." -ForegroundColor Green
Write-Host ""

npm start
