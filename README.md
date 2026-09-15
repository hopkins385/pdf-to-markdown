# pdf-to-markdown

Convert PDF files to Markdown from the command line.

Three engines: **PyMuPDF4LLM** (default, fast, native text PDFs), **Marker** (OCR for scanned PDFs), and **Claude** (vision API, best quality on complex layouts). See [docs/ENGINES.md](docs/ENGINES.md) for a full comparison and Claude pricing.

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

MIT, see [LICENSE](LICENSE).
