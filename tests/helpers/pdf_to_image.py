from __future__ import annotations

from pathlib import Path


class PdfRenderError(RuntimeError):
    """Raised when a PDF page cannot be rendered to an image."""


def get_pdf_page_count(pdf_path: Path) -> int:
    """Return the total number of pages in a PDF."""
    try:
        import pymupdf
    except ImportError as exc:
        raise PdfRenderError("pymupdf is required to inspect PDF pages; pip install pymupdf") from exc

    document = pymupdf.open(pdf_path)
    try:
        return int(document.page_count)
    finally:
        document.close()


def render_pdf_page_png(pdf_path: Path, page_index: int = 0, dpi: int = 150) -> bytes:
    """Render a single PDF page to PNG bytes using PyMuPDF (fitz)."""
    try:
        import pymupdf
    except ImportError as exc:
        raise PdfRenderError("pymupdf is required to render PDF pages; pip install pymupdf") from exc

    document = pymupdf.open(pdf_path)
    try:
        if page_index >= document.page_count:
            raise PdfRenderError(f"PDF has {document.page_count} page(s); requested page index {page_index}")
        page = document.load_page(page_index)
        zoom = dpi / 72
        matrix = pymupdf.Matrix(zoom, zoom)
        pixmap = page.get_pixmap(matrix=matrix)
        return pixmap.tobytes("png")
    finally:
        document.close()
