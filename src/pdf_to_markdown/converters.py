"""PDF conversion backends.

PyMuPDF4LLM is the default engine: fast, lightweight, no ML models needed.
Marker is an optional engine: slower but handles scanned PDFs via OCR (Surya).
"""

from __future__ import annotations

import importlib
import os
import shutil
from pathlib import Path
from typing import Literal

Engine = Literal["pymupdf4llm", "marker", "auto"]

_MARKER_INSTALL_HINT = (
    'Marker is not installed. Install it with:\n'
    '    pip install "pdf-to-markdown[marker]"\n'
    'or:\n'
    '    pip install marker-pdf'
)

# Pages with fewer than this many characters are treated as "suspiciously empty"
# when using --engine auto.
_CHARS_PER_PAGE_THRESHOLD = 100


def _convert_with_pymupdf4llm(
    pdf_path: Path,
    extract_images: bool = False,
    assets_dir: Path | None = None,
) -> str:
    """Convert a PDF using PyMuPDF4LLM."""
    import pymupdf4llm  # noqa: PLC0415

    kwargs: dict = {}
    if extract_images and assets_dir is not None:
        assets_dir.mkdir(parents=True, exist_ok=True)
        kwargs["write_images"] = True
        kwargs["image_path"] = str(assets_dir)

    md_text: str = pymupdf4llm.to_markdown(str(pdf_path), **kwargs)
    return md_text


def _convert_with_marker(
    pdf_path: Path,
    extract_images: bool = False,
    assets_dir: Path | None = None,
) -> str:
    """Convert a PDF using Marker (supports scanned PDFs via OCR)."""
    try:
        from marker.converters.pdf import PdfConverter  # noqa: PLC0415
        from marker.models import create_model_dict  # noqa: PLC0415
        from marker.output import text_from_rendered  # noqa: PLC0415
    except ImportError as exc:
        raise ImportError(_MARKER_INSTALL_HINT) from exc

    converter = PdfConverter(artifact_dict=create_model_dict())
    rendered = converter(str(pdf_path))
    md_text, _, images = text_from_rendered(rendered)

    if extract_images and assets_dir is not None and images:
        assets_dir.mkdir(parents=True, exist_ok=True)
        for img_name, img in images.items():
            img_path = assets_dir / img_name
            img.save(str(img_path))

    return md_text


def _page_count(pdf_path: Path) -> int:
    """Return the number of pages in a PDF."""
    import pymupdf  # noqa: PLC0415

    with pymupdf.open(str(pdf_path)) as doc:
        return doc.page_count


def convert_pdf(
    pdf_path: Path | str,
    engine: Engine = "pymupdf4llm",
    extract_images: bool = False,
    assets_dir: Path | str | None = None,
) -> str:
    """Convert a PDF file to Markdown text.

    Parameters
    ----------
    pdf_path:
        Path to the source PDF file.
    engine:
        Which conversion backend to use.
        - ``"pymupdf4llm"`` (default): fast, no ML models, best for native PDFs.
        - ``"marker"``: slower, handles scanned/complex PDFs via OCR.
        - ``"auto"``: use PyMuPDF4LLM; fall back to Marker if text yield is low.
    extract_images:
        When True, extract embedded images to *assets_dir*.
    assets_dir:
        Directory for extracted images. Defaults to ``<pdf_stem>/assets/``
        relative to the PDF file.

    Returns
    -------
    str
        Markdown text.
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.is_file():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    _assets_dir: Path | None = None
    if extract_images:
        if assets_dir is not None:
            _assets_dir = Path(assets_dir)
        else:
            _assets_dir = pdf_path.parent / "assets"

    if engine == "pymupdf4llm":
        return _convert_with_pymupdf4llm(pdf_path, extract_images, _assets_dir)

    if engine == "marker":
        return _convert_with_marker(pdf_path, extract_images, _assets_dir)

    if engine == "auto":
        md_text = _convert_with_pymupdf4llm(pdf_path, extract_images, _assets_dir)
        pages = _page_count(pdf_path)
        chars_per_page = len(md_text.strip()) / max(pages, 1)
        if chars_per_page < _CHARS_PER_PAGE_THRESHOLD:
            marker_available = importlib.util.find_spec("marker") is not None
            if marker_available:
                import click  # noqa: PLC0415

                click.echo(
                    f"[auto] Text yield is low ({chars_per_page:.0f} chars/page). "
                    "Retrying with Marker ...",
                    err=True,
                )
                md_text = _convert_with_marker(pdf_path, extract_images, _assets_dir)
            else:
                import click  # noqa: PLC0415

                click.echo(
                    f"[auto] Text yield is low ({chars_per_page:.0f} chars/page). "
                    "Consider installing Marker for better OCR results:\n"
                    f"    {_MARKER_INSTALL_HINT}",
                    err=True,
                )
        return md_text

    raise ValueError(f"Unknown engine: {engine!r}. Choose 'pymupdf4llm', 'marker', or 'auto'.")
