# 📱 Οδηγίες Εκτέλεσης Mobile App με Expo Go

## Βήμα 1: Εγκατάσταση Node.js & npm

Αν δεν έχεις Node.js:
1. Κατέβασε από https://nodejs.org/ (LTS version)
2. Εγκατέστησε το
3. Επιβεβαίωσε: `node --version` και `npm --version`

## Βήμα 2: Εγκατάσταση Expo Go στο Κινητό

### Android:
https://play.google.com/store/apps/details?id=host.exp.exponent

### iOS:
https://apps.apple.com/app/expo-go/id982107779

## Βήμα 3: Προετοιμασία Backend

### 1. Βρες το IP του υπολογιστή σου

**Windows (PowerShell):**
```powershell
ipconfig
```
Κοίτα για "IPv4 Address" κάτω από το Wi-Fi adapter.
Παράδειγμα: `192.168.1.100`

**Σημαντικό:** Το κινητό και ο υπολογιστής πρέπει να είναι στο **ίδιο WiFi**!

### 2. Ξεκίνα το Backend API

```powershell
cd C:\Users\valen\OneDrive\Desktop\Codes\new-project\backend\api
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

**Κρίσιμο:** Χρησιμοποίησε `--host 0.0.0.0` για να είναι προσβάσιμο από το δίκτυο!

### 3. Επιβεβαίωσε ότι λειτουργεί

Άνοιξε browser στο κινητό σου:
```
http://ΤΟ_IP_ΣΟΥ:8000/docs
```
Παράδειγμα: `http://192.168.1.100:8000/docs`

Αν δεν ανοίγει, έλεγξε:
- ✅ Firewall settings (Windows Defender Firewall)
- ✅ Το WiFi είναι το ίδιο σε PC και κινητό
- ✅ Το backend τρέχει με `--host 0.0.0.0`

## Βήμα 4: Ρύθμιση Mobile App

### 1. Άνοιξε νέο PowerShell terminal

```powershell
cd C:\Users\valen\OneDrive\Desktop\Codes\new-project\mobile-app
```

### 2. Εγκατάσταση Dependencies

```powershell
npm install
```

Αυτό θα κατεβάσει όλα τα packages (React Native, Expo, κλπ). Θα πάρει 2-5 λεπτά.

### 3. Ρύθμισε το API URL

Άνοιξε το αρχείο `mobile-app/app.json` και άλλαξε το IP:

```json
{
  "expo": {
    "extra": {
      "apiUrl": "http://192.168.1.100:8000"
    }
  }
}
```

**Αντικατέστησε το `192.168.1.100` με το δικό σου IP!**

## Βήμα 5: Εκτέλεση Expo

```powershell
npm start
```

Θα δεις κάτι τέτοιο:
```
› Metro waiting on exp://192.168.1.100:8081
› QR code: [ΜΕΓΑΛΟ QR CODE]
› Press s │ switch to development build
› Press a │ open Android
› Press i │ open iOS simulator
› Press w │ open web

› Press r │ reload app
› Press m │ toggle menu
› Press ? │ show all commands
```

## Βήμα 6: Σύνδεση με Expo Go

### 1. Άνοιξε Expo Go στο κινητό

### 2. Σκανάρισε το QR code

**Android:** 
- Πάτα "Scan QR Code" μέσα στο Expo Go
- Σκανάρισε το QR από το terminal

**iOS:**
- Άνοιξε την Camera app
- Σκανάρισε το QR code
- Πάτα το notification για να ανοίξεις στο Expo Go

### 3. Περίμενε να φορτώσει

Θα δεις:
```
Opening on Android...
Building JavaScript bundle...
100%
```

Σε 10-30 δευτερόλεπτα θα ανοίξει το app!

## Βήμα 7: Test το App

### 1. Register νέο account
- Email: `test@example.com`
- Password: `testpassword123`
- Full Name: `Test User`

### 2. Login
Μετά το registration θα κάνεις auto-login.

