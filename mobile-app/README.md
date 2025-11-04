# Financial Security Mobile App

React Native mobile application για το Financial Security API.

## 🚀 Εγκατάσταση & Εκτέλεση

### Προαπαιτούμενα
- Node.js 18+ εγκατεστημένο
- Expo Go app στο κινητό σου (Android/iOS)
- Backend API running (http://192.168.1.100:8000)

### Βήματα Εγκατάστασης

1. **Μπες στο φάκελο του mobile app:**
```bash
cd mobile-app
```

2. **Εγκατέστησε τις εξαρτήσεις:**
```bash
npm install
```

3. **Ρύθμισε το API URL:**
Άνοιξε το `app.json` και άλλαξε το `apiUrl` στο IP του υπολογιστή σου:
```json
{
  "expo": {
    "extra": {
      "apiUrl": "http://192.168.1.100:8000"
    }
  }
}
```

**Σημαντικό:** Βρες το IP σου με:
- Windows: `ipconfig` (βρες το IPv4 Address)
- Mac/Linux: `ifconfig` ή `ip addr`

4. **Ξεκίνα το Expo:**
```bash
npm start
```

5. **Σκανάρισε το QR code:**
- Άνοιξε το **Expo Go** στο κινητό σου
- Σκανάρισε το QR code που εμφανίζεται
- Περίμενε να φορτώσει η εφαρμογή

## 📱 Χαρακτηριστικά

### ✅ Έτοιμα Features
- 🔐 **Authentication** - Login/Register
- 🔒 **2FA Support** - Two-factor authentication
- 💼 **Portfolio Management** - Δες το portfolio σου
- 📈 **Trading** - Buy/Sell assets
- 🔄 **Auto Token Refresh** - Αυτόματη ανανέωση tokens
- 💾 **Secure Storage** - Ασφαλής αποθήκευση credentials

### 📱 Οθόνες
1. **Login Screen** - Σύνδεση με email/password + 2FA
2. **Register Screen** - Δημιουργία λογαριασμού
3. **Portfolio Screen** - Προβολή positions & P/L
4. **Trade Screen** - Buy/Sell assets
5. **Settings Screen** - User info & Logout

## 🔧 Ρυθμίσεις API

### Backend CORS Configuration
Για να δουλέψει το mobile app, πρέπει να προσθέσεις το IP σου στα allowed origins:

Στο `backend/api/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://192.168.1.100:8000",  # ΤΟ IP ΣΟΥ
        "http://*",  # ή αυτό για development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Εκκίνηση Backend
```bash
cd backend/api
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

**Σημαντικό:** Χρησιμοποίησε `--host 0.0.0.0` για να είναι προσβάσιμο από το κινητό!

## 🧪 Testing

### Test Login
```
Email: test@example.com
Password: testpassword123
```

### Test με δικό σου account
1. Register από το app
2. Login με τα credentials σου
3. Trade assets
4. Δες το portfolio σου

## 📁 Δομή Έργου

```
mobile-app/
├── App.tsx                 # Main app component
├── app.json               # Expo configuration
├── package.json           # Dependencies
├── babel.config.js        # Babel config
│
├── src/
│   ├── context/
│   │   └── AuthContext.tsx    # Authentication context
│   │
│   ├── services/
│   │   └── api.ts             # API client με axios
│   │
│   └── screens/
│       ├── LoginScreen.tsx     # Login οθόνη
│       ├── RegisterScreen.tsx  # Registration οθόνη
│       ├── PortfolioScreen.tsx # Portfolio προβολή
│       └── TradeScreen.tsx     # Trading οθόνη
│
└── assets/                # Icons, images, etc.
```

## 🎨 UI Components

Χρησιμοποιεί **React Native Paper** για Material Design:
- TextInput - Input fields
- Button - Buttons
- Card - Container cards
- Title, Paragraph - Typography
- ActivityIndicator - Loading states
- SegmentedButtons - Buy/Sell toggle

## 🔐 Security Features

### Secure Token Storage
- Access tokens αποθηκεύονται σε **SecureStore** (encrypted)
- Refresh tokens σε **SecureStore**
- User data σε **AsyncStorage**

### Auto Token Refresh
```typescript
// Αυτόματη ανανέωση όταν λήξει το access token
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Προσπάθησε refresh
      const newToken = await refreshToken();
      // Retry original request
    }
  }
);
```

### CSRF Protection
- Αυτόματη αποστολή CSRF tokens
- Header: `X-CSRF-Token`

## 🐛 Troubleshooting

### "Network Error"
- ✅ Έλεγξε ότι backend τρέχει: `http://YOUR_IP:8000/docs`
- ✅ Έλεγξε ότι κινητό & PC είναι στο ίδιο WiFi
- ✅ Έλεγξε firewall settings

### "Cannot connect to API"
- ✅ Άλλαξε το IP στο `app.json`
- ✅ Restart Expo server: `npm start`
- ✅ Clear cache: `expo start -c`

### "Module not found"
- ✅ Τρέξε: `npm install`
- ✅ Restart Metro bundler

### CORS Errors
- ✅ Πρόσθεσε το IP σου στα `allow_origins`
- ✅ Restart backend server

## 📦 Dependencies

### Core
- `expo` - Expo framework
- `react` - React library
- `react-native` - React Native framework

### UI
- `react-native-paper` - Material Design components
- `@expo/vector-icons` - Icon library
- `react-native-svg` - SVG support

### Navigation
- `@react-navigation/native` - Navigation framework
- `@react-navigation/stack` - Stack navigator
- `@react-navigation/bottom-tabs` - Tab navigator

### Storage
- `@react-native-async-storage/async-storage` - AsyncStorage
- `expo-secure-store` - Encrypted storage

### Networking
- `axios` - HTTP client

### Camera (για 2FA QR codes)
- `expo-camera` - Camera access
- `expo-barcode-scanner` - QR code scanning

## 🚧 Future Features

- [ ] 2FA QR Code Scanning
- [ ] Push Notifications
- [ ] Real-time price updates
- [ ] News feed
- [ ] ML Predictions view
- [ ] Charts & Analytics
- [ ] Dark mode
- [ ] Fingerprint/Face ID authentication

## 📝 Σημειώσεις

### Development
- Hot reload ενεργοποιημένο (shake device → "Reload")
- Debug menu: Shake device
- Chrome DevTools: `j` στο terminal

### Production Build
```bash
# Android
expo build:android

# iOS (χρειάζεται Mac)
expo build:ios
```

## 🆘 Support

Αν αντιμετωπίσεις προβλήματα:
1. Έλεγξε το [Expo documentation](https://docs.expo.dev)
2. Restart Expo server
3. Clear cache: `expo start -c`
4. Reinstall dependencies: `rm -rf node_modules && npm install`

---

**Status**: ✅ Ready για Expo Go  
**Version**: 1.0.0  
**Platform**: Android & iOS  
**Framework**: React Native + Expo
