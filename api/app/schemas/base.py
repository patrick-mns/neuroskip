from typing import Optional, Any
from datetime import datetime

class BaseResponse:
    """Base response model for all API responses"""
    def __init__(self, success: bool = True, message: str = "Success", timestamp: str = None):
        self.success = success
        self.message = message
        self.timestamp = timestamp or datetime.utcnow().isoformat()
    
    def dict(self):
        return {
            "success": self.success,
            "message": self.message,
            "timestamp": self.timestamp
        }

class SuccessResponse(BaseResponse):
    """Success response with data"""
    def __init__(self, message: str = "Success", data: Optional[Any] = None, **kwargs):
        super().__init__(message=message, **kwargs)
        self.data = data
    
    def dict(self):
        response = super().dict()
        response["data"] = self.data
        return response

class ErrorResponse(BaseResponse):
    """Error response model"""
    def __init__(self, message: str = "Error", error_code: Optional[str] = None, 
                 details: Optional[dict] = None, **kwargs):
        super().__init__(success=False, message=message, **kwargs)
        self.error_code = error_code
        self.details = details
    
    def dict(self):
        response = super().dict()
        if self.error_code:
            response["error_code"] = self.error_code
        if self.details:
            response["details"] = self.details
        return response

class PaginatedResponse(SuccessResponse):
    """Paginated response model"""
    def __init__(self, message: str = "Success", data: Optional[Any] = None, 
                 pagination: dict = None, **kwargs):
        super().__init__(message=message, data=data, **kwargs)
        self.pagination = pagination or {
            "page": 1,
            "limit": 10,
            "total": 0,
            "total_pages": 0
        }
    
    def dict(self):
        response = super().dict()
        response["pagination"] = self.pagination
        return response
