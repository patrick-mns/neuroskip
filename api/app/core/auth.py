from core.config import settings
from jose import jwt
from datetime import datetime, timedelta


def create_access_token(data: dict, expires_delta: timedelta = timedelta(hours=6)):
    """
    Create a JWT access token with the given data and expiration time.
    
    Args:
        data: Dictionary containing the token payload
        expires_delta: Token expiration time (default: 6 hours)
        
    Returns:
        Encoded JWT token as string
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return encoded_jwt
