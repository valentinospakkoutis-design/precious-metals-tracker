# 📱 Εγκατάσταση Flutter SDK - Βήμα προς Βήμα

## 1️⃣ Download Flutter SDK

### Μέθοδος A: Χειροκίνητα (Προτεινόμενη)
1. Πήγαινε: https://docs.flutter.dev/get-started/install/windows
2. Κατέβασε το **flutter_windows_3.24.x-stable.zip** (~1.5GB)
3. Εξάγαγε το σε: `C:\src\flutter`

### Μέθοδος B: Με Git (αν έχεις Git)
```powershell
cd C:\src
git clone https://github.com/flutter/flutter.git -b stable
```

## 2️⃣ Προσθήκη στο PATH

### Βήμα 1: Άνοιξε System Environment Variables
```powershell
# Τρέξε αυτό για να ανοίξεις τις ρυθμίσεις
rundll32 sysdm.cpl,EditEnvironmentVariables
```

### Βήμα 2: Επεξεργασία PATH
1. Στο **User variables**, επίλεξε **Path** → **Edit**
2. Πάτησε **New**
3. Πρόσθεσε: `C:\src\flutter\bin`
4. Πάτησε **OK** σε όλα τα παράθυρα

### Βήμα 3: Επανεκκίνηση PowerShell
Κλείσε και ξανάνοιξε το PowerShell για να φορτώσει το νέο PATH.

## 3️⃣ Επαλήθευση Εγκατάστασης

```powershell
# Έλεγχος εγκατάστασης
flutter --version

# Διάγνωση συστήματος
flutter doctor
```

**Αναμενόμενο αποτέλεσμα:**
```
Flutter 3.24.x • channel stable
Tools • Dart 3.5.x • DevTools 2.37.x
```

## 4️⃣ Εγκατάσταση Android Studio (για Android development)

### Γιατί το χρειάζεσαι:
- Android SDK
- Android Emulator
- Build tools

### Βήματα:
1. Download: https://developer.android.com/studio
2. Εγκατέστησε με τις default ρυθμίσεις
3. Άνοιξε Android Studio → **More Actions** → **SDK Manager**
4. Εγκατέστησε:
   - Android SDK Platform (latest)
   - Android SDK Command-line Tools
   - Android Emulator

### Αποδοχή Android Licenses
```powershell
flutter doctor --android-licenses
# Πάτησε 'y' για όλες τις άδειες
```

## 5️⃣ Δημιουργία Virtual Device (Emulator)

```powershell
# Εμφάνιση διαθέσιμων devices
flutter emulators

# Άνοιγμα Android Studio για δημιουργία AVD
# Tools → Device Manager → Create Virtual Device
# Επίλεξε: Pixel 7 Pro, Android 14 (API 34)
```

## 6️⃣ Εγκατάσταση VS Code Extensions (Προαιρετικά)

```powershell
# Flutter extension
code --install-extension Dart-Code.flutter

# Dart extension  
code --install-extension Dart-Code.dart-code
```

## 7️⃣ Τελικός Έλεγχος

```powershell
flutter doctor -v
```

**Στόχος: Όλα να είναι ✓ (ή τουλάχιστον Flutter, Android SDK)**

```
Doctor summary (to see all details, run flutter doctor -v):
[✓] Flutter (Channel stable, 3.24.x)
[✓] Windows Version (Windows 10/11)
[✓] Android toolchain - develop for Android devices
[✓] Chrome - develop for the web
[✓] Visual Studio Code (version 1.x)
[✓] Connected device (1 available)
```

## 8️⃣ Τρέξιμο της Εφαρμογής

```powershell
cd C:\Users\valen\OneDrive\Desktop\Codes\new-project\mobile_app

# Εγκατάσταση dependencies
flutter pub get

# Εμφάνιση διαθέσιμων devices
flutter devices

# Εκκίνηση emulator
flutter emulators --launch <emulator_id>

# Τρέξιμο app
flutter run
```

## 🎯 Quick Start Script

Αφού εγκαταστήσεις το Flutter SDK, τρέξε:

```powershell
# Μονοαράδα για setup
flutter doctor --android-licenses; cd C:\Users\valen\OneDrive\Desktop\Codes\new-project\mobile_app; flutter pub get; flutter run
```

## ⚠️ Συνηθισμένα Προβλήματα

### "flutter is not recognized"
- ❌ Πρόβλημα: Το PATH δεν ενημερώθηκε
- ✅ Λύση: Επανεκκίνησε το PowerShell/VS Code

### "Android licenses not accepted"
- ❌ Πρόβλημα: Δεν έχεις αποδεχτεί τις άδειες
- ✅ Λύση: `flutter doctor --android-licenses`

### "No devices available"
- ❌ Πρόβλημα: Δεν τρέχει emulator
- ✅ Λύση: Άνοιξε Android Studio → Device Manager → Start emulator

### Build errors στο app
- ❌ Πρόβλημα: Παλιές εκδόσεις
- ✅ Λύση: 
  ```powershell
  flutter clean
  flutter pub get
  flutter run
  ```

## 📊 Χρόνος Εγκατάστασης

- Download Flutter SDK: ~10-15 λεπτά (ανάλογα με internet)
- Download Android Studio: ~5-10 λεπτά
- Setup & configuration: ~10-15 λεπτά
- **Σύνολο: ~30-40 λεπτά**

## 🚀 Επόμενα Βήματα (μετά την εγκατάσταση)

1. ✅ Εγκατέστησε Flutter SDK
2. ✅ Setup Android Studio & Emulator
3. ✅ Τρέξε `flutter pub get` στο mobile_app/
4. ✅ Τρέξε `flutter run` για demo
5. 🔄 Σύνδεσε με το FastAPI backend (http://localhost:8000)
6. 🔄 Implement real-time price updates
7. 🔄 Add charts & notifications

## 💡 Alternative: Web Preview (Χωρίς Android)

Αν δεν θέλεις να εγκαταστήσεις Android Studio:

```powershell
# Τρέξε σε Chrome browser
flutter run -d chrome
```

Απλούστερο αλλά λιγότερο realistic για mobile UX.
