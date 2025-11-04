"""
WebSocket Router for Real-time Price Updates
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Set
import asyncio
import json
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from collectors.yfinance_collector import YFinanceCollector

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.collector = YFinanceCollector()
        
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        print(f"✅ WebSocket client connected. Total: {len(self.active_connections)}")
        
    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
        print(f"❌ WebSocket client disconnected. Total: {len(self.active_connections)}")
        
    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"Error sending to client: {e}")
                disconnected.add(connection)
        
        # Remove disconnected clients
        for conn in disconnected:
            self.active_connections.discard(conn)
    
    async def send_personal(self, websocket: WebSocket, message: dict):
        """Send message to specific client"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            print(f"Error sending personal message: {e}")
            self.disconnect(websocket)

manager = ConnectionManager()

@router.websocket("/ws/prices")
async def websocket_prices(websocket: WebSocket):
    """WebSocket endpoint for real-time price updates"""
    await manager.connect(websocket)
    
    try:
        while True:
            # Wait for client messages (if any)
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=0.1)
                # Handle client requests (e.g., subscribe to specific assets)
                print(f"Received from client: {data}")
            except asyncio.TimeoutError:
                pass
            
            await asyncio.sleep(0.1)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)

async def broadcast_prices():
    """Background task to broadcast prices every 5 seconds"""
    assets = ["BTC-USD", "ETH-USD", "AAPL", "GOOGL", "^GSPC"]
    
    while True:
        try:
            if manager.active_connections:
                prices_data = []
                
                for asset in assets:
                    try:
                        price_info = manager.collector.get_current_price(asset)
                        if price_info:
                            prices_data.append({
                                "asset": asset,
                                "price": price_info.get("price"),
                                "change": price_info.get("change_pct"),
                                "timestamp": datetime.now().isoformat()
                            })
                    except Exception as e:
                        print(f"Error fetching {asset}: {e}")
                
                if prices_data:
                    await manager.broadcast({
                        "type": "price_update",
                        "data": prices_data,
                        "timestamp": datetime.now().isoformat()
                    })
                    
        except Exception as e:
            print(f"Error in broadcast_prices: {e}")
        
        await asyncio.sleep(5)  # Broadcast every 5 seconds
