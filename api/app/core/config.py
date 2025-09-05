"""
Modern unified configuration for NeuroSkip API using Pydantic
"""
import os
import logging
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field
from pathlib import Path


class Settings(BaseSettings):
    """Unified application settings with environment variable support"""
    
    # ==================== APP INFO ====================
    app_name: str = Field(default="NeuroSkip API", description="Application name")
    app_version: str = Field(default="2.0.0", description="Application version")
    description: str = Field(
        default="Modern API for NeuroSkip - AI-powered content analysis",
        description="Application description"
    )
    
    # ==================== ENVIRONMENT ====================
    debug: bool = Field(default=False, env="DEBUG", description="Debug mode")
    debug_worker: bool = Field(default=False, env="DEBUG_WORKER", description="Worker debug mode")
    development: bool = Field(default=False, env="DEVELOPMENT", description="Development mode")
    base_url: str = Field(default="http://localhost:8000", env="BASE_URL", description="Base URL")
    
    # ==================== SECURITY ====================
    secret_key: str = Field(env="SECRET_KEY", description="Secret key for JWT")
    jwt_secret: str = Field(env="JWT_SECRET", description="JWT secret key")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM", description="JWT algorithm")
    access_token_expire_minutes: int = Field(default=30, description="Token expiration time")
    turnstile_secret_key: str = Field(env="TURNSTILE_SECRET_KEY", description="Turnstile secret")
    
    # ==================== DATABASE ====================
    database_url: str = Field(default="sqlite:///./neuroskip.db", env="DATABASE_URL", description="Database URL")
    connection_string_postgres: Optional[str] = Field(default=None, env="CONNECTION_STRING_POSTGRES", description="PostgreSQL connection")
    
    # ==================== REDIS/CELERY ====================
    redis_string: str = Field(env="REDIS_STRING", description="Redis connection string")
    
    # ==================== CORS ====================
    cors_origins: List[str] = Field(
        default=[
            "https://neuroskip.com",
            "http://neuroskip.com", 
            "https://api.neuroskip.com",
            "http://api.neuroskip.com",
            "chrome-extension://behbngpolkoeplcaoccllaidgkmmcdoc",
            "chrome-extension://*",
            "http://localhost:*",
            "http://127.0.0.1:*",
            "http://0.0.0.0:*"
        ],
        description="CORS allowed origins"
    )
    
    # ==================== API DOCUMENTATION ====================
    @property
    def docs_url(self) -> Optional[str]:
        return "/docs" if self.debug or self.development else None
    
    @property
    def redoc_url(self) -> Optional[str]:
        return "/redoc" if self.debug or self.development else None
    
    @property
    def openapi_url(self) -> Optional[str]:
        return "/openapi.json" if self.debug or self.development else None
    
    # ==================== LOGGING ====================
    log_level: str = Field(default="INFO", env="LOG_LEVEL", description="Logging level")
    
    @property
    def log_level_int(self) -> int:
        """Convert log level string to integer"""
        return getattr(logging, self.log_level.upper(), logging.INFO)
    
    # ==================== FILE HANDLING ====================
    tmp_dir: str = Field(default="/tmp", env="TMP_DIR", description="Temporary directory")
    max_file_size: str = Field(default="100MB", env="MAX_FILE_SIZE", description="Maximum file size")
    
    @property
    def tmp_path(self) -> Path:
        """Get temporary directory as Path object"""
        return Path(self.tmp_dir)
    
    # ==================== AI SERVICES ====================
    ad_ai_url: str = Field(env="AD_AI_URL", description="AI service URL")
    
    # ==================== PAGINATION ====================
    default_page_size: int = Field(default=10, description="Default pagination size")
    max_page_size: int = Field(default=100, description="Maximum pagination size")
    
    class Config:
        """Pydantic config"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
    def _get_env_bool(self, value: str) -> bool:
        """Convert string env var to boolean"""
        return value.lower() in ("1", "true", "yes", "on")


# Global settings instance
settings = Settings()
