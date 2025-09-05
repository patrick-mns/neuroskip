from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from core.exceptions import BaseAPIException
from schemas.base import ErrorResponse
from core.logging import get_logger
import traceback

# Initialize logger for error handlers
logger = get_logger('core.error_handlers')

async def base_exception_handler(request: Request, exc: BaseAPIException):
    """Handle custom base API exceptions"""
    logger.error(f"API Exception: {exc.message} - {exc.error_code}")
    
    error_response = ErrorResponse(
        message=exc.message,
        error_code=exc.error_code,
        details={"path": str(request.url)}
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.dict()
    )

async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle FastAPI HTTP exceptions"""
    logger.error(f"HTTP Exception: {exc.detail} - Status: {exc.status_code}")
    
    error_response = ErrorResponse(
        message=exc.detail,
        error_code=f"HTTP_{exc.status_code}",
        details={"path": str(request.url)}
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.dict()
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors"""
    logger.error(f"Validation Exception: {exc.errors()}")
    
    error_response = ErrorResponse(
        message="Validation failed",
        error_code="VALIDATION_ERROR",
        details={
            "path": str(request.url),
            "errors": exc.errors()
        }
    )
    
    return JSONResponse(
        status_code=422,
        content=error_response.dict()
    )

async def general_exception_handler(request: Request, exc: Exception):
    """Handle general unexpected exceptions"""
    logger.error(f"Unexpected Exception: {str(exc)}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    
    error_response = ErrorResponse(
        message="Internal server error",
        error_code="INTERNAL_SERVER_ERROR",
        details={"path": str(request.url)}
    )
    
    return JSONResponse(
        status_code=500,
        content=error_response.dict()
    )
