import io
import qrcode
from PIL import Image


class QRService:
    """
    Service responsible for generating high-resolution QR codes in-memory.
    """

    @staticmethod
    def generate_qr_image(data: str, box_size: int = 10, border: int = 0) -> Image.Image:
        """
        Generates a PIL Image of a QR code.
        - error_correction=ERROR_CORRECT_M: Medium error correction (retains scannability even with slight damage).
        - border=0: No extra white margin around the QR code, so it fits neatly in certificate boxes.
        """
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=box_size,
            border=border,
        )
        qr.add_data(data)
        qr.make(fit=True)
        return qr.make_image(fill_color="black", back_color="white").convert("RGB")

    @staticmethod
    def generate_qr_bytes(data: str) -> io.BytesIO:
        """
        Generates a QR code and returns it as an in-memory PNG BytesIO stream.
        This stream can be passed directly to ReportLab's ImageReader without writing to disk!
        """
        img = QRService.generate_qr_image(data)
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)  # Rewind the stream to the beginning for reading
        return buffer
