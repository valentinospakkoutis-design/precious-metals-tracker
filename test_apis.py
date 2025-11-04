"""
API Keys Test Script
Tests all configured API keys to ensure they work correctly
"""

import os
from dotenv import load_dotenv
import yfinance as yf
import requests
from datetime import datetime

# Load environment variables
load_dotenv()

print("=" * 60)
print("🔍 TESTING API KEYS - Financial Prediction App")
print("=" * 60)
print()

# Test results tracker
results = {
    "passed": [],
    "failed": [],
    "skipped": []
}

# ============================================
# 1. TEST NEWSAPI
# ============================================
print("1️⃣  Testing NewsAPI...")
newsapi_key = os.getenv("NEWSAPI_KEY")

if newsapi_key and newsapi_key != "your_newsapi_key_here":
    try:
        url = f"https://newsapi.org/v2/everything?q=bitcoin&pageSize=5&apiKey={newsapi_key}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            articles = data.get("articles", [])
            print(f"   ✅ SUCCESS - Retrieved {len(articles)} articles")
            print(f"   Sample: {articles[0]['title'][:60]}..." if articles else "")
            results["passed"].append("NewsAPI")
        else:
            print(f"   ❌ FAILED - Status: {response.status_code}")
            print(f"   Error: {response.json().get('message', 'Unknown error')}")
            results["failed"].append("NewsAPI")
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        results["failed"].append("NewsAPI")
else:
    print("   ⏭️  SKIPPED - No API key configured")
    results["skipped"].append("NewsAPI")

print()

# ============================================
# 2. TEST BINANCE
# ============================================
print("2️⃣  Testing Binance API...")
binance_key = os.getenv("BINANCE_API_KEY")
binance_secret = os.getenv("BINANCE_API_SECRET")

if binance_key and binance_key != "your_binance_api_key_here":
    try:
        # Test public endpoint (no auth needed)
        url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            btc_price = float(data["price"])
            print(f"   ✅ SUCCESS - BTC Price: ${btc_price:,.2f}")
            
            # Test authenticated endpoint
            from binance.client import Client
            client = Client(binance_key, binance_secret)
            account = client.get_account()
            print(f"   ✅ Authenticated - Account status: {account['accountType']}")
            results["passed"].append("Binance")
        else:
            print(f"   ❌ FAILED - Status: {response.status_code}")
            results["failed"].append("Binance")
    except ImportError:
        print("   ⚠️  Binance library not installed (will install in backend)")
        print(f"   ✅ Public API works - BTC available")
        results["passed"].append("Binance (public)")
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        results["failed"].append("Binance")
else:
    print("   ⏭️  SKIPPED - No API key configured")
    results["skipped"].append("Binance")

print()

# ============================================
# 3. TEST YFINANCE (Metals & Crypto)
# ============================================
print("3️⃣  Testing yfinance (Metals & Crypto)...")

try:
    # Test Gold
    gold = yf.Ticker("GC=F")
    gold_data = gold.history(period="1d")
    
    if not gold_data.empty:
        gold_price = gold_data['Close'].iloc[-1]
        print(f"   ✅ Gold (GC=F): ${gold_price:,.2f}")
    
    # Test Bitcoin
    btc = yf.Ticker("BTC-USD")
    btc_data = btc.history(period="1d")
    
    if not btc_data.empty:
        btc_price = btc_data['Close'].iloc[-1]
        print(f"   ✅ Bitcoin (BTC-USD): ${btc_price:,.2f}")
    
    # Test Ethereum
    eth = yf.Ticker("ETH-USD")
    eth_data = eth.history(period="1d")
    
    if not eth_data.empty:
        eth_price = eth_data['Close'].iloc[-1]
        print(f"   ✅ Ethereum (ETH-USD): ${eth_price:,.2f}")
    
    results["passed"].append("yfinance")
    
except Exception as e:
    print(f"   ❌ ERROR: {str(e)}")
    results["failed"].append("yfinance")

print()

# ============================================
# 4. TEST NASDAQ API
# ============================================
print("4️⃣  Testing NASDAQ Profile API...")
nasdaq_key = os.getenv("NASDAQ_API_KEY")

if nasdaq_key and nasdaq_key != "your_nasdaq_profile_key_here":
    try:
        # Test NASDAQ Data Link API
        url = f"https://data.nasdaq.com/api/v3/datasets/WIKI/AAPL.json?api_key={nasdaq_key}&limit=1"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ SUCCESS - NASDAQ API working")
            print(f"   Dataset: {data['dataset']['name']}")
            results["passed"].append("NASDAQ")
        elif response.status_code == 404:
            # Try alternative endpoint
            print(f"   ⚠️  Testing alternative NASDAQ endpoint...")
            url = f"https://data.nasdaq.com/api/v3/databases.json?api_key={nasdaq_key}"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"   ✅ SUCCESS - NASDAQ API key is valid")
                results["passed"].append("NASDAQ")
            else:
                print(f"   ❌ FAILED - Status: {response.status_code}")
                results["failed"].append("NASDAQ")
        else:
            print(f"   ❌ FAILED - Status: {response.status_code}")
            results["failed"].append("NASDAQ")
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        results["failed"].append("NASDAQ")
else:
    print("   ⏭️  SKIPPED - No API key configured")
    results["skipped"].append("NASDAQ")

print()

# ============================================
# SUMMARY
# ============================================
print("=" * 60)
print("📊 TEST SUMMARY")
print("=" * 60)
print()

print(f"✅ Passed: {len(results['passed'])}")
for service in results['passed']:
    print(f"   • {service}")
print()

if results['failed']:
    print(f"❌ Failed: {len(results['failed'])}")
    for service in results['failed']:
        print(f"   • {service}")
    print()

if results['skipped']:
    print(f"⏭️  Skipped: {len(results['skipped'])}")
    for service in results['skipped']:
        print(f"   • {service}")
    print()

total_tested = len(results['passed']) + len(results['failed'])
success_rate = (len(results['passed']) / total_tested * 100) if total_tested > 0 else 0

print("=" * 60)
print(f"🎯 Success Rate: {success_rate:.0f}% ({len(results['passed'])}/{total_tested})")
print("=" * 60)
print()

if len(results['passed']) >= 3:
    print("🎉 Great! You have enough APIs to start development!")
    print("💡 Next: Run Docker setup and create the backend")
else:
    print("⚠️  Consider adding more API keys for better data coverage")

print()
print(f"Tested at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
