"""
Simple In-Memory Database Mock
Used for development without Docker
"""

from datetime import datetime
from typing import Dict, List, Optional

class InMemoryDB:
    def __init__(self):
        self.price_data = []
        self.predictions = []
        self.news = []
        
    def save_price(self, asset_id: str, price: float, volume: float = 0):
        """Save price data"""
        self.price_data.append({
            'time': datetime.now(),
            'asset_id': asset_id,
            'price': price,
            'volume': volume,
            'source': 'yfinance'
        })
        
        # Keep only last 1000 records per asset
        if len(self.price_data) > 10000:
            self.price_data = self.price_data[-10000:]
    
    def get_latest_price(self, asset_id: str) -> Optional[Dict]:
        """Get latest price for asset"""
        for data in reversed(self.price_data):
            if data['asset_id'] == asset_id:
                return data
        return None
    
    def get_all_latest_prices(self) -> List[Dict]:
        """Get latest prices for all assets"""
        assets = {}
        for data in reversed(self.price_data):
            if data['asset_id'] not in assets:
                assets[data['asset_id']] = data
        return list(assets.values())

# Global instance
db = InMemoryDB()
