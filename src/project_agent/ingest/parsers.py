from pathlib import Path

import fitz
from docx import Document as DocxDocument
from openpyxl import load_workbook


def parse_pdf(path: Path) -> str:
    parts: list[str] = []
    with fitz.open(path) as doc:
        for i, page in enumerate(doc, start=1):
            text = page.get_text().strip()
            if text:
                parts.append(f"## Page {i}\n\n{text}")
    return "\n\n".join(parts) if parts else ""


def parse_docx(path: Path) -> str:
    doc = DocxDocument(path)
    parts: list[str] = []
    for para in doc.paragraphs:
        t = para.text.strip()
        if t:
            style = para.style.name if para.style else ""
            if "Heading" in style:
                level = style.replace("Heading", "").strip() or "2"
                try:
                    n = min(int(level), 6)
                except ValueError:
                    n = 2
                parts.append(f"{'#' * n} {t}")
            else:
                parts.append(t)
    return "\n\n".join(parts)


def parse_xlsx(path: Path) -> str:
    wb = load_workbook(path, read_only=True, data_only=True)
    parts: list[str] = []
    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
        parts.append(f"## Sheet: {sheet_name}\n")
        rows: list[str] = []
        for row in ws.iter_rows(values_only=True):
            cells = [str(c) if c is not None else "" for c in row]
            if any(cells):
                rows.append("| " + " | ".join(cells) + " |")
        if rows and len(rows) > 1:
            header = rows[0]
            sep = "| " + " | ".join(["---"] * (rows[0].count("|") + 1)) + " |"
            parts.append("\n".join([header, sep, *rows[1:]]))
        elif rows:
            parts.append("\n".join(rows))
    wb.close()
    return "\n\n".join(parts)


def parse_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def parse_file(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return parse_pdf(path)
    if suffix in (".docx",):
        return parse_docx(path)
    if suffix in (".xlsx", ".xlsm"):
        return parse_xlsx(path)
    if suffix in (".txt", ".md", ".markdown", ".csv"):
        return parse_text(path)
    raise ValueError(f"Unsupported file type: {suffix}")
