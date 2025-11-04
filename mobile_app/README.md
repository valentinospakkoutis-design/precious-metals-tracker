# Financial Prediction Mobile App

## Εγκατάσταση Flutter

### Windows:
1. Κατέβασε Flutter SDK: https://flutter.dev/docs/get-started/install/windows
2. Εξάγαγε το σε `C:\src\flutter`
3. Πρόσθεσε στο PATH: `C:\src\flutter\bin`
4. Τρέξε: `flutter doctor`

### Εγκατάσταση Android Studio (για emulator):
1. Κατέβασε: https://developer.android.com/studio
2. Εγκατέστησε Android SDK
3. Δημιούργησε Virtual Device (AVD)

## Εκτέλεση App

```bash
cd mobile_app

# Εγκατάσταση dependencies
flutter pub get

# Τρέξε στο emulator
flutter run

# Ή build APK
flutter build apk
```

## Χαρακτηριστικά

✅ Dark Fintech Theme (μαύρο/μπλε)
✅ 3 Tabs: Μέταλλα, Κρυπτονομίσματα, Shitcoins
✅ Κάρτες assets με τιμές και % αλλαγή
✅ Detail page με προβλέψεις (10/20/30 min)
✅ News & Sentiment integration
✅ Ελληνική γλώσσα UI

## Επόμενα Βήματα

🔄 Σύνδεση με το FastAPI backend
🔄 Real-time price updates
🔄 Charts με fl_chart
🔄 Push notifications για alerts
🔄 Portfolio tracking
