# pdf-to-markdown

Convert PDF files to Markdown with a single command.

Three conversion engines are supported. **PyMuPDF4LLM** is the default: fast, no ML dependencies, works well on native PDFs with selectable text. **Marker** is an optional engine for scanned or complex PDFs, using the Surya OCR model. **Claude** is an optional engine that renders each page as an image and sends it to Claude's vision API, which gives the best results on complex layouts, mixed content, and low-quality scans.

## Why these engines?

| Engine      | Speed          | Scanned PDFs   | Complex layouts | Install size      |
| ----------- | -------------- | -------------- | --------------- | ----------------- |
| PyMuPDF4LLM | Very fast      | No (text only) | Limited         | Small             |
| Marker      | Slower         | Yes (OCR)      | Good            | Large (ML models) |
| Claude      | Depends on API | Yes            | Best            | Small (API call)  |

PyMuPDF4LLM is the right default for most use cases. Marker is available when you need local OCR. Claude is the best choice for high-fidelity conversion when quality matters more than cost.

## Installation

### Core (PyMuPDF4LLM engine only)

```bash
pip install pdf-to-markdown
```

### With Marker support

```bash
pip install "pdf-to-markdown[marker]"
```

### With Claude support

```bash
pip install "pdf-to-markdown[claude]"
```

Requires an `ANTHROPIC_API_KEY` environment variable (or a `.env` file in the working directory, see `.env.example`).

### Development install

```bash
git clone https://github.com/hopkins385/pdf-to-markdown.git
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

```bash
source .venv/bin/activate && pdf2md convert "path/to/the/file.pdf"
```

Writes `document.md` in the same directory.

### Specify an output file

```bash
pdf2md convert document.pdf -o result.md
```

### Use Marker for scanned PDFs

```bash
pdf2md convert scanned.pdf --engine marker
```

Marker must be installed (`pip install "pdf-to-markdown[marker]"`). If it is not installed, the tool prints a hint and exits.

### Use Claude for high-fidelity conversion

```bash
pdf2md convert document.pdf --engine claude
```

Each page is rendered to a PNG and sent to Claude's vision API. The default model is `claude-opus-4-8`. Progress and a cost summary are printed to stderr after conversion:

```
  [claude] page 1/12 ...
  [claude] page 2/12 ...
  ...
  [claude] done — 12 pages | 84,231 input tokens | 12,450 output tokens | estimated cost: $0.7323
```

To use a different model:

```bash
pdf2md convert document.pdf --engine claude --model claude-haiku-4-5-20251001
```

PDFs with more than 50 pages prompt for confirmation before starting, since each page is a separate API call.

#### Claude model pricing

| Model             | Input         | Output        |
| ----------------- | ------------- | ------------- |
| claude-fable-5    | $10.00 / MTok | $50.00 / MTok |
| claude-mythos-5   | $10.00 / MTok | $50.00 / MTok |
| claude-opus-4-8   | $5.00 / MTok  | $25.00 / MTok |
| claude-opus-4-7   | $5.00 / MTok  | $25.00 / MTok |
| claude-opus-4-6   | $5.00 / MTok  | $25.00 / MTok |
| claude-opus-4-5   | $5.00 / MTok  | $25.00 / MTok |
| claude-sonnet-4-6 | $3.00 / MTok  | $15.00 / MTok |
| claude-sonnet-4-5 | $3.00 / MTok  | $15.00 / MTok |
| claude-haiku-4-5  | $1.00 / MTok  | $5.00 / MTok  |
| claude-haiku-3-5  | $0.80 / MTok  | $4.00 / MTok  |

Source: [Anthropic pricing](https://platform.claude.com/docs/en/about-claude/pricing).

### Auto mode

```bash
pdf2md convert document.pdf --engine auto
```

Runs PyMuPDF4LLM first. If the text yield is below 100 characters per page on average, it suggests or uses Marker instead.

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
    converters.py     PyMuPDF4LLM, Marker, and Claude backends
  tests/
    test_conversion.py
  pyproject.toml
  README.md
```

## License

MIT, see [LICENSE](LICENSE).
