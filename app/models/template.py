from datetime import datetime
from sqlalchemy import Column, String, Float, Text, DateTime, JSON
from app.db.database import Base


class Template(Base):
    """
    Templates Table
    Stores reusable certificate designs, dimensions, and the coordinate layout schema.
    """
    __tablename__ = "templates"

    # Unique identifier, e.g., "tmpl_zap10x_s11" or UUID
    id = Column(String(64), primary_key=True, index=True)
    
    # Human-readable title, e.g., "Zap10X Hackathon Series 11"
    title = Column(String(255), nullable=False)
    
    # Optional description or notes
    description = Column(Text, nullable=True)
    
    # Canvas dimensions in PDF points (A4 Landscape default: 842.25 x 595.5)
    page_width = Column(Float, nullable=False, default=842.25)
    page_height = Column(Float, nullable=False, default=595.5)
    
    # Path to the base PDF template on disk (e.g. storage/templates/template.pdf)
    base_pdf_path = Column(String(512), nullable=False)
    
    # The JSON Layout Schema:
    # Stores the array of all elements: text boxes, fonts, sizes, colors, and coordinates!
    # SQLAlchemy handles Python list/dict <-> JSON serialization automatically.
    layout_schema = Column(JSON, nullable=False)
    
    # Audit Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
