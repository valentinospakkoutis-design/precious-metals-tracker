"""
WebSocket endpoints for real-time updates
"""
from fastapi import WebSocket, WebSocketDisconnect, APIRouter
from typing import List
import asyncio
import json
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from collectors.yfinance_collector import YFinanceCollector

router = APIRouter()

class ConnectionManager:
    """Manages WebSocket connections"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.collector = YFinanceCollector()
    
    async def connect(self, websocket: WebSocket):
        """Accept and store new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"✅ WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        self.active_connections.remove(websocket)
        print(f"❌ WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def broadcast(self, message: dict):
        """Send message to all connected clients"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"Error broadcasting to client: {e}")
                disconnected.append(connection)
        
        # Remove disconnected clients
        for conn in disconnected:
            self.active_connections.remove(conn)
    
    async def send_personal(self, message: dict, websocket: WebSocket):
        """Send message to specific client"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            print(f"Error sending to client: {e}")
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)

# Global connection manager
manager = ConnectionManager()

@router.websocket("/ws/prices")
async def websocket_prices(websocket: WebSocket):
    """
    WebSocket endpoint for real-time price updates
    
    Sends price updates every 5 seconds for all assets
    """
    await manager.connect(websocket)
    
    try:
        # Send initial welcome message
        await manager.send_personal({
            "type": "connection",
            "status": "connected",
            "message": "Real-time price feed connected",
            "timestamp": datetime.now().isoformat()
        }, websocket)
        
        while True:
            try:
                # Wait for client messages (ping/pong or subscribe requests)
                data = await asyncio.wait_for(websocket.receive_text(), timeout=5.0)
                request = json.loads(data)
                
                # Handle different message types
                if request.get("type") == "ping":
                    await manager.send_personal({
                        "type": "pong",
                        "timestamp": datetime.now().isoformat()
                    }, websocket)
                elif request.get("type") == "subscribe":
                    assets = request.get("assets", [])
                    await manager.send_personal({
                        "type": "subscribed",
                        "assets": assets,
                        "message": f"Subscribed to {len(assets)} assets"
                    }, websocket)
                    
            except asyncio.TimeoutError:
                # No message received, that's ok - we'll send updates anyway
                pass
            except json.JSONDecodeError:
                await manager.send_personal({
                    "type": "error",
                    "message": "Invalid JSON format"
                }, websocket)
            
            # This will be handled by the background task in main.py
            # Just keep the connection alive here
            await asyncio.sleep(1)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("Client disconnected normally")
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)


@router.websocket("/ws/alerts")
async def websocket_alerts(websocket: WebSocket):
    """
    WebSocket endpoint for real-time alert notifications
    
    Sends alerts when price thresholds are crossed
    """
    await manager.connect(websocket)
    
    try:
        await manager.send_personal({
            "type": "connection",
            "status": "connected",
            "message": "Alert notifications connected",
            "timestamp": datetime.now().isoformat()
        }, websocket)
        
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            request = json.loads(data)
            
            if request.get("type") == "ping":
                await manager.send_personal({
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                }, websocket)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)


async def broadcast_price_updates():
    """
    Background task to broadcast price updates to all connected clients
    
    Runs every 5 seconds
    """
    assets = ['BTC-USD', 'ETH-USD', 'AAPL', 'GOOGL', 'TSLA', 'GC=F', 'SI=F']
    
    while True:
        try:
            if len(manager.active_connections) > 0:
                prices = []
                
                for asset in assets:
                    try:
                        price_data = manager.collector.get_current_price(asset)
                        if price_data:
                            prices.append({
                                "asset": asset,
                                "price": price_data.get("price"),
                                "change_pct": price_data.get("change_pct"),
                                "timestamp": price_data.get("time"),
                                "source": price_data.get("source", "yfinance")
                            })
                    except Exception as e:
                        print(f"Error fetching {asset}: {e}")
                
                if prices:
                    await manager.broadcast({
                        "type": "price_update",
                        "data": prices,
                        "timestamp": datetime.now().isoformat()
                    })
                    print(f"📡 Broadcasted {len(prices)} prices to {len(manager.active_connections)} clients")
            
            await asyncio.sleep(5)  # Update every 5 seconds
            
        except Exception as e:
            print(f"Error in broadcast task: {e}")
            await asyncio.sleep(5)
