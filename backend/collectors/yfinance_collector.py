"""
Data Collector for yfinance (Metals & Crypto)
Collects price data for all 10 assets every 10 minutes
Uses metals.live API for real-time metal prices
"""

import yfinance as yf
import requests
from datetime import datetime
import time
import os
from dotenv import load_dotenv

load_dotenv()

# Metals Live API (Free, no key needed!)
METALS_LIVE_API = "https://api.metals.live/v1/spot"

# Asset mappings
ASSETS = {
    # Metals
    'GOLD': 'GC=F',
    'SILVER': 'SI=F',
    'PLATINUM': 'PL=F',
    
    # Crypto
    'BTC': 'BTC-USD',
    'ETH': 'ETH-USD',
    'BNB': 'BNB-USD',
    'ADA': 'ADA-USD',
    
    # Shitcoins
    'DOGE': 'DOGE-USD',
    'SHIB': 'SHIB-USD',
    'PEPE': 'PEPE-USD'
}

class YFinanceCollector:
    def __init__(self):
        self.assets = ASSETS
    
    def get_metal_price_live(self, asset_id):
        """Get real-time metal price from metals.live API"""
        try:
            response = requests.get(METALS_LIVE_API, timeout=5)
            if response.status_code == 200:
                data = response.json()
                
                # Map our asset IDs to metals.live keys
                metal_mapping = {
                    'GOLD': 'gold',
                    'SILVER': 'silver',
                    'PLATINUM': 'platinum'
                }
                
                if asset_id in metal_mapping:
                    metal_key = metal_mapping[asset_id]
                    if metal_key in data:
                        price = data[metal_key]
                        return {
                            'asset_id': asset_id,
                            'time': datetime.now(),
                            'price': float(price),
                            'volume': 0,  # metals.live doesn't provide volume
                            'source': 'metals.live'
                        }
            return None
        except Exception as e:
            print(f"⚠️  metals.live API error for {asset_id}: {str(e)}")
            return None
        
    def collect_price(self, asset_id, symbol):
        """Collect current price for a single asset"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1d", interval="1m")
            
            if data.empty:
                print(f"⚠️  No data for {asset_id} ({symbol})")
                return None
            
            latest = data.iloc[-1]
            
            price_data = {
                'asset_id': asset_id,
                'time': datetime.now(),
                'price': float(latest['Close']),
                'volume': float(latest['Volume']) if latest['Volume'] else 0,
                'source': 'yfinance'
            }
            
            return price_data
            
        except Exception as e:
            print(f"❌ Error collecting {asset_id}: {str(e)}")
            return None
    
    def get_current_price(self, asset_id):
        """Get current price with 24h change for a single asset"""
        try:
            if asset_id not in self.assets:
                return None
            
            # Try metals.live API first for metals (faster & real-time)
            if asset_id in ['GOLD', 'SILVER', 'PLATINUM']:
                metal_data = self.get_metal_price_live(asset_id)
                if metal_data:
                    # Still need yfinance for 24h change calculation
                    symbol = self.assets[asset_id]
                    ticker = yf.Ticker(symbol)
                    data = ticker.history(period="2d", interval="1h")
                    
                    if not data.empty and len(data) >= 2:
                        if len(data) >= 24:
                            price_24h_ago = float(data['Close'].iloc[-24])
                        else:
                            price_24h_ago = float(data['Close'].iloc[0])
                        
                        change_24h = ((metal_data['price'] - price_24h_ago) / price_24h_ago) * 100
                        
                        return {
                            'asset_id': asset_id,
                            'price': metal_data['price'],
                            'change_24h': change_24h,
                            'timestamp': datetime.now(),
                            'source': 'metals.live'
                        }
                
            # Fallback to yfinance for crypto or if metals.live fails
            symbol = self.assets[asset_id]
            ticker = yf.Ticker(symbol)
            
            # Get 2 days of data to calculate 24h change
            data = ticker.history(period="2d", interval="1h")
            
            if data.empty or len(data) < 2:
                return None
            
            current_price = float(data['Close'].iloc[-1])
            
            # Calculate 24h change
            if len(data) >= 24:
                price_24h_ago = float(data['Close'].iloc[-24])
            else:
                price_24h_ago = float(data['Close'].iloc[0])
            
            change_24h = ((current_price - price_24h_ago) / price_24h_ago) * 100
            
            return {
                'asset_id': asset_id,
                'price': current_price,
                'change_24h': change_24h,
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            print(f"Error getting price for {asset_id}: {str(e)}")
            return None
    
    def collect_all(self):
        """Collect prices for all assets"""
        print(f"\n🔄 Collecting data at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        results = []
        
        for asset_id, symbol in self.assets.items():
            data = self.collect_price(asset_id, symbol)
            
            if data:
                print(f"✅ {asset_id:8} | ${data['price']:>12,.2f} | Vol: {data['volume']:>15,.0f}")
                results.append(data)
            else:
                print(f"❌ {asset_id:8} | Failed to collect")
        
        print("=" * 60)
        print(f"✅ Collected: {len(results)}/{len(self.assets)} assets")
        
        return results

def main():
    """Run collector in a loop (every 10 minutes)"""
    collector = YFinanceCollector()
    
    print("🚀 Starting yfinance Data Collector")
    print("📊 Collecting 10 assets every 10 minutes")
    print("=" * 60)
    
    # Collect immediately
    collector.collect_all()
    
    # Then every 10 minutes
    interval = 600  # 10 minutes in seconds
    
    while True:
        try:
            print(f"\n⏳ Next collection in {interval//60} minutes...")
            time.sleep(interval)
            collector.collect_all()
            
        except KeyboardInterrupt:
            print("\n\n🛑 Collector stopped by user")
            break
        except Exception as e:
            print(f"\n❌ Error in main loop: {str(e)}")
            print("⏳ Retrying in 1 minute...")
            time.sleep(60)

if __name__ == "__main__":
    main()
