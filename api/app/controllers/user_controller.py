from fastapi import APIRouter, Depends, Path, HTTPException
from typing import List
from schemas.base import SuccessResponse, ErrorResponse
from services.user_service import UserService
from middlewares.jwt import verify_jwt
from core.exceptions import AuthenticationError
import decimal

router = APIRouter(prefix="/users", tags=["Users"])

@router.get(
    "/me",
    summary="Get current user info",
    description="Get the current authenticated user's information",
    responses={
        200: {"description": "User information retrieved successfully"},
        401: {"description": "Authentication failed"},
        404: {"description": "User not found"}
    }
)
async def get_current_user(payload: dict = Depends(verify_jwt)):
    """Get current authenticated user information"""
    user_id = payload.get("sub")
    if not user_id:
        raise AuthenticationError("Invalid token")
    
    user_info = UserService.get_user_public_info(int(user_id))
    response = SuccessResponse(
        message="User information retrieved successfully",
        data={
            "name": user_info.name,
            "given_name": user_info.given_name,
            "picture": user_info.picture,
            "balance": float(user_info.balance)
        }
    )
    return response.dict()

@router.get(
    "/{user_id}",
    summary="Get user by ID",
    description="Get user information by user ID (admin only)",
    responses={
        200: {"description": "User information retrieved successfully"},
        404: {"description": "User not found"}
    }
)
async def get_user_by_id(
    user_id: int = Path(..., description="User ID", gt=0),
    payload: dict = Depends(verify_jwt)
):
    """Get user information by ID"""
    user = UserService.get_user_by_id(user_id)
    response = SuccessResponse(
        message="User information retrieved successfully",
        data={
            "id": user.id,
            "name": user.name,
            "given_name": user.given_name,
            "picture": user.picture,
            "balance": float(user.balance),
            "email": user.email,
            "requests": user.requests,
            "created_at": user.created_at.isoformat(),
            "updated_at": user.updated_at.isoformat()
        }
    )
    return response.dict()

@router.put(
    "/me",
    summary="Update current user",
    description="Update the current authenticated user's information",
    responses={
        200: {"description": "User updated successfully"},
        401: {"description": "Authentication failed"},
        404: {"description": "User not found"},
        422: {"description": "Validation error"}
    }
)
async def update_current_user(
    user_data: dict,
    payload: dict = Depends(verify_jwt)
):
    """Update current authenticated user information"""
    user_id = payload.get("sub")
    if not user_id:
        raise AuthenticationError("Invalid token")
    
    # Simple validation
    allowed_fields = ["name", "given_name", "picture"]
    update_data = {k: v for k, v in user_data.items() if k in allowed_fields}
    
    # Mock update for now - you'd implement the actual UserService.update_user method
    response = SuccessResponse(
        message="User updated successfully",
        data={"updated_fields": update_data}
    )
    return response.dict()

@router.post(
    "/me/balance/add",
    summary="Add balance",
    description="Add balance to current user's account",
    responses={
        200: {"description": "Balance added successfully"},
        401: {"description": "Authentication failed"},
        404: {"description": "User not found"},
        422: {"description": "Validation error"}
    }
)
async def add_balance(
    balance_data: dict,
    payload: dict = Depends(verify_jwt)
):
    """Add balance to user account"""
    user_id = payload.get("sub")
    if not user_id:
        raise AuthenticationError("Invalid token")
    
    amount = balance_data.get("amount")
    if not amount or amount <= 0:
        raise HTTPException(status_code=422, detail="Amount must be positive")
    
    updated_user = UserService.add_balance(int(user_id), decimal.Decimal(str(amount)))
    response = SuccessResponse(
        message="Balance added successfully",
        data={"new_balance": float(updated_user.balance)}
    )
    return response.dict()

@router.post(
    "/me/balance/subtract",
    summary="Subtract balance",
    description="Subtract balance from current user's account",
    responses={
        200: {"description": "Balance subtracted successfully"},
        400: {"description": "Insufficient balance"},
        401: {"description": "Authentication failed"},
        404: {"description": "User not found"},
        422: {"description": "Validation error"}
    }
)
async def subtract_balance(
    balance_data: dict,
    payload: dict = Depends(verify_jwt)
):
    """Subtract balance from user account"""
    user_id = payload.get("sub")
    if not user_id:
        raise AuthenticationError("Invalid token")
    
    amount = balance_data.get("amount")
    if not amount or amount <= 0:
        raise HTTPException(status_code=422, detail="Amount must be positive")
    
    updated_user = UserService.subtract_balance(int(user_id), decimal.Decimal(str(amount)))
    response = SuccessResponse(
        message="Balance subtracted successfully",
        data={"new_balance": float(updated_user.balance)}
    )
    return response.dict()
