# pdf-to-markdown

Convert PDF files to Markdown with a single command.

Two conversion engines are supported. **PyMuPDF4LLM** is the default. It is fast, has no ML model dependencies, and works well on native PDFs (those with selectable text). **Marker** is an optional engine for scanned or complex PDFs. It uses the Surya OCR model and supports Apple MPS acceleration, but requires a heavier install.

## Why these tools?

| Engine | Speed | Scanned PDFs | Install size |
|---|---|---|---|
| PyMuPDF4LLM | Very fast | No (text only) | Small |
| Marker | Slower | Yes (OCR) | Large (ML models) |

PyMuPDF4LLM is the right default for most use cases. Marker is available as an optional extra when you need OCR.

## Installation

### Core (PyMuPDF4LLM engine only)

```bash
pip install pdf-to-markdown
```

### With Marker support (optional)

```bash
pip install "pdf-to-markdown[marker]"
```

### Development install

```bash
git clone <repo-url>
cd pdf-to-markdown
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

## Usage

### Convert a single PDF

```bash
pdf2md convert document.pdf
```

This writes `document.md` in the same directory.

### Specify an output file

```bash
pdf2md convert document.pdf -o result.md
```

### Use Marker for scanned PDFs

```bash
pdf2md convert scanned.pdf --engine marker
```

Marker must be installed (`pip install "pdf-to-markdown[marker]"`). If it is not installed, the tool prints a helpful hint and exits.

### Auto mode

```bash
pdf2md convert document.pdf --engine auto
```

Auto mode runs PyMuPDF4LLM first. If the text yield is below 100 characters per page on average, it suggests or uses Marker instead.

### Extract images

```bash
pdf2md convert document.pdf --images
```

Images are saved to `assets/` next to the output file. Use `--assets-dir` to override the location.

```bash
pdf2md convert document.pdf --images --assets-dir ./my_images/
```

### Batch convert a directory

```bash
pdf2md convert ./my_pdfs/
```

All `.pdf` files under `./my_pdfs/` are converted in place (each gets a `.md` sibling).

```bash
pdf2md convert ./my_pdfs/ -o ./output_dir/
```

Output files mirror the input directory structure under `./output_dir/`.

### Version

```bash
pdf2md --version
```

## Running tests

```bash
pytest
```

## Project layout

```
pdf-to-markdown/
  src/pdf_to_markdown/
    __init__.py       Public API (convert_pdf)
    cli.py            Click CLI (pdf2md entry point)
    converters.py     PyMuPDF4LLM and Marker backends
  tests/
    test_conversion.py
  pyproject.toml
  README.md
```

## License

MIT
