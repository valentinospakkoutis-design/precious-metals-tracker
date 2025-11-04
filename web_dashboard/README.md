# 🌐 Web Dashboard

## Εκτέλεση

### Μέθοδος 1: VS Code Live Server (Προτεινόμενο)
1. Εγκατάσταση Live Server extension
2. Right-click στο `index.html` → "Open with Live Server"
3. Άνοιγμα: http://localhost:5500

### Μέθοδος 2: Python HTTP Server
```powershell
cd web_dashboard
python -m http.server 5500
```
Άνοιγμα: http://localhost:5500

### Μέθοδος 3: Άνοιγμα απευθείας
Double-click το `index.html` (αλλά χρειάζεται CORS configuration)

## Προαπαιτούμενα

**Το FastAPI backend πρέπει να τρέχει:**
```powershell
cd backend/api
python main.py
```

## Χαρακτηριστικά

✅ Real-time τιμές για όλα τα assets
✅ Προβλέψεις 10/20/30 λεπτών
✅ News sentiment analysis
✅ Accuracy statistics
✅ Dark Fintech theme
✅ Auto-refresh κάθε 5 λεπτά
✅ Responsive design

## Troubleshooting

### CORS Errors
Αν βλέπεις CORS errors, βεβαιώσου ότι:
1. Το backend τρέχει στο port 8000
2. Χρησιμοποιείς Live Server ή Python server (όχι file://)

### "API not responding"
1. Έλεγξε: http://localhost:8000/api/v1/health
2. Βεβαιώσου ότι το backend τρέχει
