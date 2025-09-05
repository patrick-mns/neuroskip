"""Custom handlers for logging."""

import logging
import logging.handlers
from pathlib import Path
from typing import Optional


class TimedRotatingFileHandler(logging.handlers.TimedRotatingFileHandler):
    """Enhanced TimedRotatingFileHandler with better file management."""
    
    def __init__(self, filename: str, when: str = 'midnight', 
                 interval: int = 1, backupCount: int = 7, **kwargs):
        """Initialize the handler."""
        # Ensure the directory exists
        log_file = Path(filename)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        super().__init__(filename, when, interval, backupCount, **kwargs)


class AsyncFileHandler(logging.Handler):
    """Asynchronous file handler for high-performance logging."""
    
    def __init__(self, filename: str, maxBytes: int = 10485760, 
                 backupCount: int = 5, **kwargs):
        """Initialize the async handler."""
        super().__init__(**kwargs)
        
        # Create the underlying file handler
        self._file_handler = logging.handlers.RotatingFileHandler(
            filename, maxBytes=maxBytes, backupCount=backupCount
        )
        
        # Copy the formatter if it exists
        if self.formatter:
            self._file_handler.setFormatter(self.formatter)
    
    def emit(self, record: logging.LogRecord) -> None:
        """Emit a record asynchronously."""
        try:
            # For now, just delegate to the file handler
            # In a real implementation, you might use asyncio or threading
            self._file_handler.emit(record)
        except Exception:
            self.handleError(record)
    
    def setFormatter(self, formatter: logging.Formatter) -> None:
        """Set the formatter for both this handler and the file handler."""
        super().setFormatter(formatter)
        if hasattr(self, '_file_handler'):
            self._file_handler.setFormatter(formatter)


class StructuredHandler(logging.Handler):
    """Handler that ensures structured logging with context."""
    
    def __init__(self, base_handler: logging.Handler, **kwargs):
        """Initialize with a base handler to delegate to."""
        super().__init__(**kwargs)
        self.base_handler = base_handler
    
    def emit(self, record: logging.LogRecord) -> None:
        """Emit with additional structure."""
        # Add structured context if not present
        if not hasattr(record, 'component'):
            record.component = getattr(record, 'name', 'unknown')
        
        if not hasattr(record, 'request_id'):
            record.request_id = getattr(record, 'request_id', 'N/A')
        
        # Delegate to the base handler
        self.base_handler.emit(record)
    
    def setFormatter(self, formatter: logging.Formatter) -> None:
        """Set formatter on the base handler."""
        self.base_handler.setFormatter(formatter)
