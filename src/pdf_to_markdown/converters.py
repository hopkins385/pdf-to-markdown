"""PDF conversion backends.

PyMuPDF4LLM is the default engine: fast, lightweight, no ML models needed.
Marker is an optional engine: slower but handles scanned PDFs via OCR (Surya).
Claude is an optional engine: uses Claude's vision API to convert each page.
"""

from __future__ import annotations

import base64
import importlib
import os
import shutil
from pathlib import Path
from typing import Literal

Engine = Literal["pymupdf4llm", "marker", "claude", "auto"]

_MARKER_INSTALL_HINT = (
    'Marker is not installed. Install it with:\n'
    '    pip install "pdf-to-markdown[marker]"\n'
    'or:\n'
    '    pip install marker-pdf'
)

_CLAUDE_INSTALL_HINT = (
    'anthropic is not installed. Install it with:\n'
    '    pip install "pdf-to-markdown[claude]"\n'
    'or:\n'
    '    pip install anthropic'
)

# (input $/1M tokens, output $/1M tokens) — matched by prefix
# Prices from https://platform.claude.com/docs/en/about-claude/pricing
_CLAUDE_MODEL_PRICING: dict[str, tuple[float, float]] = {
    "claude-fable-5": (10.00, 50.00),
    "claude-mythos-5": (10.00, 50.00),
    "claude-opus-4-8": (5.00, 25.00),
    "claude-opus-4-7": (5.00, 25.00),
    "claude-opus-4-6": (5.00, 25.00),
    "claude-opus-4-5": (5.00, 25.00),
    "claude-sonnet-4-6": (3.00, 15.00),
    "claude-sonnet-4-5": (3.00, 15.00),
    "claude-haiku-4-5": (1.00, 5.00),
    "claude-haiku-3-5": (0.80, 4.00),
}

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


def _convert_with_claude(
    pdf_path: Path,
    model: str = "claude-opus-4-8",
) -> str:
    """Convert a PDF by rendering each page as an image and sending it to Claude."""
    try:
        import anthropic  # noqa: PLC0415
    except ImportError as exc:
        raise ImportError(_CLAUDE_INSTALL_HINT) from exc

    import pymupdf  # noqa: PLC0415

    input_price: float | None = None
    output_price: float | None = None
    for prefix, (ip, op) in _CLAUDE_MODEL_PRICING.items():
        if model.startswith(prefix):
            input_price, output_price = ip, op
            break

    client = anthropic.Anthropic()
    pages_md: list[str] = []
    total_input_tokens = 0
    total_output_tokens = 0

    with pymupdf.open(str(pdf_path)) as doc:
        n_pages = doc.page_count
        for i, page in enumerate(doc, start=1):
            import click  # noqa: PLC0415

            click.echo(f"  [claude] page {i}/{n_pages} ...", err=True)
            # Cap scale so neither dimension exceeds the 8000-pixel API limit.
            _MAX_DIM = 7900
            _scale = min(2.0, _MAX_DIM / max(page.rect.width, page.rect.height))
            pix = page.get_pixmap(matrix=pymupdf.Matrix(_scale, _scale))
            png_bytes = pix.tobytes("png")
            b64 = base64.standard_b64encode(png_bytes).decode()

            response = client.messages.create(
                model=model,
                max_tokens=4096,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/png",
                                    "data": b64,
                                },
                            },
                            {
                                "type": "text",
                                "text": (
                                    "Convert this PDF page image to Markdown. "
                                    "Preserve the document structure including headings, "
                                    "lists, tables, and code blocks. "
                                    "Output only the Markdown content with no explanation or preamble."
                                ),
                            },
                        ],
                    }
                ],
            )
            pages_md.append(response.content[0].text)
            total_input_tokens += response.usage.input_tokens
            total_output_tokens += response.usage.output_tokens

    cost_str = ""
    if input_price is not None and output_price is not None:
        cost = (total_input_tokens * input_price + total_output_tokens * output_price) / 1_000_000
        cost_str = f" | estimated cost: ${cost:.4f}"

    import click  # noqa: PLC0415

    click.echo(
        f"  [claude] done — {n_pages} pages | "
        f"{total_input_tokens:,} input tokens | "
        f"{total_output_tokens:,} output tokens"
        f"{cost_str}",
        err=True,
    )

    return "\n\n---\n\n".join(pages_md)


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
    llm_model: str = "claude-opus-4-8",
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
        - ``"claude"``: renders each page as an image and sends it to Claude's vision API.
        - ``"auto"``: use PyMuPDF4LLM; fall back to Marker if text yield is low.
    extract_images:
        When True, extract embedded images to *assets_dir*. Ignored for ``"claude"`` engine.
    assets_dir:
        Directory for extracted images. Defaults to ``<pdf_stem>/assets/``
        relative to the PDF file.
    llm_model:
        Claude model to use when ``engine="claude"``. Defaults to ``"claude-opus-4-8"``.

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

    if engine == "claude":
        return _convert_with_claude(pdf_path, model=llm_model)

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

    raise ValueError(
        f"Unknown engine: {engine!r}. Choose 'pymupdf4llm', 'marker', 'claude', or 'auto'."
    )
