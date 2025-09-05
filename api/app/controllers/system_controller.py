from fastapi import APIRouter, Path
from schemas.base import SuccessResponse
from core.config import settings

router = APIRouter(tags=["System"])

from fastapi import APIRouter, Path
from core.config import settings

router = APIRouter(tags=["System"])

@router.get(
    "/health",
    summary="Health check",
    description="Check if the API is running and healthy"
)
async def health_check():
    """Health check endpoint"""
    return {
        "success": True,
        "message": "API is healthy",
        "data": {
            "status": "healthy",
            "version": "2.0.0",
            "environment": "development" if settings.development else "production"
        }
    }

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
    
    return {
        "success": True,
        "message": "Extension status retrieved successfully",
        "data": {
            "status": f"{version} OK",
            "api_version": "2.0.0",
            "compatible": True
        }
    }

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
            "api_version": "2.0.0",
            "compatible": True
        }
    )
    return response.dict()
