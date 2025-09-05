from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal
from datetime import datetime

class UserBase(BaseModel):
    """Base user schema"""
    email: str
    name: Optional[str] = None
    given_name: Optional[str] = None
    picture: Optional[str] = None

class UserCreate(UserBase):
    """User creation schema"""
    google_id: str

class UserUpdate(BaseModel):
    """User update schema"""
    name: Optional[str] = None
    given_name: Optional[str] = None
    picture: Optional[str] = None

class UserResponse(UserBase):
    """User response schema"""
    id: int
    balance: Decimal = Field(decimal_places=2)
    requests: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserPublicResponse(BaseModel):
    """Public user response (limited info)"""
    name: Optional[str] = None
    given_name: Optional[str] = None
    picture: Optional[str] = None
    balance: Decimal = Field(decimal_places=2)

    class Config:
        from_attributes = True

class BalanceUpdate(BaseModel):
    """Balance update schema"""
    amount: Decimal = Field(gt=0, decimal_places=2, description="Amount to add/subtract from balance")
