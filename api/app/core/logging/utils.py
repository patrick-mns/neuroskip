"""Logging utilities and decorators."""

import functools
import time
from typing import Callable, Any
from .config import get_logger


def log_execution_time(logger_name: str = None):
    """Decorator to log function execution time."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            logger = get_logger(logger_name or func.__module__)
            start_time = time.time()
            
            try:
                logger.debug(f"Starting execution of {func.__name__}")
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                logger.info(f"{func.__name__} executed successfully in {execution_time:.4f}s")
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(f"{func.__name__} failed after {execution_time:.4f}s: {str(e)}")
                raise
        
        return wrapper
    return decorator


def log_api_call(logger_name: str = 'api'):
    """Decorator to log API calls with request/response info."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            logger = get_logger(logger_name)
            
            # Try to extract request info if available
            request_info = {}
            if args and hasattr(args[0], 'method'):
                request_info['method'] = args[0].method
                request_info['path'] = getattr(args[0], 'path', 'unknown')
            
            logger.info(f"API call started: {func.__name__}", extra=request_info)
            
            try:
                result = func(*args, **kwargs)
                logger.info(f"API call completed: {func.__name__}")
                return result
            except Exception as e:
                logger.error(f"API call failed: {func.__name__} - {str(e)}")
                raise
        
        return wrapper
    return decorator


class LogContext:
    """Context manager for adding structured logging context."""
    
    def __init__(self, logger_name: str, **context):
        self.logger = get_logger(logger_name)
        self.context = context
        self.old_context = {}
    
    def __enter__(self):
        # Store old context and add new context
        for key, value in self.context.items():
            if hasattr(self.logger, key):
                self.old_context[key] = getattr(self.logger, key)
            setattr(self.logger, key, value)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Restore old context
        for key in self.context.keys():
            if key in self.old_context:
                setattr(self.logger, key, self.old_context[key])
            else:
                delattr(self.logger, key)


def with_logging_context(**context):
    """Decorator to add logging context to a function."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            logger_name = context.get('logger', func.__module__)
            with LogContext(logger_name, **context):
                return func(*args, **kwargs)
        return wrapper
    return decorator
