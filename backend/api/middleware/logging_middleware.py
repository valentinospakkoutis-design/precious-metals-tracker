"""
Request/Response Logging Middleware
Logs all API requests with timing, status codes, and request details
"""
import time
import logging
from fastapi import Request
import json

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware:
    """Log all HTTP requests with timing and details"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        
        request = Request(scope, receive)
        start_time = time.time()
        
        # Extract request details
        method = request.method
        url = str(request.url)
        client_ip = request.client.host if request.client else "unknown"
        
        # Log request
        logger.info(f"➡️  {method} {url} from {client_ip}")
        
        # Track response
        status_code = 200
        
        async def send_wrapper(message):
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            await send(message)
        
        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000
            
            # Color-code by status
            if status_code < 400:
                log_level = logging.INFO
                emoji = "✅"
            elif status_code < 500:
                log_level = logging.WARNING
                emoji = "⚠️"
            else:
                log_level = logging.ERROR
                emoji = "❌"
            
            logger.log(
                log_level,
                f"{emoji} {method} {url} - {status_code} - {duration_ms:.2f}ms"
            )


async def log_request_body(request: Request):
    """Utility to log request body (use sparingly - can be large)"""
    try:
        body = await request.body()
        if body:
            try:
                json_body = json.loads(body)
                logger.debug(f"Request body: {json.dumps(json_body, indent=2)}")
            except json.JSONDecodeError:
                logger.debug(f"Request body (raw): {body[:500]}")  # Truncate large bodies
    except Exception as e:
        logger.warning(f"Could not read request body: {e}")
