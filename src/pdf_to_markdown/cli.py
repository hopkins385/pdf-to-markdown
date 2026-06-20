"""CLI entry point for pdf-to-markdown."""

from __future__ import annotations

import sys
from pathlib import Path

import click
from dotenv import load_dotenv

from pdf_to_markdown.converters import Engine, convert_pdf

load_dotenv()


def _resolve_output(input_path: Path, output: str | None) -> Path:
    if output:
        return Path(output)
    return input_path.with_suffix(".md")


@click.group()
@click.version_option(package_name="pdf-to-markdown")
def main() -> None:
    """pdf2md: Convert PDF files to Markdown."""


@main.command("convert")
@click.argument("input", type=click.Path(exists=True, path_type=Path))
@click.option(
    "-o",
    "--output",
    "output",
    default=None,
    help="Output Markdown file (or directory when INPUT is a directory). "
    "Defaults to <input>.md",
)
@click.option(
    "--engine",
    type=click.Choice(["pymupdf4llm", "marker", "claude", "auto"], case_sensitive=False),
    default="pymupdf4llm",
    show_default=True,
    help=(
        "Conversion engine. "
        "'pymupdf4llm' is fast and works on native PDFs. "
        "'marker' handles scanned PDFs via OCR (requires marker-pdf). "
        "'claude' renders each page as an image and sends it to Claude vision API (requires anthropic). "
        "'auto' tries pymupdf4llm first and suggests Marker if text yield is low."
    ),
)
@click.option(
    "--model",
    "llm_model",
    default="claude-opus-4-8",
    show_default=True,
    help="Claude model to use when --engine=claude.",
)
@click.option(
    "--images",
    "extract_images",
    is_flag=True,
    default=False,
    help="Extract embedded images to an assets/ folder next to the output file.",
)
@click.option(
    "--assets-dir",
    "assets_dir",
    default=None,
    help="Directory for extracted images (overrides default assets/ location).",
)
def convert_command(
    input: Path,
    output: str | None,
    engine: Engine,
    llm_model: str,
    extract_images: bool,
    assets_dir: str | None,
) -> None:
    """Convert INPUT (a PDF file or directory of PDFs) to Markdown.

    Examples:

    \b
        pdf2md convert document.pdf
        pdf2md convert document.pdf -o result.md
        pdf2md convert document.pdf --engine marker
        pdf2md convert document.pdf --engine claude
        pdf2md convert document.pdf --engine claude --model claude-sonnet-4-6
        pdf2md convert document.pdf --engine auto
        pdf2md convert document.pdf --images
        pdf2md convert ./my_pdfs/ -o ./output_dir/
    """
    if input.is_dir():
        _batch_convert(input, output, engine, llm_model, extract_images, assets_dir)
    else:
        _single_convert(input, output, engine, llm_model, extract_images, assets_dir)


def _single_convert(
    pdf_path: Path,
    output: str | None,
    engine: Engine,
    llm_model: str,
    extract_images: bool,
    assets_dir: str | None,
) -> None:
    """Convert a single PDF file."""
    if not pdf_path.suffix.lower() == ".pdf":
        click.echo(f"Warning: {pdf_path} does not have a .pdf extension.", err=True)

    out_path = _resolve_output(pdf_path, output)

    _assets_dir: Path | None = None
    if extract_images:
        if assets_dir:
            _assets_dir = Path(assets_dir)
        else:
            _assets_dir = out_path.parent / "assets"

    if engine == "claude":
        import pymupdf  # noqa: PLC0415

        with pymupdf.open(str(pdf_path)) as _doc:
            n_pages = _doc.page_count
        if n_pages > 50:
            click.echo(
                f"This PDF has {n_pages} pages. Each page makes a separate API call.",
                err=True,
            )
            click.confirm("Continue?", default=False, abort=True)

    click.echo(f"Converting {pdf_path} -> {out_path} [engine={engine}]", err=True)

    try:
        md_text = convert_pdf(
            pdf_path,
            engine=engine,
            extract_images=extract_images,
            assets_dir=_assets_dir,
            llm_model=llm_model,
        )
    except ImportError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)
    except FileNotFoundError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(md_text, encoding="utf-8")
    click.echo(f"Written: {out_path}", err=True)

    # Print markdown to stdout so callers can pipe it
    click.echo(md_text)


def _batch_convert(
    input_dir: Path,
    output: str | None,
    engine: Engine,
    llm_model: str,
    extract_images: bool,
    assets_dir: str | None,
) -> None:
    """Convert all PDF files in a directory."""
    pdf_files = sorted(input_dir.rglob("*.pdf"))
    if not pdf_files:
        click.echo(f"No PDF files found in {input_dir}", err=True)
        sys.exit(1)

    out_dir = Path(output) if output else input_dir
    errors: list[str] = []

    for pdf_path in pdf_files:
        rel = pdf_path.relative_to(input_dir)
        out_path = out_dir / rel.with_suffix(".md")

        _assets_dir: Path | None = None
        if extract_images:
            if assets_dir:
                _assets_dir = Path(assets_dir)
            else:
                _assets_dir = out_path.parent / "assets"

        click.echo(f"Converting {pdf_path} -> {out_path} [engine={engine}]", err=True)

        try:
            md_text = convert_pdf(
                pdf_path,
                engine=engine,
                extract_images=extract_images,
                assets_dir=_assets_dir,
                llm_model=llm_model,
            )
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(md_text, encoding="utf-8")
            click.echo(f"  Written: {out_path}", err=True)
        except ImportError as exc:
            click.echo(f"  Error (import): {exc}", err=True)
            errors.append(str(pdf_path))
        except Exception as exc:  # noqa: BLE001
            click.echo(f"  Error converting {pdf_path}: {exc}", err=True)
            errors.append(str(pdf_path))

    total = len(pdf_files)
    failed = len(errors)
    click.echo(
        f"\nDone: {total - failed}/{total} files converted successfully.",
        err=True,
    )
    if errors:
        click.echo(f"Failed files:\n" + "\n".join(f"  {e}" for e in errors), err=True)
        sys.exit(1)
