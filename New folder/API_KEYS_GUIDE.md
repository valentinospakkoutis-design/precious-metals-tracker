# 🔑 ΟΔΗΓΟΣ API KEYS - Financial Prediction App

Ημερομηνία: 26 Οκτωβρίου 2025

---

## 📋 ΠΕΡΙΛΗΨΗ

Για να λειτουργήσει το app μας, χρειαζόμαστε API keys από τις παρακάτω υπηρεσίες:

1. **Binance** - Crypto τιμές (BTC, ETH, BNB, ADA, DOGE, SHIB, PEPE)
2. **MetalpriceAPI** - Metals τιμές (Gold, Silver, Platinum)
3. **NewsAPI** - Ειδήσεις & sentiment analysis

**Κόστος:** Όλα ΔΩΡΕΑΝ ✅ (για development)

---

## 1️⃣ BINANCE API

### Γιατί το χρειαζόμαστε:
- Real-time crypto prices κάθε 10 λεπτά
- Volume data
- Orderbook information
- Historical data

### 📊 Free Tier:
- ✅ Unlimited read requests
- ✅ Real-time data
- ❌ No trading needed (Read-Only)

### 🔗 Links:
- **Official Guide:** https://www.binance.com/en/support/faq/how-to-create-api-keys-on-binance-360002502072
- **Testnet (για δοκιμές):** https://testnet.binance.vision/
- **API Documentation:** https://binance-docs.github.io/apidocs/spot/en/

### 📝 Βήματα:

#### A. Δημιουργία Λογαριασμού
1. Πήγαινε στο: https://www.binance.com/
2. Click "Register" (πάνω δεξιά)
3. Συμπλήρωσε:
   - Email
   - Password (strong!)
   - Accept Terms
4. Verify email (check inbox)
5. **ΣΗΜΑΝΤΙΚΟ:** Enable 2FA (Google Authenticator ή SMS)

#### B. Δημιουργία API Key
1. Login στο Binance
2. Click στο profile icon (πάνω δεξιά)
3. Επίλεξε **"Account"**
4. Από το μενού, επίλεξε **"API Management"**
5. Click **"Create API"**
6. Διάλεξε **"System generated"** (HMAC)
7. Δώσε ένα όνομα: π.χ. "Financial Prediction App"
8. Complete 2FA verification
9. **Θα δεις το API Key και το Secret Key - ΑΠΟΘΗΚΕΥΣΕ ΤΑ ΑΜΕΣΩΣ!**
   - API Key: 64 χαρακτήρες
   - Secret Key: **ΜΟΝΟ 1 ΦΟΡΑ ΦΑΙΝΕΤΑΙ - αν το χάσεις πρέπει να φτιάξεις νέο!**

#### C. Ρυθμίσεις Ασφαλείας
1. Στην API Management page:
2. **Permissions:** Επίλεξε ΜΟΝΟ "Enable Reading" ✅
   - ❌ ΜΗΝ ενεργοποιήσεις: Spot Trading, Futures, Withdrawals
3. **IP Restrictions:** 
   - Για local development: "Unrestricted" (προσωρινά)
   - Για production: Add το specific IP του server
4. Click **"Save"**

#### D. Testing
Δοκίμασε με curl:
```bash
curl -X GET 'https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT'
```

Θα πρέπει να δεις κάτι σαν:
```json
{
  "symbol": "BTCUSDT",
  "price": "68150.00"
}
```

### ⚠️ Προσοχή:
- **ΠΟΤΕ μην κοινοποιήσεις το Secret Key**
- Αποθήκευσε τα keys σε `.env` file (όχι στο Git!)
- Για production, πρόσθεσε IP restrictions
- Έλεγχε τακτικά την API usage στο dashboard

---

## 2️⃣ COINGECKO API (Εναλλακτικό/Backup)

### Γιατί το χρειαζόμαστε:
- Backup για Binance
- Περισσότερα shitcoins
- Market cap data
- Social metrics

### 📊 Free Tier (Demo Plan):
- ✅ 10-30 calls/minute
- ✅ Real-time data
- ✅ No credit card required

### 🔗 Links:
- **Pricing Page:** https://www.coingecko.com/en/api/pricing
- **Dashboard:** https://www.coingecko.com/en/developers/dashboard
- **Documentation:** https://docs.coingecko.com/

### 📝 Βήματα:

1. Πήγαινε στο: https://www.coingecko.com/en/api/pricing
2. Click **"Create Free Account"** (Demo Plan)
3. Register ή Login με:
   - Email
   - Password
   ή μέσω Google/GitHub
