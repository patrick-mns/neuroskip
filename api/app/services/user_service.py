from typing import Optional, List
from decimal import Decimal
from models.User import User
from schemas.user import UserCreate, UserUpdate, UserResponse, UserPublicResponse
from core.exceptions import UserNotFoundError, InsufficientBalanceError

class UserService:
    """Service layer for user operations"""
    
    @staticmethod
    def create_user(user_data: UserCreate) -> UserResponse:
        """Create a new user"""
        try:
            user = User.create(
                google_id=user_data.google_id,
                email=user_data.email,
                name=user_data.name,
                given_name=user_data.given_name,
                picture=user_data.picture
            )
            return UserResponse.from_orm(user)
        except Exception as e:
            raise Exception(f"Failed to create user: {str(e)}")
    
    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[UserResponse]:
        """Get user by ID"""
        user = User.get_or_none(User.id == user_id)
        if not user:
            raise UserNotFoundError(f"User with ID {user_id} not found")
        return UserResponse.from_orm(user)
    
    @staticmethod
    def get_user_by_google_id(google_id: str) -> Optional[UserResponse]:
        """Get user by Google ID"""
        user = User.get_user_by_google_id(google_id)
        if not user:
            return None
        return UserResponse.from_orm(user)
    
    @staticmethod
    def update_user(user_id: int, user_data: UserUpdate) -> UserResponse:
        """Update user information"""
        user = User.get_or_none(User.id == user_id)
        if not user:
            raise UserNotFoundError(f"User with ID {user_id} not found")
        
        update_data = user_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        user.save()
        return UserResponse.from_orm(user)
    
    @staticmethod
    def add_balance(user_id: int, amount: Decimal) -> UserResponse:
        """Add balance to user account"""
        user = User.get_or_none(User.id == user_id)
        if not user:
            raise UserNotFoundError(f"User with ID {user_id} not found")
        
        user.add_balance(amount)
        return UserResponse.from_orm(user)
    
    @staticmethod
    def subtract_balance(user_id: int, amount: Decimal) -> UserResponse:
        """Subtract balance from user account"""
        user = User.get_or_none(User.id == user_id)
        if not user:
            raise UserNotFoundError(f"User with ID {user_id} not found")
        
        if user.balance < amount:
            raise InsufficientBalanceError("Insufficient balance")
        
        user.subtract_balance(float(amount))
        return UserResponse.from_orm(user)
    
    @staticmethod
    def get_user_public_info(user_id: int) -> UserPublicResponse:
        """Get public user information"""
        user = User.get_or_none(User.id == user_id)
        if not user:
            raise UserNotFoundError(f"User with ID {user_id} not found")
        
        return UserPublicResponse.from_orm(user)
    
    @staticmethod
    def delete_user(user_id: int) -> bool:
        """Delete user"""
        user = User.get_or_none(User.id == user_id)
        if not user:
            raise UserNotFoundError(f"User with ID {user_id} not found")
        
        user.delete_instance()
        return True
