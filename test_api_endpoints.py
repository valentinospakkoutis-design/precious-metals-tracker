"""
Test FastAPI Endpoints
"""

import requests
import json
from time import sleep

BASE_URL = "http://localhost:8001"

print("🧪 Testing Financial Prediction API")
print("=" * 60)

# Wait for server to start
sleep(2)

# Test 1: Health check
print("\n1️⃣  Testing Health Endpoint...")
try:
    response = requests.get(f"{BASE_URL}/api/v1/health")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Status: {data['status']}")
        print(f"   Assets: {data['assets_count']}")
    else:
        print(f"❌ Failed: {response.status_code}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 2: Get all assets
print("\n2️⃣  Testing Assets Endpoint...")
try:
    response = requests.get(f"{BASE_URL}/api/v1/assets")
    if response.status_code == 200:
        assets = response.json()
        print(f"✅ Found {len(assets)} assets:")
        for asset in assets[:5]:  # Show first 5
            print(f"   • {asset['id']:8} - {asset['name']} ({asset['type']})")
    else:
        print(f"❌ Failed: {response.status_code}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 3: Get BTC price
print("\n3️⃣  Testing Price Endpoint (BTC)...")
try:
    response = requests.get(f"{BASE_URL}/api/v1/price/BTC")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ BTC Price: ${data['price']:,.2f}")
        if data['change_pct']:
            change_symbol = "📈" if data['change_pct'] > 0 else "📉"
            print(f"   Change: {change_symbol} {data['change_pct']:+.2f}%")
        print(f"   Volume: {data['volume']:,.0f}")
    else:
        print(f"❌ Failed: {response.status_code}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 4: Get all prices
print("\n4️⃣  Testing All Prices Endpoint...")
try:
    response = requests.get(f"{BASE_URL}/api/v1/prices")
    if response.status_code == 200:
        prices = response.json()
        print(f"✅ Retrieved {len(prices)} prices:")
        for price in prices[:5]:  # Show first 5
            change = f"{price['change_pct']:+.2f}%" if price.get('change_pct') else "N/A"
            print(f"   {price['asset_id']:8} ${price['price']:>12,.2f}  {change}")
    else:
        print(f"❌ Failed: {response.status_code}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 5: Get BTC prediction
print("\n5️⃣  Testing Prediction Endpoint (BTC)...")
try:
    response = requests.post(f"{BASE_URL}/api/v1/predict/BTC")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Current BTC: ${data['current_price']:,.2f}")
        print(f"\n   🔮 Predictions:")
        for pred in data['predictions']:
            arrow = "🔼" if pred['predicted_change_pct'] > 0 else "🔽"
            print(f"   {pred['horizon']:6} {arrow} {pred['predicted_change_pct']:+.2f}%  "
                  f"→ ${pred['predicted_price']:,.2f}  (Confidence: {pred['confidence']:.0f}%)")
            print(f"           Range: ${pred['min_price']:,.2f} - ${pred['max_price']:,.2f}")
    else:
        print(f"❌ Failed: {response.status_code}")
        print(f"   {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 6: Get GOLD prediction
print("\n6️⃣  Testing Prediction Endpoint (GOLD)...")
try:
    response = requests.post(f"{BASE_URL}/api/v1/predict/GOLD")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Current GOLD: ${data['current_price']:,.2f}")
        print(f"\n   🔮 Predictions:")
        for pred in data['predictions']:
            arrow = "🔼" if pred['predicted_change_pct'] > 0 else "🔽"
            print(f"   {pred['horizon']:6} {arrow} {pred['predicted_change_pct']:+.2f}%  "
                  f"→ ${pred['predicted_price']:,.2f}  (Confidence: {pred['confidence']:.0f}%)")
    else:
        print(f"❌ Failed: {response.status_code}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 60)
print("🎉 API Testing Complete!")
print("📖 Full docs: http://localhost:8000/docs")
