from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def simple_pdf(path: str | Path, title: str, rows: list[tuple[str, str]]) -> Path:
    output = Path(path)
    pdf = canvas.Canvas(str(output), pagesize=letter)
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(40, 740, title)
    pdf.setFont("Helvetica", 10)
    y = 700
    for left, right in rows:
        pdf.drawString(40, y, str(left))
        pdf.drawRightString(560, y, str(right))
        y -= 18
        if y < 60:
            pdf.showPage()
            y = 740
    pdf.save()
    return output
