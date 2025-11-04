"""
Portfolio models for tracking user investments
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum

class TransactionType(str, Enum):
    """Transaction types"""
    BUY = "BUY"
    SELL = "SELL"

class PortfolioPosition(BaseModel):
    """Portfolio position model"""
    id: Optional[int] = None
    user_id: str = Field(..., description="User identifier (e.g., telegram_user_id)")
    asset_id: str = Field(..., description="Asset symbol (BTC, ETH, GOLD, etc.)")
    quantity: float = Field(..., gt=0, description="Number of units held")
    avg_buy_price: float = Field(..., gt=0, description="Average purchase price per unit")
    total_invested: float = Field(..., gt=0, description="Total amount invested")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "telegram_12345",
                "asset_id": "BTC",
                "quantity": 0.5,
                "avg_buy_price": 45000.0,
                "total_invested": 22500.0
            }
        }

class Transaction(BaseModel):
    """Buy/Sell transaction model"""
    user_id: str = Field(..., description="User identifier")
    asset_id: str = Field(..., description="Asset symbol")
    transaction_type: TransactionType = Field(..., description="BUY or SELL")
    quantity: float = Field(..., gt=0, description="Number of units")
    price_per_unit: float = Field(..., gt=0, description="Price per unit at transaction")
    total_amount: Optional[float] = None  # Calculated automatically
    timestamp: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "telegram_12345",
                "asset_id": "BTC",
                "transaction_type": "BUY",
                "quantity": 0.1,
                "price_per_unit": 45000.0
            }
        }

class PortfolioSummary(BaseModel):
    """Portfolio summary with P&L calculations"""
    user_id: str
    positions: List[dict] = Field(default_factory=list)
    total_invested: float = 0.0
    current_value: float = 0.0
    total_pnl: float = 0.0
    total_pnl_pct: float = 0.0
    last_updated: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "telegram_12345",
                "positions": [
                    {
                        "asset_id": "BTC",
                        "quantity": 0.5,
                        "avg_buy_price": 45000.0,
                        "current_price": 50000.0,
                        "invested": 22500.0,
                        "current_value": 25000.0,
                        "pnl": 2500.0,
                        "pnl_pct": 11.11
                    }
                ],
                "total_invested": 22500.0,
                "current_value": 25000.0,
                "total_pnl": 2500.0,
                "total_pnl_pct": 11.11,
                "last_updated": "2025-10-30T12:00:00"
            }
        }

class PositionDetail(BaseModel):
    """Detailed position with current market data"""
    asset_id: str
    asset_name: str
    quantity: float
    avg_buy_price: float
    current_price: float
    invested: float
    current_value: float
    pnl: float
    pnl_pct: float
    change_24h: Optional[float] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "asset_id": "BTC",
                "asset_name": "Bitcoin",
                "quantity": 0.5,
                "avg_buy_price": 45000.0,
                "current_price": 50000.0,
                "invested": 22500.0,
                "current_value": 25000.0,
                "pnl": 2500.0,
                "pnl_pct": 11.11,
                "change_24h": 2.5
            }
        }