### 3. Δες το Portfolio
Θα είναι άδειο αρχικά.

### 4. Buy Asset
- Symbol: `AAPL`
- Quantity: `10`
- Price: `150`

### 5. Refresh Portfolio
Pull down για refresh - θα δεις το νέο position!

## 🔧 Troubleshooting

### "Network request failed"

**Λύση 1: Έλεγξε το IP**
```powershell
ipconfig
```
Σιγουρέψου ότι το IP στο `app.json` είναι σωστό.

**Λύση 2: Firewall**
Windows Defender μπορεί να μπλοκάρει το port 8000.

Άνοιξε PowerShell ως Administrator:
```powershell
New-NetFirewallRule -DisplayName "Expo Backend" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow
```

**Λύση 3: Backend restart**
```powershell
# Σκότωσε το Python
Get-Process python | Stop-Process -Force

# Ξεκίνα ξανά
cd C:\Users\valen\OneDrive\Desktop\Codes\new-project\backend\api
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### "Unable to resolve module"

**Λύση:**
```powershell
cd mobile-app
rm -rf node_modules
npm install
```

### "Metro bundler error"

**Λύση:**
```powershell
npm start -- --clear
```

### CORS Errors

Το backend έχει ήδη CORS enabled για development:
```python
configure_cors(app, environment="development")
```

Αν εξακολουθείς να βλέπεις CORS errors, restart το backend.

## 📱 Χρήση του App

### Login Screen
- Email & Password
- Support για 2FA (αν enabled)
- Link για Registration

### Portfolio Screen
- Δες όλα τα positions
- Total value & P/L
- Pull to refresh
- Buy/Sell buttons

### Trade Screen
- Toggle Buy/Sell
- Εισαγωγή Symbol, Quantity, Price
- Live total calculation
- CSRF protected

### Settings Screen
- User info
- 2FA status
- Logout button

## 🎯 Features που Λειτουργούν

✅ Authentication (Login/Register)
✅ JWT Token Management (auto-refresh)
✅ Portfolio View
✅ Buy/Sell Assets
✅ CSRF Protection
✅ Secure Token Storage
✅ Pull to Refresh
✅ Error Handling
✅ Loading States

## 🚧 Future Features

Έτοιμα για implementation:
- 2FA QR Scanning (camera ready)
- Real-time prices (WebSocket)
- ML Predictions view
- News feed
- Charts
- Push notifications

## 📝 Σημαντικά

### Development Mode
- Hot reload enabled (αλλαγές φαίνονται αυτόματα)
- Shake device → Debug menu
- Errors εμφανίζονται full screen

### Production Build
Όταν είσαι έτοιμος:
```powershell
# Build για Android
expo build:android

# Build για iOS (χρειάζεται Mac)
expo build:ios
```

### API Endpoints που Χρησιμοποιεί

- `POST /api/v1/auth/register` - Registration
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/refresh` - Token refresh
- `POST /api/v1/auth/logout` - Logout
- `GET /api/v1/portfolio` - Get portfolio
- `POST /api/v1/portfolio/buy` - Buy asset
- `POST /api/v1/portfolio/sell` - Sell asset
- `GET /api/v1/health` - Health check

## ✅ Checklist

Πριν τρέξεις το app:

- [ ] Node.js εγκατεστημένο
- [ ] Expo Go στο κινητό
- [ ] Backend τρέχει με `--host 0.0.0.0`
- [ ] IP στο `app.json` είναι σωστό
- [ ] Κινητό & PC στο ίδιο WiFi
- [ ] `npm install` completed
- [ ] Firewall επιτρέπει port 8000
- [ ] Backend health check works από κινητό

## 🎉 Επιτυχία!

Αν όλα πάνε καλά, θα δεις:
1. Login screen με το "Financial Security" logo
2. Smooth animations
3. Material Design UI
4. Functional authentication
5. Working portfolio management

Απόλαυσε το app! 🚀
