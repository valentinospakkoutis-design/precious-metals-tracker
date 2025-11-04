"""
Test metals.live API integration
"""

import requests
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.collectors.yfinance_collector import YFinanceCollector

print("=" * 70)
print("🥇 TESTING METALS.LIVE API")
print("=" * 70)
print()

# Test raw API
print("1️⃣ Testing raw metals.live API:")
print("-" * 70)

try:
    response = requests.get("https://api.metals.live/v1/spot", timeout=5)
    if response.status_code == 200:
        data = response.json()
        print("✅ API Response:")
        for metal, price in data.items():
            print(f"   {metal.upper()}: ${price:,.2f}")
    else:
        print(f"❌ Error: {response.status_code}")
except Exception as e:
    print(f"❌ Error: {e}")

print()
print("2️⃣ Testing integrated collector:")
print("-" * 70)

collector = YFinanceCollector()

for asset_id in ['GOLD', 'SILVER', 'PLATINUM']:
    print(f"\n{asset_id}:")
    
    price_data = collector.get_current_price(asset_id)
    
    if price_data:
        print(f"   💵 Price: ${price_data['price']:,.2f}")
        print(f"   📊 24h Change: {price_data['change_24h']:+.2f}%")
        print(f"   🔌 Source: {price_data.get('source', 'unknown')}")
        print(f"   ⏰ Time: {price_data['timestamp'].strftime('%H:%M:%S')}")
    else:
        print("   ❌ Failed to fetch price")

print()
print("=" * 70)
print("✅ Test Complete!")
print()
print("💡 Benefits of metals.live:")
print("   • Free API (no key needed)")
print("   • Real-time spot prices")
print("   • Faster than yfinance for metals")
print("   • Fallback to yfinance if fails")
print("=" * 70)
