import barcode
from barcode.writer import ImageWriter
import qrcode
import io
import os
from typing import Optional

class BarcodeService:
    @staticmethod
    def generate_ean13(code: str) -> io.BytesIO:
        """
        Genera un código de barras EAN13 en formato PNG.
        """
        EAN = barcode.get_barcode_class('ean13')
        # EAN13 requiere 12 dígitos (el 13 es el checksum)
        # Si el código es más corto, lo rellenamos con ceros
        if len(code) < 12:
            code = code.zfill(12)
        elif len(code) > 12:
            code = code[:12]
            
        ean = EAN(code, writer=ImageWriter())
        buffer = io.BytesIO()
        ean.write(buffer)
        buffer.seek(0)
        return buffer

    @staticmethod
    def generate_code128(code: str) -> io.BytesIO:
        """
        Genera un código de barras Code128 en formato PNG.
        """
        CODE128 = barcode.get_barcode_class('code128')
        c128 = CODE128(code, writer=ImageWriter())
        buffer = io.BytesIO()
        c128.write(buffer)
        buffer.seek(0)
        return buffer

    @staticmethod
    def generate_qr(data: str) -> io.BytesIO:
        """
        Genera un código QR en formato PNG.
        """
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        return buffer

barcode_service = BarcodeService()
