import os
import json
import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import get_db
from app.models.template import Template
from app.schemas.element import CanvasElement
from app.schemas.template import TemplateResponse

router = APIRouter(
    prefix="/templates",
    tags=["Templates"]  # Groups under "Templates" in Swagger docs!
)


@router.post(
    "",
    response_model=TemplateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Save a new certificate template",
    description="Uploads a background PDF and saves its canvas coordinates layout schema into the database."
)
async def create_template(
    title: str = Form(..., description="Template title, e.g. 'Zap10X Hackathon Series 11'"),
    description: str = Form("", description="Optional template description"),
    page_width: float = Form(842.25, description="Page width in points"),
    page_height: float = Form(595.5, description="Page height in points"),
    layout_schema_json: str = Form(..., description="JSON string of CanvasElement array"),
    base_pdf: UploadFile = File(..., description="Background certificate PDF template"),
    db: Session = Depends(get_db)
):
    """
    Saves the uploaded PDF into storage/templates/ and stores the layout coordinates in the DB.
    """
    # 1. Parse and validate layout schema with Pydantic
    try:
        raw_elements = json.loads(layout_schema_json)
        # Validates each element through Pydantic's CanvasElement
        elements = [CanvasElement(**elem).model_dump() for elem in raw_elements]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid layout_schema_json: {str(e)}"
        )

    # 2. Save the uploaded template PDF into storage/templates/
    template_id = f"tmpl_{uuid.uuid4().hex[:12]}"
    filename = f"{template_id}_{base_pdf.filename}"
    file_path = os.path.join(settings.TEMPLATES_DIR, filename)

    content = await base_pdf.read()
    with open(file_path, "wb") as f_out:
        f_out.write(content)

    # 3. Create database record
    db_template = Template(
        id=template_id,
        title=title,
        description=description,
        page_width=page_width,
        page_height=page_height,
        base_pdf_path=file_path,
        layout_schema=elements
    )
    db.add(db_template)
    db.commit()
    db.refresh(db_template)

    return db_template


@router.get(
    "",
    response_model=List[TemplateResponse],
    summary="List all saved certificate templates",
    description="Returns all reusable certificate templates available in the system."
)
def list_templates(db: Session = Depends(get_db)):
    """
    Fetches all templates ordered by most recently updated.
    """
    return db.query(Template).order_by(Template.updated_at.desc()).all()


@router.get(
    "/{template_id}",
    response_model=TemplateResponse,
    summary="Get single template by ID",
    description="Fetches a specific template design and its element layout schema."
)
def get_template(template_id: str, db: Session = Depends(get_db)):
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template with ID '{template_id}' was not found."
        )
    return template


@router.delete(
    "/{template_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a template by ID"
)
def delete_template(template_id: str, db: Session = Depends(get_db)):
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template with ID '{template_id}' was not found."
        )
    
    # Remove PDF file if it exists on disk
    if os.path.exists(template.base_pdf_path):
        try:
            os.remove(template.base_pdf_path)
        except OSError:
            pass

    db.delete(template)
    db.commit()
    return None
