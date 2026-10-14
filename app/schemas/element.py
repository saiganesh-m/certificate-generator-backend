from typing import Literal, Optional
from pydantic import BaseModel, Field


class CanvasElement(BaseModel):
    """
    Schema for a single draggable element on the certificate canvas.
    Validated by Pydantic before drawing onto the PDF.
    """

    # 1. Identification
    id: str = Field(..., description="Unique element ID, e.g. 'elem_name' or 'elem_qr'")
    type: Literal["text", "qr_code", "image"] = Field(
        default="text", 
        description="Type of canvas element"
    )

    # 2. Data Mapping
    # Which column from the uploaded Excel sheet supplies the text for this element?
    # e.g. 'First Name', 'College', or empty string if static text
    source_column: Optional[str] = Field(
        default=None, 
        description="Excel column name to pull data from"
    )
    # If it's static text (like 'Certificate of Completion'), store it here:
    static_text: Optional[str] = Field(
        default="", 
        description="Static text if not bound to an Excel column"
    )

    # 3. Canvas Positioning & Geometry (Measured in PDF points: 1/72 inch)
    # ge=0 means 'Greater than or Equal to 0' (no negative coordinates allowed!)
    x: float = Field(..., ge=0, description="X coordinate on canvas (from bottom-left or top-left)")
    y: float = Field(..., ge=0, description="Y coordinate on canvas")
    width: float = Field(default=200.0, gt=0, description="Bounding box width")
    height: float = Field(default=40.0, gt=0, description="Bounding box height")

    # 4. Typography (for text elements)
    font_family: str = Field(
        default="Helvetica-Bold", 
        description="Standard PDF font: Helvetica, Helvetica-Bold, Times-Roman, Courier, etc."
    )
    font_size: int = Field(
        default=20, 
        gt=0, 
        le=120, 
        description="Font size in points (between 1 and 120)"
    )
    min_font_size: int = Field(
        default=10, 
        gt=0, 
        description="Minimum font size if auto-shrinking"
    )
    color: str = Field(
        default="#000000", 
        description="Hex color string, e.g. '#000000' or '#1E3A8A'"
    )
    alignment: Literal["left", "center", "right"] = Field(
        default="center", 
        description="Text alignment within its bounding box"
    )
    auto_shrink: bool = Field(
        default=True, 
        description="If True, scales down font size if text is wider than bounding width"
    )

    # 5. QR Code Specific Properties
    qr_size: float = Field(
        default=100.0, 
        gt=0, 
        description="Size in points (width & height) of the QR code"
    )
    # Custom URL pattern (e.g., 'https://internshipleague.com/verify/?id={{cert_id}}')
    qr_url_template: Optional[str] = Field(
        default=None, 
        description="Custom verification URL pattern containing {{cert_id}}"
    )
