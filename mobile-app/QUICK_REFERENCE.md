# 📱 Quick Reference - Mobile App

## 🚀 Γρήγορη Εκκίνηση

### 1. Εγκατάσταση (Μία Φορά)
```powershell
cd mobile-app
npm install
```

### 2. Ξεκίνημα Backend
```powershell
cd backend\api
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### 3. Ξεκίνημα Mobile App
```powershell
cd mobile-app
.\start.ps1
```
**Ή χειροκίνητα:**
```powershell
npm start
```

### 4. Σύνδεση
- Άνοιξε **Expo Go** στο κινητό
- Σκανάρισε το **QR code**
- Περίμενε να φορτώσει

---

## 📱 Expo Go Download

**Android:**  
https://play.google.com/store/apps/details?id=host.exp.exponent

**iOS:**  
https://apps.apple.com/app/expo-go/id982107779

---

## 🔧 Troubleshooting

### Network Error?
```powershell
# 1. Βρες το IP σου
ipconfig
# Κοίτα για IPv4 Address (π.χ. 192.168.1.100)

# 2. Ενημέρωσε app.json
# Άλλαξε το apiUrl σε "http://ΤΟ_IP_ΣΟΥ:8000"

# 3. Restart Expo
npm start
```

### Module Not Found?
```powershell
rm -rf node_modules
npm install
```

### Metro Bundler Error?
```powershell
npm start -- --clear
```

### Backend Not Responding?
```powershell
# Restart backend
Get-Process python | Stop-Process -Force
cd backend\api
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### Firewall Blocking?
```powershell
# Run as Administrator
New-NetFirewallRule -DisplayName "Expo Backend" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow
```

---

## 🎯 Test Credentials

```
Email: test@example.com
Password: testpassword123
```

**Ή δημιούργησε νέο λογαριασμό μέσω Register!**

---

## 📁 Αρχεία Ρυθμίσεων

### app.json - Άλλαξε το IP σου
```json
{
  "expo": {
    "extra": {
      "apiUrl": "http://192.168.1.100:8000"  ← ΑΛΛΑΞΕ ΕΔΩ
    }
  }
}
```

---

## 🔥 Χρήσιμα Commands

```powershell
# Ξεκίνημα
npm start

# Ξεκίνημα με clear cache
npm start -- --clear

# Android over USB
npm run android

# iOS Simulator (Mac μόνο)
npm run ios

# Stop όλα τα Python processes
Get-Process python | Stop-Process -Force
```

---

## 📋 Checklist

Πριν τρέξεις:
- [ ] Node.js installed
- [ ] Expo Go στο κινητό
- [ ] Backend τρέχει (`--host 0.0.0.0`)
- [ ] IP στο app.json correct
- [ ] Same WiFi (phone + PC)
- [ ] Firewall allows port 8000

---

## 🆘 Βοήθεια

**Full Documentation:**
- `README.md` - Overview
- `SETUP_GUIDE.md` - Βήμα-βήμα οδηγίες
- `COMPLETE_GUIDE.md` - Πλήρης τεκμηρίωση

**Support:**
- Expo Docs: https://docs.expo.dev
- React Native: https://reactnative.dev
- React Navigation: https://reactnavigation.org

---

## ✅ Features

- ✅ Login/Register
- ✅ JWT Auth με auto-refresh
- ✅ 2FA Support
- ✅ Portfolio Management
- ✅ Buy/Sell Assets
- ✅ CSRF Protection
- ✅ Secure Token Storage
- ✅ Material Design UI

---

**Quick Start:** `.\start.ps1` → Scan QR → Done! 🚀
