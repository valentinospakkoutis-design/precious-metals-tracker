"""
Middleware Package
Contains error handling, logging, and validation middleware
"""
from .error_handler import (
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler,
    ErrorHandlerMiddleware
)
from .logging_middleware import RequestLoggingMiddleware, log_request_body
from .validation import (
    TradeRequest,
    PredictionRequest,
    PriceHistoryRequest,
    AlertRequest,
    PortfolioFilters,
    BacktestRequest,
    ErrorResponse,
    SuccessResponse,
    AssetType,
    PredictionHorizon
)

__all__ = [
    'http_exception_handler',
    'validation_exception_handler',
    'general_exception_handler',
    'ErrorHandlerMiddleware',
    'RequestLoggingMiddleware',
    'log_request_body',
    'TradeRequest',
    'PredictionRequest',
    'PriceHistoryRequest',
    'AlertRequest',
    'PortfolioFilters',
    'BacktestRequest',
    'ErrorResponse',
    'SuccessResponse',
    'AssetType',
    'PredictionHorizon'
]
