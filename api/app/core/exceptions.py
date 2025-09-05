"""
Custom exceptions for the application
"""

class BaseAPIException(Exception):
    """Base exception for all API exceptions"""
    def __init__(self, message: str, status_code: int = 500, error_code: str = None):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or self.__class__.__name__
        super().__init__(message)

class ValidationError(BaseAPIException):
    """Validation error exception"""
    def __init__(self, message: str = "Validation failed"):
        super().__init__(message, status_code=422, error_code="VALIDATION_ERROR")

class AuthenticationError(BaseAPIException):
    """Authentication error exception"""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401, error_code="AUTHENTICATION_ERROR")

class AuthorizationError(BaseAPIException):
    """Authorization error exception"""
    def __init__(self, message: str = "Access denied"):
        super().__init__(message, status_code=403, error_code="AUTHORIZATION_ERROR")

class UserNotFoundError(BaseAPIException):
    """User not found exception"""
    def __init__(self, message: str = "User not found"):
        super().__init__(message, status_code=404, error_code="USER_NOT_FOUND")

class InsufficientBalanceError(BaseAPIException):
    """Insufficient balance exception"""
    def __init__(self, message: str = "Insufficient balance"):
        super().__init__(message, status_code=400, error_code="INSUFFICIENT_BALANCE")

class ResourceNotFoundError(BaseAPIException):
    """Resource not found exception"""
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404, error_code="RESOURCE_NOT_FOUND")

class ConflictError(BaseAPIException):
    """Conflict error exception"""
    def __init__(self, message: str = "Resource conflict"):
        super().__init__(message, status_code=409, error_code="CONFLICT_ERROR")

class InternalServerError(BaseAPIException):
    """Internal server error exception"""
    def __init__(self, message: str = "Internal server error"):
        super().__init__(message, status_code=500, error_code="INTERNAL_SERVER_ERROR")

class ServiceUnavailableError(BaseAPIException):
    """Service unavailable exception"""
    def __init__(self, message: str = "Service temporarily unavailable"):
        super().__init__(message, status_code=503, error_code="SERVICE_UNAVAILABLE")
