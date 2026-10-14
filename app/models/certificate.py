from datetime import datetime
from sqlalchemy import Column, String, Date, DateTime, JSON, ForeignKey
from app.db.database import Base


class Certificate(Base):
    """
    Certificates Table
    Stores generated certificates and their verification status.
    """
    __tablename__ = "certificates"

    # Unique Certificate UUID (e.g., "eb612ee5-41f7-4171-8921-c2afd1e6a769")
    # This ID is printed on the certificate and encoded into the QR code URL.
    id = Column(String(64), primary_key=True, index=True)
    
    # Optional link back to the template used to generate this certificate
    template_id = Column(String(64), ForeignKey("templates.id", ondelete="SET NULL"), nullable=True)
    
    # Core recipient details
    recipient_name = Column(String(255), nullable=False)
    recipient_id = Column(String(100), index=True, nullable=True)      # e.g., Member ID (1934214) or Roll No
    recipient_email = Column(String(255), nullable=True)
    
    # Event metadata
    event_name = Column(String(255), nullable=False)                  # e.g., "Hackathon Series / 11"
    issue_date = Column(Date, nullable=False)                         # e.g., 2026-10-15
    
    # Certificate status: 'ACTIVE', 'REVOKED', or 'EXPIRED'
    # If a certificate was issued by error, you can mark it REVOKED without deleting the record!
    status = Column(String(20), default="ACTIVE", index=True)
    
    # DYNAMIC METADATA (JSON):
    # This is the secret to making this generator work for ANY event!
    # Stores all custom columns from the Excel sheet:
    # e.g. {"College": "Narayana Engineering", "Degree": "B.Tech", "Application No": "ILJULY2026-0253"}
    metadata_json = Column(JSON, nullable=False, default={})
    
    # Timestamp when certificate was generated
    created_at = Column(DateTime, default=datetime.utcnow)
