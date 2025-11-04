"""
Portfolio Tracking Router - Fixed
Handles buy/sell trades and P&L calculations with proper async database
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.async_db import async_db

router = APIRouter(prefix="/api/v1/portfolio", tags=["Portfolio"])

# Pydantic models
class TradeRequest(BaseModel):
    asset_id: str
    quantity: float
    price: float
    user_id: Optional[str] = "default"

class PortfolioPosition(BaseModel):
    asset_id: str
    name: str
    asset_type: str
    quantity: float
    average_price: float
    current_price: float
    total_value: float
    total_cost: float
    pnl: float
    pnl_percent: float

class PortfolioSummary(BaseModel):
    total_value: float
    total_cost: float
    total_pnl: float
    total_pnl_percent: float
    position_count: int
    positions: List[PortfolioPosition]


@router.post("/buy")
async def buy_asset(trade: TradeRequest):
    """Buy an asset"""
    try:
        # Validate asset exists
        asset = await async_db.get_asset(trade.asset_id)
        if not asset:
            raise HTTPException(status_code=404, detail=f"Asset {trade.asset_id} not found")
        
        # Get current position
        position = await async_db.get_position(trade.asset_id, trade.user_id)
        
        if position:
            # Update existing position (calculate new average price)
            old_qty = float(position['quantity'])
            old_avg = float(position['average_price'])
            new_qty = old_qty + trade.quantity
            new_avg = ((old_avg * old_qty) + (trade.price * trade.quantity)) / new_qty
            
            await async_db.upsert_position(trade.asset_id, new_qty, new_avg, trade.user_id)
        else:
            # Create new position
            await async_db.upsert_position(trade.asset_id, trade.quantity, trade.price, trade.user_id)
        
        return {
            "success": True,
            "message": f"Bought {trade.quantity} {trade.asset_id} at ${trade.price}",
            "trade": {
                "type": "BUY",
                "asset_id": trade.asset_id,
                "quantity": trade.quantity,
                "price": trade.price,
                "timestamp": datetime.now().isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Trade failed: {str(e)}")


@router.post("/sell")
async def sell_asset(trade: TradeRequest):
    """Sell an asset"""
    try:
        # Get current position
        position = await async_db.get_position(trade.asset_id, trade.user_id)
        
        if not position:
            raise HTTPException(status_code=400, detail=f"No position in {trade.asset_id}")
        
        current_qty = float(position['quantity'])
        
        if trade.quantity > current_qty:
            raise HTTPException(
                status_code=400, 
                detail=f"Insufficient quantity. Have {current_qty}, trying to sell {trade.quantity}"
            )
        
        new_qty = current_qty - trade.quantity
        avg_price = float(position['average_price'])
        
        if new_qty == 0:
            # Close position completely
            await async_db.delete_position(trade.asset_id, trade.user_id)
        else:
            # Update position
            await async_db.upsert_position(trade.asset_id, new_qty, avg_price, trade.user_id)
        
        # Calculate P&L
        pnl = (trade.price - avg_price) * trade.quantity
        pnl_pct = ((trade.price - avg_price) / avg_price) * 100
        
        return {
            "success": True,
            "message": f"Sold {trade.quantity} {trade.asset_id} at ${trade.price}",
            "trade": {
                "type": "SELL",
                "asset_id": trade.asset_id,
                "quantity": trade.quantity,
                "price": trade.price,
                "pnl": round(pnl, 2),
                "pnl_percent": round(pnl_pct, 2),
                "timestamp": datetime.now().isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Trade failed: {str(e)}")


@router.get("/positions")
async def get_positions(user_id: str = "default"):
    """Get all portfolio positions with current P&L"""
    try:
        positions = await async_db.get_portfolio_positions(user_id)
        
        result = []
        for pos in positions:
            # Get latest price
            latest_price = await async_db.get_latest_price(pos['asset_id'])
            current_price = float(latest_price['price']) if latest_price else float(pos['average_price'])
            
            quantity = float(pos['quantity'])
            avg_price = float(pos['average_price'])
            total_cost = avg_price * quantity
            total_value = current_price * quantity
            pnl = total_value - total_cost
            pnl_percent = (pnl / total_cost * 100) if total_cost > 0 else 0
            
            result.append({
                "asset_id": pos['asset_id'],
                "name": pos.get('name', pos['asset_id']),
                "asset_type": pos.get('asset_type', 'unknown'),
                "quantity": quantity,
                "average_price": avg_price,
                "current_price": current_price,
                "total_value": round(total_value, 2),
                "total_cost": round(total_cost, 2),
                "pnl": round(pnl, 2),
                "pnl_percent": round(pnl_percent, 2)
            })
        
        return {
            "user_id": user_id,
            "positions": result,
            "count": len(result)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get positions: {str(e)}")


@router.get("/summary")
async def get_portfolio_summary(user_id: str = "default"):
    """Get portfolio summary with total P&L"""
    try:
        positions = await async_db.get_portfolio_positions(user_id)
        
        total_value = 0
        total_cost = 0
        position_details = []
        
        for pos in positions:
            # Get latest price
            latest_price = await async_db.get_latest_price(pos['asset_id'])
            current_price = float(latest_price['price']) if latest_price else float(pos['average_price'])
            
            quantity = float(pos['quantity'])
            avg_price = float(pos['average_price'])
            pos_cost = avg_price * quantity
            pos_value = current_price * quantity
            
            total_value += pos_value
            total_cost += pos_cost
            
            pnl = pos_value - pos_cost
            pnl_percent = (pnl / pos_cost * 100) if pos_cost > 0 else 0
            
            position_details.append({
                "asset_id": pos['asset_id'],
                "name": pos.get('name', pos['asset_id']),
                "asset_type": pos.get('asset_type', 'unknown'),
                "quantity": quantity,
                "average_price": avg_price,
                "current_price": current_price,
                "total_value": round(pos_value, 2),
                "total_cost": round(pos_cost, 2),
                "pnl": round(pnl, 2),
                "pnl_percent": round(pnl_percent, 2)
            })
        
        total_pnl = total_value - total_cost
        total_pnl_percent = (total_pnl / total_cost * 100) if total_cost > 0 else 0
        
        return {
            "user_id": user_id,
            "total_value": round(total_value, 2),
            "total_cost": round(total_cost, 2),
            "total_pnl": round(total_pnl, 2),
            "total_pnl_percent": round(total_pnl_percent, 2),
            "position_count": len(position_details),
            "positions": position_details
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get summary: {str(e)}")


@router.delete("/position/{asset_id}")
async def close_position(asset_id: str, user_id: str = "default"):
    """Close a position (sell all)"""
    try:
        position = await async_db.get_position(asset_id, user_id)
        
        if not position:
            raise HTTPException(status_code=404, detail=f"Position {asset_id} not found")
        
        await async_db.delete_position(asset_id, user_id)
        
        return {
            "success": True,
            "message": f"Position {asset_id} closed",
            "quantity_sold": float(position['quantity']),
            "average_price": float(position['average_price'])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to close position: {str(e)}")
