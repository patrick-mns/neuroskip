from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class SegmentBase(BaseModel):
    """Base segment schema"""
    text: Optional[str] = None
    start_time: Optional[float] = Field(None, ge=0)
    end_time: Optional[float] = Field(None, ge=0)

class SegmentCreate(SegmentBase):
    """Segment creation schema"""
    pass

class SegmentUpdate(SegmentBase):
    """Segment update schema"""
    pass

class SegmentResponse(SegmentBase):
    """Segment response schema"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class StatusResponse(BaseModel):
    """Status response schema"""
    status: str = Field(..., description="Status message")
    version: Optional[str] = Field(None, description="API version")
