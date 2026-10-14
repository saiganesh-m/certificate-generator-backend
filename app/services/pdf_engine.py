import io
import uuid
import zipfile
from datetime import date
from typing import List, Dict, Any, Tuple, Optional
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from pypdf import PdfReader, PdfWriter
from app.core.config import settings
from app.schemas.element import CanvasElement
from app.services.qr_service import QRService


class PDFEngineService:
    """
    Core vector PDF generation engine.
    Overlays dynamic text and QR codes onto any base PDF certificate template.
    """

    @staticmethod
    def hex_to_rgb(hex_str: str) -> Tuple[float, float, float]:
        """
        Converts a web hex color (e.g., '#1E3A8A' or '000000') into ReportLab RGB (0.0 to 1.0).
        """
        hex_str = hex_str.lstrip("#")
        if len(hex_str) != 6:
            return 0.0, 0.0, 0.0  # Default to black if invalid
        r = int(hex_str[0:2], 16) / 255.0
        g = int(hex_str[2:4], 16) / 255.0
        b = int(hex_str[4:6], 16) / 255.0
        return r, g, b

    @classmethod
    def get_fitted_font_size(
        cls, 
        c: canvas.Canvas, 
        text: str, 
        font_family: str, 
        start_size: int, 
        min_size: int, 
        max_width: float
    ) -> int:
        """
        Dynamically shrinks font size until text fits within max_width points.
        """
        size = start_size
        while size > min_size and c.stringWidth(text, font_family, size) > max_width:
            size -= 1
        return size

    @classmethod
    def generate_overlay(
        cls,
        page_width: float,
        page_height: float,
        elements: List[CanvasElement],
        record_data: Dict[str, Any],
        cert_id: str
    ) -> io.BytesIO:
        """
        Creates an in-memory PDF overlay containing only the dynamic text and QR code.
        """
        packet = io.BytesIO()
        c = canvas.Canvas(packet, pagesize=(page_width, page_height))

        for elem in elements:
            if elem.type == "text":
                # Determine text value: from Excel column or static text
                text_value = ""
                if elem.source_column and elem.source_column in record_data:
                    text_value = str(record_data[elem.source_column]).strip()
                elif elem.static_text:
                    text_value = elem.static_text.strip()

                if not text_value:
                    continue

                # Set color
                r, g, b = cls.hex_to_rgb(elem.color)
                c.setFillColorRGB(r, g, b)

                # Calculate font size (with auto-shrink if enabled)
                font_size = elem.font_size
                if elem.auto_shrink and elem.width > 0:
                    font_size = cls.get_fitted_font_size(
                        c, text_value, elem.font_family, elem.font_size, elem.min_font_size, elem.width
                    )

                c.setFont(elem.font_family, font_size)

                # Draw text according to alignment
                if elem.alignment == "center":
                    c.drawCentredString(elem.x, elem.y, text_value)
                elif elem.alignment == "right":
                    c.drawRightString(elem.x + elem.width, elem.y, text_value)
                else:  # left
                    c.drawString(elem.x, elem.y, text_value)

            elif elem.type == "qr_code":
                # Construct verification URL
                if elem.qr_url_template and "{{cert_id}}" in elem.qr_url_template:
                    qr_url = elem.qr_url_template.replace("{{cert_id}}", cert_id)
                else:
                    qr_url = f"{settings.VERIFICATION_BASE_URL}{cert_id}"

                # Generate in-memory QR code PNG stream
                qr_stream = QRService.generate_qr_bytes(qr_url)
                
                # Draw QR code onto canvas
                c.drawImage(
                    ImageReader(qr_stream),
                    elem.x,
                    elem.y,
                    width=elem.qr_size,
                    height=elem.qr_size
                )

        c.save()
        packet.seek(0)
        return packet

    @classmethod
    def generate_single_certificate(
        cls,
        base_pdf_bytes: bytes,
        page_width: float,
        page_height: float,
        elements: List[CanvasElement],
        record_data: Dict[str, Any],
        cert_id: str
    ) -> io.BytesIO:
        """
        Merges the dynamic overlay onto page 1 of the base PDF template.
        Returns the final certificate as an in-memory BytesIO PDF.
        """
        overlay_stream = cls.generate_overlay(page_width, page_height, elements, record_data, cert_id)
        overlay_reader = PdfReader(overlay_stream)
        base_reader = PdfReader(io.BytesIO(base_pdf_bytes))

        # Merge overlay with template page 1
        page = base_reader.pages[0]
        page.merge_page(overlay_reader.pages[0])

        writer = PdfWriter()
        writer.add_page(page)

        output_stream = io.BytesIO()
        writer.write(output_stream)
        output_stream.seek(0)
        return output_stream

    @classmethod
    def generate_batch_zip(
        cls,
        base_pdf_bytes: bytes,
        page_width: float,
        page_height: float,
        elements: List[CanvasElement],
        records: List[Dict[str, Any]],
        event_name: str,
        issue_date: date,
        filename_column: Optional[str] = "Member ID"
    ) -> Tuple[io.BytesIO, List[Dict[str, Any]]]:
        """
        Generates certificates for all participants, bundles them into an in-memory ZIP archive,
        and returns:
        1. zip_stream: in-memory ZIP file ready for browser download
        2. cert_db_records: list of certificate dictionaries to insert into the database
        """
        zip_buffer = io.BytesIO()
        cert_db_records: List[Dict[str, Any]] = []

        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for index, row in enumerate(records):
                cert_id = str(uuid.uuid4())

                # Generate single PDF in memory
                pdf_stream = cls.generate_single_certificate(
                    base_pdf_bytes=base_pdf_bytes,
                    page_width=page_width,
                    page_height=page_height,
                    elements=elements,
                    record_data=row,
                    cert_id=cert_id
                )

                # Determine clean filename (e.g. "1934214.pdf" or "Lakshmi_Somisetty.pdf")
                file_stem = ""
                if filename_column and filename_column in row and row[filename_column]:
                    file_stem = str(row[filename_column]).strip()
                elif "Full Name" in row and row["Full Name"]:
                    file_stem = str(row["Full Name"]).strip().replace(" ", "_")
                else:
                    file_stem = f"certificate_{index + 1}"

                # Sanitize filename
                clean_name = "".join(c for c in file_stem if c.isalnum() or c in ("-", "_")).strip()
                filename = f"{clean_name}.pdf"

                # Add PDF directly into the in-memory ZIP
                zip_file.writestr(filename, pdf_stream.getvalue())

                # Prepare certificate record for database insertion
                recipient_name = row.get("Full Name") or row.get("Name") or f"Participant {index + 1}"
                recipient_id = str(row.get("Member ID") or row.get("Application No") or "")

                cert_db_records.append({
                    "id": cert_id,
                    "recipient_name": recipient_name,
                    "recipient_id": recipient_id,
                    "event_name": event_name,
                    "issue_date": issue_date,
                    "status": "ACTIVE",
                    "metadata_json": row  # Stores all other columns (College, Degree, City, etc.)
                })

        zip_buffer.seek(0)
        return zip_buffer, cert_db_records
