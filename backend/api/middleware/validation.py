"""
Input Validation Schemas
Pydantic models for request validation with business logic
"""
from pydantic import BaseModel, Field, validator, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class AssetType(str, Enum):
    """Valid asset types"""
    CRYPTO = "crypto"
    METAL = "metal"
    SHITCOIN = "shitcoin"
    STOCK = "stock"
    FOREX = "forex"


class PredictionHorizon(str, Enum):
    """Valid prediction time horizons"""
    MIN_10 = "10min"
    MIN_20 = "20min"
    MIN_30 = "30min"
    HOUR_1 = "1hour"
    HOUR_4 = "4hour"
    DAY_1 = "1day"


class TradeRequest(BaseModel):
    """Validated trade request"""
    asset_id: str = Field(..., min_length=1, max_length=20, description="Asset identifier")
    quantity: float = Field(..., gt=0, description="Quantity to trade (must be positive)")
    price: float = Field(..., gt=0, description="Price per unit (must be positive)")
    user_id: Optional[str] = Field("default", max_length=100)
    
    @field_validator('asset_id')
    @classmethod
    def validate_asset_id(cls, v):
        """Ensure asset_id is uppercase and alphanumeric"""
        if not v.replace('_', '').isalnum():
            raise ValueError("Asset ID must be alphanumeric")
        return v.upper()
    
    @field_validator('quantity')
    @classmethod
    def validate_quantity(cls, v):
        """Round to 8 decimal places (crypto precision)"""
        return round(v, 8)
    
    @field_validator('price')
    @classmethod
    def validate_price(cls, v):
        """Round to 2 decimal places"""
        return round(v, 2)


class PredictionRequest(BaseModel):
    """Validated prediction request"""
    asset_id: str = Field(..., min_length=1, max_length=20)
    horizon: Optional[PredictionHorizon] = PredictionHorizon.MIN_10
    include_sentiment: Optional[bool] = True
    confidence_threshold: Optional[float] = Field(0.0, ge=0.0, le=1.0)
    
    @field_validator('asset_id')
    @classmethod
    def validate_asset_id(cls, v):
        return v.upper()


class PriceHistoryRequest(BaseModel):
    """Validated price history request"""
    asset_id: str = Field(..., min_length=1, max_length=20)
    hours: int = Field(24, ge=1, le=720, description="Hours of history (1-720)")
    interval: Optional[str] = Field("1hour", pattern="^(1min|5min|15min|1hour|4hour|1day)$")
    
    @field_validator('asset_id')
    @classmethod
    def validate_asset_id(cls, v):
        return v.upper()


class AlertRequest(BaseModel):
    """Validated alert creation request"""
    asset_id: str = Field(..., min_length=1, max_length=20)
    condition: str = Field(..., pattern="^(above|below|change)$")
    threshold: float = Field(..., gt=0)
    notification_type: str = Field("telegram", pattern="^(telegram|email|both)$")
    user_id: Optional[str] = Field("default", max_length=100)
    
    @field_validator('asset_id')
    @classmethod
    def validate_asset_id(cls, v):
        return v.upper()


class PortfolioFilters(BaseModel):
    """Filters for portfolio queries"""
    user_id: Optional[str] = Field("default", max_length=100)
    asset_type: Optional[AssetType] = None
    min_value: Optional[float] = Field(None, ge=0)
    sort_by: Optional[str] = Field("pnl", pattern="^(pnl|value|quantity|asset_id)$")
    sort_order: Optional[str] = Field("desc", pattern="^(asc|desc)$")


class BacktestRequest(BaseModel):
    """Validated backtesting request"""
    strategy: str = Field(..., min_length=1, max_length=50)
    asset_ids: List[str] = Field(..., min_items=1, max_items=20)
    start_date: datetime
    end_date: datetime
    initial_capital: float = Field(10000.0, gt=0, le=1000000)
    
    @field_validator('asset_ids')
    @classmethod
    def validate_asset_ids(cls, v):
        return [asset.upper() for asset in v]
    
    @field_validator('end_date')
    @classmethod
    def validate_date_range(cls, v, info):
        if 'start_date' in info.data and v <= info.data['start_date']:
            raise ValueError("end_date must be after start_date")
        return v


# Response models with validation
class ErrorResponse(BaseModel):
    """Standard error response"""
    error: bool = True
    status_code: int
    message: str
    error_id: Optional[str] = None
    path: Optional[str] = None
    timestamp: datetime


class SuccessResponse(BaseModel):
    """Standard success response"""
    success: bool = True
    message: str
    data: Optional[dict] = None
    timestamp: datetime = Field(default_factory=datetime.now)
