from pathlib import Path

from openpyxl import Workbook


def export_rows(path: str | Path, headers: list[str], rows: list[list[object]]) -> Path:
    output = Path(path)
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Shoro POS"
    sheet.append(headers)
    for row in rows:
        sheet.append(row)
    workbook.save(output)
    return output
