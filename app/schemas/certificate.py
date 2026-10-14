from datetime import date, datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from app.schemas.element import CanvasElement


class CertificateVerificationResponse(BaseModel):
    """
    Public Verification Schema
    Returned when an employer or student scans the QR code.
    Notice the dynamic 'metadata' dict: it holds ANY custom fields from Excel!
    """
    certificate_id: str = Field(..., description="UUID printed on certificate")
    recipient_name: str = Field(..., description="Recipient full name")
    recipient_id: Optional[str] = Field(default=None, description="Member ID or Roll No")
    event_name: str = Field(..., description="Event or Course title")
    issue_date: date = Field(..., description="Date certificate was issued")
    status: str = Field(default="ACTIVE", description="'ACTIVE', 'REVOKED', or 'EXPIRED'")
    
    # Dynamic metadata: holds College, Degree, Application No, Rank, etc.
    metadata: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Dynamic key-value pairs from the Excel sheet"
    )
    
    verified_at: datetime = Field(
        default_factory=datetime.utcnow, 
        description="Timestamp of verification request"
    )

    class Config:
        from_attributes = True


class SingleCertificatePreview(BaseModel):
    """Schema for previewing a single certificate before batch generating"""
    record_index: int = Field(default=0, ge=0)
    elements: List[CanvasElement]
    sample_data: Dict[str, Any]
