# pdf-to-markdown

Convert PDF files to Markdown from the command line.

## Engines

| Engine      | Flag                  | Speed          | Scanned PDFs   | Complex layouts | Install size      |
| ----------- | --------------------- | -------------- | -------------- | ---------------- | ----------------- |
| PyMuPDF4LLM | `--engine pymupdf4llm` (default) | Very fast      | No (text only) | Limited          | Small             |
| Marker      | `--engine marker`     | Slower         | Yes (OCR)      | Good              | Large (ML models) |
| Claude      | `--engine claude`     | Depends on API | Yes            | Best              | Small (API call)  |

See [docs/ENGINES.md](docs/ENGINES.md) for auto-mode behavior and Claude pricing, and [docs/RESEARCH.md](docs/RESEARCH.md) for the research behind these choices.

## Installation

Not yet published to PyPI. Install from source with [uv](https://docs.astral.sh/uv/):

```bash
git clone https://github.com/hopkins385/pdf-to-markdown.git
cd pdf-to-markdown
uv venv
source .venv/bin/activate
uv pip install -e .
```

Optional extras: `uv pip install -e ".[marker]"` for OCR, `uv pip install -e ".[claude]"` for the Claude engine (requires `ANTHROPIC_API_KEY`, see `.env.example`).

## Usage

```bash
pdf2md convert document.pdf
pdf2md convert document.pdf -o result.md
pdf2md convert document.pdf --engine marker
pdf2md convert document.pdf --engine claude
pdf2md convert document.pdf --images
pdf2md convert ./my_pdfs/ -o ./output_dir/
```

Run `pdf2md convert --help` for all options, or see [docs/ENGINES.md](docs/ENGINES.md) for engine-specific details.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

This repo's own code is MIT, see [LICENSE](LICENSE).

The default engine depends on `PyMuPDF` / `pymupdf4llm`, which are dual-licensed under **AGPL-3.0 or a commercial Artifex license**. They are not MIT. If you distribute this tool or run it as a network service, review the AGPL terms or obtain a commercial PyMuPDF license. Check the `marker` extra's license separately if you enable it.