4. Verify email
5. Go to **Developer's Dashboard**
6. Click **"+ Add New Key"**
7. Δώσε label: π.χ. "Financial Pred App"
8. Copy το **API Key**

### Testing:
```bash
curl 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&x_cg_demo_api_key=YOUR_API_KEY'
```

Response:
```json
{
  "bitcoin": {
    "usd": 68150
  }
}
```

---

## 3️⃣ METALPRICEAPI

### Γιατί το χρειαζόμαστε:
- Real-time Gold, Silver, Platinum prices
- Historical data
- Multiple currencies support

### 📊 Free Tier:
- ✅ 100 requests/month
- ✅ Real-time data
- ✅ No credit card required

### 🔗 Links:
- **Homepage:** https://metalpriceapi.com/
- **Documentation:** https://metalpriceapi.com/documentation
- **Dashboard:** https://metalpriceapi.com/dashboard

### 📝 Βήματα:

1. Πήγαινε στο: https://metalpriceapi.com/
2. Click **"Get Free API Key"**
3. Register με:
   - Name
   - Email
   - Password
4. Verify email
5. Login και go to **Dashboard**
6. Copy το **API Key**

### Testing:
```bash
curl 'https://api.metalpriceapi.com/v1/latest?api_key=YOUR_API_KEY&base=USD&currencies=XAU,XAG,XPT'
```

Response:
```json
{
  "success": true,
  "timestamp": 1698345600,
  "base": "USD",
  "rates": {
    "XAU": 0.00043,  // Gold (1 USD = X oz)
    "XAG": 0.0385,   // Silver
    "XPT": 0.00104   // Platinum
  }
}
```

### 🔄 Εναλλακτικά:

#### Metals-API
- URL: https://metals-api.com/
- Free: 50 requests/month
- Similar features

#### Metals.Dev
- URL: https://metals.dev/
- Free: 100 requests/month
- LBMA pricing

---

## 4️⃣ NEWSAPI

### Γιατί το χρειαζόμαστε:
- Οικονομικά άρθρα
- Sentiment analysis
- Real-time news για crypto/metals
- Impact στις τιμές

### 📊 Free Tier (Developer):
- ✅ 500 requests/day
- ✅ 30k+ news sources
- ✅ Real-time updates
- ❌ Development only (not for production)

### 🔗 Links:
- **Register:** https://newsapi.org/register
- **Documentation:** https://newsapi.org/docs
- **Dashboard:** https://newsapi.org/account

### 📝 Βήματα:

1. Πήγαινε στο: https://newsapi.org/register
2. Συμπλήρωσε:
   - **First Name:** Το όνομα σου
   - **Email:** Το email σου
   - **You are...:** Επίλεξε "I am an individual"
3. Tick boxes:
   - ✅ I agree to the terms
   - ✅ I promise to add attribution link (για το app)
4. Click **"Submit"**
5. Θα σε redirect στο dashboard
6. **Copy το API Key** (φαίνεται αμέσως)

### Testing:
```bash
curl 'https://newsapi.org/v2/everything?q=bitcoin&apiKey=YOUR_API_KEY'
```

Response:
```json
{
  "status": "ok",
  "totalResults": 1234,
  "articles": [
    {
      "source": {"name": "CoinDesk"},
      "title": "Bitcoin Surges...",
      "description": "...",
      "publishedAt": "2025-10-26T10:00:00Z",
      ...
    }
  ]
}
```

### 🔍 Useful Queries για το app:
```bash
# Bitcoin news
q=bitcoin OR cryptocurrency OR BTC

# Gold news
q=gold OR precious metals OR XAU

# Sentiment keywords
q=(bitcoin OR crypto) AND (surge OR crash OR spike OR drop)
```

### 🔄 Εναλλακτικά:

#### NewsData.io
- URL: https://newsdata.io/
- Free: 200 requests/day
- 50k+ sources

#### GNews
- URL: https://gnews.io/
- Free: 100 requests/day
- 60k+ sources

---

## 📦 ΑΠΟΘΗΚΕΥΣΗ API KEYS

### .env File Structure

Δημιούργησε ένα `.env` file στο root του project:

```bash
# Binance
BINANCE_API_KEY=your_binance_api_key_here
BINANCE_SECRET_KEY=your_binance_secret_key_here

# CoinGecko (backup)
COINGECKO_API_KEY=your_coingecko_key_here

# Metals
METALPRICE_API_KEY=your_metalpriceapi_key_here

# News
NEWS_API_KEY=your_newsapi_key_here

# Alternative News (optional)
NEWSDATA_API_KEY=your_newsdata_key_here
```

