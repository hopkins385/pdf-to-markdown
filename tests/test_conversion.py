"""Tests for pdf-to-markdown conversion."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pymupdf
import pytest

from pdf_to_markdown.converters import convert_pdf


def make_sample_pdf(path: Path, text: str = "Hello, PDF to Markdown!") -> Path:
    """Create a minimal single-page PDF containing *text* using PyMuPDF."""
    doc = pymupdf.open()
    page = doc.new_page(width=595, height=842)  # A4
    page.insert_text(
        (72, 100),
        text,
        fontsize=14,
    )
    doc.save(str(path))
    doc.close()
    return path


class TestConvertPdf:
    """Tests for the convert_pdf() function."""

    def test_pymupdf4llm_basic(self, tmp_path: Path) -> None:
        """PyMuPDF4LLM converts a native PDF and the expected text is present."""
        expected_text = "Hello from PyMuPDF4LLM"
        pdf_path = make_sample_pdf(tmp_path / "sample.pdf", text=expected_text)

        result = convert_pdf(pdf_path, engine="pymupdf4llm")

        assert isinstance(result, str), "convert_pdf should return a string"
        assert len(result) > 0, "Converted Markdown should not be empty"
        assert expected_text in result, (
            f"Expected text '{expected_text}' not found in output:\n{result}"
        )

    def test_returns_markdown_string(self, tmp_path: Path) -> None:
        """Output is a non-empty string for a valid PDF."""
        pdf_path = make_sample_pdf(tmp_path / "check.pdf", text="Markdown output check")
        result = convert_pdf(pdf_path, engine="pymupdf4llm")
        assert isinstance(result, str)
        assert len(result.strip()) > 0

    def test_file_not_found(self, tmp_path: Path) -> None:
        """FileNotFoundError is raised when the PDF does not exist."""
        with pytest.raises(FileNotFoundError):
            convert_pdf(tmp_path / "nonexistent.pdf")

    def test_auto_engine_native_pdf(self, tmp_path: Path) -> None:
        """Auto engine works on a native PDF without needing Marker."""
        expected_text = "Auto engine test"
        pdf_path = make_sample_pdf(tmp_path / "auto.pdf", text=expected_text)

        result = convert_pdf(pdf_path, engine="auto")

        assert expected_text in result, (
            f"Expected text not found in auto-engine output:\n{result}"
        )

    def test_invalid_engine(self, tmp_path: Path) -> None:
        """ValueError is raised for an unknown engine name."""
        pdf_path = make_sample_pdf(tmp_path / "bad_engine.pdf")
        with pytest.raises(ValueError, match="Unknown engine"):
            convert_pdf(pdf_path, engine="bogus")  # type: ignore[arg-type]

    def test_multiple_sentences(self, tmp_path: Path) -> None:
        """All lines of text appear in the output."""
        lines = ["First sentence.", "Second sentence.", "Third sentence."]
        # PyMuPDF insert_text places text at a single point; use newlines
        text_block = "  ".join(lines)  # single line with spacing
        pdf_path = make_sample_pdf(tmp_path / "multi.pdf", text=text_block)
        result = convert_pdf(pdf_path, engine="pymupdf4llm")
        for line in lines:
            assert line in result, f"Expected '{line}' in output but got:\n{result}"

    def test_extract_images_creates_assets_dir(self, tmp_path: Path) -> None:
        """When --images is requested, assets dir is created (even if no images in PDF)."""
        pdf_path = make_sample_pdf(tmp_path / "img_test.pdf")
        assets_dir = tmp_path / "assets"
        convert_pdf(pdf_path, engine="pymupdf4llm", extract_images=True, assets_dir=assets_dir)
        assert assets_dir.exists(), "assets/ directory should be created when --images is used"
