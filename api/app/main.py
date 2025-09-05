import os
import debugpy

# Modern logging setup
from core.logging import setup_logging, get_app_logger

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

# New imports for modern architecture
from core.config import settings
from core.exceptions import BaseAPIException
from core.error_handlers import (
    base_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler
)

# Import controllers
from controllers.user_controller import router as user_router
from controllers.system_controller import router as system_router
from controllers.extension_controller import router as extension_router

# Import middlewares
from middlewares.logging import RequestLoggingMiddleware

import migrate

def create_app():
    # Setup modern logging first
    setup_logging(settings.log_level)
    logger = get_app_logger()
    
    # Run database migrations
    logger.info("Running database migrations...")
    try:
        migrate.create_tables()
        logger.info("Database migrations completed successfully")
    except Exception as e:
        logger.error(f"Failed to run database migrations: {e}")
        raise
    
    # Initialize FastAPI with modern configuration
    app = FastAPI(
        title=settings.app_name,
        description=settings.description,
        version=settings.app_version,
        docs_url=settings.docs_url,
        redoc_url=settings.redoc_url,
        openapi_url=settings.openapi_url,
        openapi_tags=[
            {
                "name": "System",
                "description": "System health and status endpoints"
            },
            {
                "name": "Users", 
                "description": "User management and profile operations"
            },
            {
                "name": "Browser Extension",
                "description": "Browser extension specific endpoints"
            }
        ]
    )
     
    if settings.debug:
        debugpy.listen(("0.0.0.0", 5678))
        logger.debug("Debugpy escutando na porta 5678 para FastAPI...")

    # Setup CORS
    cors_origins = settings.cors_origins.copy()
    if settings.development:
        cors_origins.extend([
            settings.base_url,
            "*"  # Allow all origins in development
        ])
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins if not settings.development else ["*"], 
        allow_credentials=True,
        allow_methods=["POST", "PUT", "GET", "OPTIONS", "DELETE", "PATCH"],
        allow_headers=["*"],
        expose_headers=["*"]
    )
    
    # Add custom middlewares
    app.add_middleware(RequestLoggingMiddleware)

    # Register exception handlers
    app.add_exception_handler(BaseAPIException, base_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)

    # Register modern API routes
    app.include_router(system_router, prefix="/v2")
    app.include_router(user_router, prefix="/v2")
    app.include_router(extension_router, prefix="/v2")
    
    return app

app = create_app()  