from fastapi import APIRouter, Depends, HTTPException, Path
from typing import Optional

from sympy import false
from schemas.base import SuccessResponse, ErrorResponse
from models.User import User
from models.Segment import Segment
from middlewares.jwt import verify_jwt
from tasks.youtube_processing import process_youtube_video
from services.lock_service import is_task_locked, lock_task, unlock_task
import httpx
from core.auth import create_access_token
import decimal

router = APIRouter(prefix="/extension", tags=["Browser Extension"])

class GoogleLoginRequest:
    def __init__(self, token: str):
        self.token = token

@router.get(
    "/status/{version}",
    summary="Extension status check",
    description="Check API status for browser extension",
    responses={
        200: {"description": "Status retrieved successfully"},
        503: {"description": "Service under maintenance"}
    }
)
async def extension_status(
    version: str = Path(..., description="Extension version", min_length=1)
):
    """Extension status check endpoint"""
    # Uncomment the line below for maintenance mode
    # raise HTTPException(status_code=503, detail="⚠️ Service under maintenance!")
    
    response = SuccessResponse(
        message="Extension status retrieved successfully",
        data={
            "status": f"{version} OK",
            "compatible": True,
            "maintenance": False
        }
    )
    return response.dict()

@router.post(
    "/login/google",
    summary="Google OAuth login",
    description="Authenticate user with Google OAuth token",
    responses={
        200: {"description": "Login successful"},
        400: {"description": "Token required"},
        401: {"description": "Invalid token"},
        500: {"description": "Authentication error"}
    }
)
async def google_login(request_data: dict):
    """Authenticate user with Google OAuth token"""
    
    token = request_data.get("token")
    if not token:
        raise HTTPException(status_code=400, detail="Token is required.")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://www.googleapis.com/oauth2/v3/userinfo",
                headers={"Authorization": f"Bearer {token}"}
            )
            
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code, 
                detail="Failed to fetch user info from Google."
            )
        
        user_info = response.json()
        user = User.get_user_by_google_id(user_info["sub"]) 
        
        if user is None:
            user = User(
                google_id=user_info["sub"],
                email=user_info["email"],
                name=user_info.get("name"),
                given_name=user_info.get("given_name"),
                picture=user_info.get("picture"),
            )
            user.save()
        
        access_token = create_access_token(
            data={"sub": str(user.id), "role": "user"}
        )
        
        response = SuccessResponse(
            message="Login successful",
            data={
                "userInfo": {
                    "given_name": user.given_name,
                    "picture": user.picture,
                    "balance": float(user.balance)
                },
                "access_token": access_token,
                "token_type": "bearer"
            }
        )
        return response.dict()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error validating user: {str(e)}")

@router.post(
    "/me",
    summary="Get current user info",
    description="Get current authenticated user information for extension",
    responses={
        200: {"description": "User info retrieved successfully"},
        401: {"description": "Authentication failed"},
        404: {"description": "User not found"}
    }
)
async def get_current_user_extension(payload: dict = Depends(verify_jwt)):
    """Get current user information for extension"""
    try:
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token.")
        
        user = User.get_or_none(User.id == int(user_id))
        if user is None:
            raise HTTPException(status_code=404, detail="User not found.")
        
        response = SuccessResponse(
            message="User information retrieved successfully",
            data={
                "name": user.name,
                "given_name": user.given_name,
                "picture": user.picture,
                "balance": float(user.balance)
            }
        )
        return response.dict()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get(
    "/segments/{external_id}/{provider}",
    summary="Get video segments",
    description="Get transcription segments for a video",
    responses={
        200: {"description": "Segments retrieved successfully"},
        401: {"description": "Authentication failed"},
        404: {"description": "User not found"},
        422: {"description": "Insufficient balance"}
    }
)
async def get_segments_extension(
    external_id: str = Path(..., description="Video ID"),
    provider: str = Path(..., description="Video provider (e.g., youtube)"),
    payload: dict = Depends(verify_jwt)
):
    """Get video transcription segments"""
    
    locked = is_task_locked(external_id)
    user_id = payload.get("sub")
    
    if not user_id:
        raise HTTPException(status_code=404, detail="User ID not found in token")

    user = User.get_or_none(User.id == int(user_id))
    if user is None:
        raise HTTPException(status_code=404, detail="User not found.")
    
    # if user.balance < decimal.Decimal('0.02'):  
    #     raise HTTPException(status_code=422, detail="Insufficient balance")
    
    try:
        # Check if segments already exist
        segments = Segment.select().where(
            (Segment.external_id == external_id) & 
            (Segment.provider == provider)
        )
        
        if segments.exists():
            segments_data = [
                {
                    "start": segment.start,
                    "end": segment.end,
                    "text": segment.text,
                    "type": segment.type
                }
                for segment in segments.order_by(Segment.created_at)
            ]
            
            response = SuccessResponse(
                message="Segments retrieved successfully",
                data={
                    "segments": segments_data,
                    "external_id": external_id,
                    "provider": provider,
                    "cached": True
                }
            )
            return response.dict()
        
        # If not cached and not locked, start processing
        if not locked:
            lock_task(external_id)
            try:
                # Create video_info dict with provider info
                video_info = {"provider": provider}
                print(f"Dispatching task for external_id: {external_id}, provider: {provider}, user_id: {user.id}")
                process_youtube_video.apply_async(
                    args=[external_id, user.id, False], 
                    queue="urgent"
                )
                print(f"Task dispatched successfully for external_id: {external_id}")
            except Exception as e:
                print(f"Error dispatching task: {str(e)}")
                unlock_task(external_id)
                raise HTTPException(
                    status_code=500, 
                    detail="Failed to start video processing"
                )
        
        message = "Video processing started" if not locked else "Video processing in progress"
        response = SuccessResponse(
            message=message,
            data={
                "external_id": external_id,
                "provider": provider,
                "status": "processing",
                "cached": False
            }
        )
        return response.dict()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
