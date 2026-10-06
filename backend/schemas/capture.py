from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

class CaptureBase(BaseModel):
    filename: str

class CaptureResponse(BaseModel):
    id: str
    filename: str
    file_size_bytes: int
    packet_count: int
    total_bytes: int
    duration_seconds: float
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    status: str
    error_message: Optional[str] = None
    is_demo: int
    created_at: datetime

    class Config:
        from_attributes = True

class CaptureSummary(BaseModel):
    id: str
    filename: str
    file_size_bytes: int
    packet_count: int
    total_bytes: int
    duration_seconds: float
    status: str
    is_demo: int
    findings_count: int
    protocols_count: int
    created_at: datetime

    class Config:
        from_attributes = True
