# 📮 Postman Collection Guide

Complete Postman collection for the Financial Prediction API with authentication, 2FA, and CSRF protection.

## 📥 Import Files

Import both files into Postman:

1. **Collection**: `Financial_API.postman_collection.json`
2. **Environment**: `Financial_API_Local.postman_environment.json`

## 🚀 Quick Start

### 1. Setup Environment

1. Open Postman
2. Click "Import" → Select both JSON files
3. Select "Financial API - Local" environment (top-right dropdown)

### 2. Test Authentication Flow

**Step 1: Register User**
```
POST /api/v1/auth/register
```
- Automatically saves `access_token` and `refresh_token`

**Step 2: Get CSRF Token** (for portfolio operations)
```
GET /api/v1/csrf-token
```
- Automatically saves `csrf_token`

**Step 3: Make Authenticated Requests**
- All endpoints use Bearer token automatically
- Portfolio endpoints include CSRF token

## 🔐 2FA Testing Workflow

### Enable 2FA

1. **Login** → Get access token
2. **Enable 2FA** → Receive QR code + secret + backup codes
3. Scan QR code with Google Authenticator app
4. **Verify 2FA** → Enter 6-digit code from app
5. **Login with 2FA** → Use email + password + TOTP code

### Test 2FA Endpoints

```
1. POST /api/v1/auth/2fa/enable
   → Save secret and backup codes

2. POST /api/v1/auth/2fa/verify
   → Confirm setup with TOTP token

3. POST /api/v1/auth/login/2fa
   → Login with 2FA (email + password + TOTP)

4. POST /api/v1/auth/2fa/disable
   → Disable 2FA (requires TOTP)

5. POST /api/v1/auth/2fa/backup-code
   → Emergency login with backup code
```

## 🛡️ CSRF Protection

Portfolio endpoints require CSRF token:

1. **Get CSRF Token**:
   ```
   GET /api/v1/csrf-token
   ```

2. **Use in Headers**:
   ```
   X-CSRF-Token: {{csrf_token}}
   ```

3. **Protected Endpoints**:
   - `POST /api/v1/portfolio/buy`
   - `POST /api/v1/portfolio/sell`

## 📊 Collection Structure

### 1. Authentication
- Register User
- Login
- Refresh Token
- Get Current User
- Logout

### 2. Two-Factor Authentication (2FA)
- Enable 2FA
- Verify 2FA Setup
- Login with 2FA
- Disable 2FA
- Login with Backup Code

### 3. Security
- Get CSRF Token

### 4. Portfolio (CSRF Protected)
- Buy Asset
- Sell Asset

### 5. Predictions
- Predict Stock
- Predict Crypto

### 6. Prices
- Get Stock Price
- Get Crypto Price
- Get Gold Price

### 7. News
- Get Latest News

### 8. Health Check
- Health

## 🔄 Automatic Token Management

The collection includes **test scripts** that automatically:

1. ✅ Save `access_token` after login/register
2. ✅ Save `refresh_token` for token renewal
3. ✅ Save `csrf_token` for protected operations
4. ✅ Save `two_factor_secret` during 2FA setup
5. ✅ Include Bearer token in all authenticated requests

## 📝 Environment Variables

| Variable | Description | Auto-set |
|----------|-------------|----------|
| `base_url` | API base URL | ❌ Manual |
| `test_email` | Test user email | ❌ Manual |
| `test_password` | Test user password | ❌ Manual |
| `access_token` | JWT access token | ✅ Auto |
| `refresh_token` | JWT refresh token | ✅ Auto |
| `csrf_token` | CSRF protection token | ✅ Auto |
| `two_factor_secret` | 2FA secret key | ✅ Auto |

## 🧪 Testing Scenarios

### Scenario 1: Basic Authentication
```
1. Register User
2. Login
3. Get Current User
4. Logout
```

### Scenario 2: CSRF Protection
```
1. Login
2. Get CSRF Token
3. Buy Asset (with CSRF token)
4. Sell Asset (with CSRF token)
```

### Scenario 3: 2FA Flow
```
1. Register User
2. Login
3. Enable 2FA → Save secret
4. Verify 2FA → Enter TOTP
5. Logout
6. Login with 2FA → Enter TOTP
```

### Scenario 4: Token Refresh
```
1. Login → Get tokens
2. Wait 15 minutes (token expires)
3. Refresh Token → Get new access token
4. Make authenticated request
```

### Scenario 5: Account Lockout (Security Test)
```
1. Try to login with wrong password (5 times)
2. Account locked for 1 hour
3. Try to login again → HTTP 423 (Locked)
```

## ⚠️ Rate Limits

| Endpoint | Limit |
|----------|-------|
| Authentication | 5 requests/minute |
| Predictions | 10 requests/minute |
| Portfolio | 30 requests/minute |
| Prices | 60 requests/minute |

## 🔧 Troubleshooting

### CSRF Token Error (403)
```
✅ Solution: Get new CSRF token before portfolio operations
GET /api/v1/csrf-token
```

### Unauthorized (401)
```
✅ Solution: Login to get new access token
POST /api/v1/auth/login
```

### Token Expired (401)
```
✅ Solution: Refresh your token
POST /api/v1/auth/refresh?refresh_token={{refresh_token}}
```

### Account Locked (423)
```
✅ Solution: Wait 1 hour or contact admin
(5 failed login attempts = 1 hour lockout)
```

### Rate Limit Exceeded (429)
```
✅ Solution: Wait 1 minute before retrying
```

## 📱 2FA Setup (Google Authenticator)

1. **Enable 2FA** in Postman → Receive QR code
2. Open Google Authenticator app
3. Click "+" → "Scan QR code"
4. Scan the base64 QR code image from response
5. App shows 6-digit code (changes every 30 seconds)
6. Use code to **Verify 2FA** in Postman

## 🎯 Production Environment

Create a new environment for production:

```json
{
  "base_url": "https://api.yourproduction.com",
  "test_email": "your.email@example.com",
  "test_password": "YourSecurePassword123!"
}
```

## 📚 Additional Resources

- **API Documentation**: http://127.0.0.1:8000/docs (Swagger UI)
- **Alternative Docs**: http://127.0.0.1:8000/redoc (ReDoc)
- **Security Audit**: See `SECURITY_AUDIT.md`
- **Deployment Guide**: See `DEPLOYMENT.md`

## 💡 Tips

1. **Run Collection**: Use "Runner" to test all endpoints automatically
2. **Environment Switcher**: Easily switch between local/staging/production
3. **Pre-request Scripts**: Automatic token refresh before each request
4. **Test Scripts**: Verify responses and extract data automatically
5. **Mock Server**: Create mock server from collection for frontend development

---

**Happy Testing! 🚀**
