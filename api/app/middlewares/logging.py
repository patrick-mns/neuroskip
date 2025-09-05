import time
import uuid
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from core.logging import get_logger
import json

# Initialize logger for request middleware
logger = get_logger('middleware.logging')

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging API requests and responses"""
    
    async def dispatch(self, request: Request, call_next):
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        
        # Start timing
        start_time = time.time()
        
        # Log request
        logger.info(f"[{request_id}] {request.method} {request.url}")
        
        # Add request ID to request state
        request.state.request_id = request_id
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Log response
            logger.info(
                f"[{request_id}] Response: {response.status_code} "
                f"({process_time:.3f}s)"
            )
            
            # Add custom headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = f"{process_time:.3f}"
            
            return response
            
        except Exception as e:
            # Calculate processing time for errors
            process_time = time.time() - start_time
            
            # Log error
            logger.error(
                f"[{request_id}] Error: {str(e)} "
                f"({process_time:.3f}s)"
            )
            
            raise
