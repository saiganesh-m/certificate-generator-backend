from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from app.schemas.element import CanvasElement


class TemplateBase(BaseModel):
    """Common attributes shared across Template schemas"""
    title: str = Field(..., min_length=1, max_length=255, description="Template title, e.g. 'Zap10X Series 11'")
    description: Optional[str] = Field(default=None, description="Optional description or notes")
    page_width: float = Field(default=842.25, gt=0, description="Page width in points (default A4 landscape)")
    page_height: float = Field(default=595.5, gt=0, description="Page height in points (default A4 landscape)")


class TemplateCreate(TemplateBase):
    """
    Schema sent by React when saving a certificate design.
    Notice it embeds a list of CanvasElement objects!
    """
    base_pdf_filename: str = Field(..., description="Filename of the uploaded background PDF")
    elements: List[CanvasElement] = Field(
        default_factory=list, 
        description="Array of canvas elements (text, QR code, signatures)"
    )


class TemplateResponse(TemplateBase):
    """
    Schema returned by FastAPI when React fetches saved templates.
    Includes the database ID and timestamps.
    """
    id: str
    base_pdf_path: str
    layout_schema: List[CanvasElement]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Allows Pydantic to read directly from SQLAlchemy models!
