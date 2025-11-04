"""
Request Queue Manager
Protects against DDoS by limiting concurrent requests
"""

import asyncio
from fastapi import HTTPException
from typing import Callable, Any
import logging
import time

logger = logging.getLogger(__name__)


class RequestQueue:
    """
    Async request queue to prevent DDoS attacks
    
    Limits the number of concurrent requests to expensive operations
    Returns HTTP 503 when queue is full
    """
    
    def __init__(self, max_size: int = 100, timeout: int = 30):
        """
        Initialize request queue
        
        Args:
            max_size: Maximum number of requests in queue
            timeout: Maximum seconds to wait for queue space
        """
        self.queue = asyncio.Queue(maxsize=max_size)
        self.max_size = max_size
        self.timeout = timeout
        self.processing_count = 0
        self.total_requests = 0
        self.rejected_requests = 0
        
    async def process_request(self, func: Callable, *args, **kwargs) -> Any:
        """
        Process a request through the queue
        
        Args:
            func: Async function to execute
            *args, **kwargs: Arguments for the function
            
        Returns:
            Result from the function
            
        Raises:
            HTTPException: 503 if queue is full
        """
        self.total_requests += 1
        
        # Check if queue is full
        if self.queue.full():
            self.rejected_requests += 1
            logger.warning(
                f"Request queue full ({self.max_size}/{self.max_size}). "
                f"Rejected: {self.rejected_requests}/{self.total_requests}"
            )
            raise HTTPException(
                status_code=503,
                detail=f"Server is busy. Queue full ({self.max_size} requests). "
                       f"Please try again in a few moments."
            )
        
        try:
            # Put request in queue
            await asyncio.wait_for(
                self.queue.put(time.time()),
                timeout=self.timeout
            )
            
            self.processing_count += 1
            logger.info(f"Processing request (Queue: {self.queue.qsize()}/{self.max_size})")
            
            # Execute the function
            result = await func(*args, **kwargs)
            
            return result
            
        except asyncio.TimeoutError:
            self.rejected_requests += 1
            logger.error(f"Request timeout waiting for queue space ({self.timeout}s)")
            raise HTTPException(
                status_code=503,
                detail=f"Server timeout. Could not process request within {self.timeout}s"
            )
            
        finally:
            # Remove from queue
            try:
                await self.queue.get()
                self.queue.task_done()
                self.processing_count -= 1
            except Exception as e:
                logger.error(f"Error removing from queue: {e}")
    
    def get_stats(self) -> dict:
        """Get queue statistics"""
        return {
            "queue_size": self.queue.qsize(),
            "max_size": self.max_size,
            "processing_count": self.processing_count,
            "total_requests": self.total_requests,
            "rejected_requests": self.rejected_requests,
            "success_rate": (
                (self.total_requests - self.rejected_requests) / self.total_requests * 100
                if self.total_requests > 0 else 100
            )
        }


# Global queue instances for different endpoint types
prediction_queue = RequestQueue(max_size=50, timeout=30)  # ML predictions
portfolio_queue = RequestQueue(max_size=100, timeout=10)  # Portfolio operations
general_queue = RequestQueue(max_size=200, timeout=5)     # General API calls


async def queue_prediction(func: Callable, *args, **kwargs):
    """Queue a prediction request"""
    return await prediction_queue.process_request(func, *args, **kwargs)


async def queue_portfolio(func: Callable, *args, **kwargs):
    """Queue a portfolio operation"""
    return await portfolio_queue.process_request(func, *args, **kwargs)


async def queue_general(func: Callable, *args, **kwargs):
    """Queue a general API request"""
    return await general_queue.process_request(func, *args, **kwargs)


def get_all_queue_stats() -> dict:
    """Get statistics for all queues"""
    return {
        "prediction_queue": prediction_queue.get_stats(),
        "portfolio_queue": portfolio_queue.get_stats(),
        "general_queue": general_queue.get_stats()
    }


# Example usage in endpoints:
"""
from security.request_queue import queue_prediction

@app.post("/api/v1/predict")
async def predict_price(asset_id: str):
    async def do_prediction():
        # Your expensive ML prediction logic
        return {"prediction": 123.45}
    
    # Process through queue
    return await queue_prediction(do_prediction)
"""
