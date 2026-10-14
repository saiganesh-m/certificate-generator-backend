import json
from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.certificate import Certificate
from app.schemas.element import CanvasElement
from app.schemas.certificate import CertificateVerificationResponse
from app.services.excel_parser import ExcelParserService
from app.services.pdf_engine import PDFEngineService

# APIRouter acts like a mini-FastAPI app for certificate-related endpoints
router = APIRouter(
    prefix="/certificates",
    tags=["Certificates"]  # Groups these routes together in Swagger docs!
)


@router.post(
    "/parse-data",
    summary="Parse participant Excel or CSV file",
    description="Reads an uploaded Excel/CSV file in-memory and returns detected columns and cleaned participant records."
)
async def parse_participant_data(
    file: UploadFile = File(..., description="Excel (.xlsx/.xls) or CSV (.csv) participant file")
):
    """
    Endpoint called when the user drops an Excel file into the React studio.
    Returns column headers for draggable badges and cleaned records for live preview.
    """
    if not (file.filename.endswith(".xlsx") or file.filename.endswith(".xls") or file.filename.endswith(".csv")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format. Please upload an Excel (.xlsx/.xls) or CSV file."
        )

    content = await file.read()
    try:
        columns, records = ExcelParserService.parse_file(content, file.filename)
        return {
            "filename": file.filename,
            "total_records": len(records),
            "columns": columns,
            "records": records
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to parse Excel file: {str(e)}"
        )


@router.post(
    "/generate-batch",
    summary="Batch generate certificates as ZIP archive",
    description="Takes a base PDF template, participant Excel sheet, and canvas layout JSON. Returns a downloadable ZIP bundle.",
    response_class=Response
)
async def generate_batch_certificates(
    template_pdf: UploadFile = File(..., description="Base certificate template PDF"),
    data_file: UploadFile = File(..., description="Excel/CSV participant data file"),
    layout_schema_json: str = Form(..., description="JSON string array of CanvasElement objects"),
    event_name: str = Form("Hackathon Series / 11", description="Event or Course title"),
    issue_date_str: str = Form(str(date.today()), description="Issue date in YYYY-MM-DD format"),
    page_width: float = Form(842.25, description="Page width in points"),
    page_height: float = Form(595.5, description="Page height in points"),
    filename_column: str = Form("Member ID", description="Column to use for PDF filenames"),
    db: Session = Depends(get_db)  # Automatically acquires DB session
):
    """
    The master generation endpoint!
    Generates all certificates in-memory, writes records to the database, and returns a ZIP file.
    """
    # 1. Parse layout schema from JSON
    try:
        raw_elements = json.loads(layout_schema_json)
        elements = [CanvasElement(**elem) for elem in raw_elements]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid layout_schema_json: {str(e)}"
        )

    # 2. Parse participant data
    pdf_bytes = await template_pdf.read()
    data_bytes = await data_file.read()

    try:
        _, records = ExcelParserService.parse_file(data_bytes, data_file.filename)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error reading participant file: {str(e)}"
        )

    if not records:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The participant file contains no valid rows."
        )

    # 3. Parse issue date
    try:
        issue_date_val = date.fromisoformat(issue_date_str)
    except ValueError:
        issue_date_val = date.today()

    # 4. Generate the ZIP bundle and DB records
    try:
        zip_stream, cert_db_records = PDFEngineService.generate_batch_zip(
            base_pdf_bytes=pdf_bytes,
            page_width=page_width,
            page_height=page_height,
            elements=elements,
            records=records,
            event_name=event_name,
            issue_date=issue_date_val,
            filename_column=filename_column
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PDF generation error: {str(e)}"
        )

    # 5. Save all generated certificates into SQLite / MySQL database
    try:
        for cert_dict in cert_db_records:
            cert_obj = Certificate(
                id=cert_dict["id"],
                recipient_name=cert_dict["recipient_name"],
                recipient_id=cert_dict["recipient_id"],
                event_name=cert_dict["event_name"],
                issue_date=cert_dict["issue_date"],
                status="ACTIVE",
                metadata_json=cert_dict["metadata_json"]
            )
            db.merge(cert_obj)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save verification records to database: {str(e)}"
        )

    # 6. Stream the ZIP file back to the user
    return Response(
        content=zip_stream.getvalue(),
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename=certificates_{event_name.replace(' ', '_')}.zip"
        }
    )


@router.get(
    "/verify/{certificate_id}",
    response_model=CertificateVerificationResponse,
    summary="Verify certificate authenticity by UUID",
    description="Queried when someone scans a QR code. Returns verification details, recipient info, and dynamic metadata."
)
def verify_certificate(
    certificate_id: str,
    db: Session = Depends(get_db)
):
    """
    Public verification endpoint queried by the verification page.
    """
    cert = db.query(Certificate).filter(Certificate.id == certificate_id).first()
    if not cert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Certificate with ID '{certificate_id}' was not found in the official registry."
        )

    return CertificateVerificationResponse(
        certificate_id=cert.id,
        recipient_name=cert.recipient_name,
        recipient_id=cert.recipient_id,
        event_name=cert.event_name,
        issue_date=cert.issue_date,
        status=cert.status,
        metadata=cert.metadata_json or {}
    )