### 🛡️ Security Best Practices:

#### .gitignore
**ΠΑΝΤΑ** πρόσθεσε στο `.gitignore`:
```
.env
.env.local
.env.production
*.pem
secrets/
```

#### Docker Compose
Για local development:
```yaml
services:
  api:
    environment:
      - BINANCE_API_KEY=${BINANCE_API_KEY}
      - BINANCE_SECRET_KEY=${BINANCE_SECRET_KEY}
      - METALPRICE_API_KEY=${METALPRICE_API_KEY}
      - NEWS_API_KEY=${NEWS_API_KEY}
    env_file:
      - .env
```

#### Python (FastAPI)
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    binance_api_key: str
    binance_secret_key: str
    metalprice_api_key: str
    news_api_key: str
    
    class Config:
        env_file = ".env"
```

---

## 🔍 TESTING CHECKLIST

Πριν αρχίσεις development, δοκίμασε όλα τα APIs:

### ✅ Binance
```bash
curl -X GET 'https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT'
```
Expected: Price data

### ✅ CoinGecko
```bash
curl 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd'
```
Expected: Bitcoin price

### ✅ MetalpriceAPI
```bash
curl 'https://api.metalpriceapi.com/v1/latest?api_key=YOUR_KEY&base=USD&currencies=XAU'
```
Expected: Gold price

### ✅ NewsAPI
```bash
curl 'https://newsapi.org/v2/everything?q=bitcoin&apiKey=YOUR_KEY'
```
Expected: News articles

---

## 📊 API RATE LIMITS SUMMARY

| API | Free Limit | Reset Period | Notes |
|-----|------------|--------------|-------|
| **Binance** | Unlimited reads | - | Weight-based system |
| **CoinGecko** | 10-30/min | Per minute | Demo plan |
| **MetalpriceAPI** | 100/month | Monthly | Consider paid if needed |
| **NewsAPI** | 500/day | Daily | Dev only |

### 💡 Tips για να μην ξεπεράσεις τα limits:

1. **Caching:** Αποθήκευσε responses για 10 λεπτά (Redis)
2. **Batch Requests:** Ζήτα πολλά assets μαζί
3. **Conditional Requests:** Χρησιμοποίησε ETags
4. **Rate Limiting:** Implement exponential backoff
5. **Monitoring:** Track usage στο dashboard κάθε API

---

## 🆘 TROUBLESHOOTING

### Binance Error: "Invalid API Key"
**Λύση:**
- Έλεγξε αν το key είναι σωστά copy-pasted
- Βεβαιώσου ότι το API key δεν έχει διαγραφεί
- Τσέκαρε αν IP restrictions block το request

### CoinGecko Error: "Rate limit exceeded"
**Λύση:**
- Περίμενε 1 λεπτό και retry
- Implement caching
- Upgrade σε paid plan αν χρειάζεται

### MetalpriceAPI Error: "Quota exceeded"
**Λύση:**
- Έχεις ξεπεράσει τα 100 requests/month
- Περίμενε μέχρι την 1η του μήνα
- Εναλλακτικά, χρησιμοποίησε Metals-API ή Metals.Dev

### NewsAPI Error: "Invalid API key"
**Λύση:**
- Τσέκαρε αν το key είναι valid
- Βεβαιώσου ότι το account είναι verified
- Για production, χρειάζεσαι paid plan

---

## 📞 SUPPORT LINKS

Αν έχεις πρόβλημα:

- **Binance Support:** https://www.binance.com/en/support
- **CoinGecko Support:** https://support.coingecko.com/
- **MetalpriceAPI Support:** support@metalpriceapi.com
- **NewsAPI Support:** https://newsapi.org/contact

---

## 🎯 ΕΠΟΜΕΝΟ ΒΗΜΑ

Μόλις έχεις όλα τα API keys:

1. ✅ Αποθήκευσε τα σε `.env` file
2. ✅ Πρόσθεσε `.env` στο `.gitignore`
3. ✅ Δοκίμασε κάθε API με curl
4. ✅ Ενημέρωσε τον developer ότι είσαι έτοιμος!

---

**Status:** 🟢 Ready to Collect Keys  
**Estimated Time:** ~20 λεπτά για όλα  
**Cost:** €0.00 (Όλα free!) 💰✅

---

*Τελευταία ενημέρωση: 26 Οκτωβρίου 2025*
