# PDF to Markdown: Tool Research (June 2026)

Research into the best open-source options for converting PDF to Markdown.
This informed the design of this repo: PyMuPDF4LLM as the default engine, Marker as an optional extra.

## Summary

| Tool | Strengths | Weaknesses | Best for |
|------|-----------|------------|----------|
| **Marker** | Highest accuracy, OCR via Surya, Apple MPS/GPU/CPU, optional `--use_llm` for near-perfect output, also handles DOCX/PPTX/EPUB | Heavy install, more licensing restrictions | Safest single default, scanned or messy PDFs |
| **PyMuPDF4LLM** | Fastest, pip install and go, no ML models or GPU, detects headers, paragraphs, tables, images | No OCR, weak on complex tables, PDF only | Native PDFs with selectable text |
| **Docling** (IBM) | Best semantic structure (DoclingDocument), strong table extraction via TableFormer, 88% F1 in one comparison | Slow on CPU (~2 min per 100 pages), install can be painful | Production RAG pipelines, LlamaIndex/LangChain |
| **MinerU** | Complete extraction of tables, formulas, images; OCR for 84 languages; LaTeX-friendly | Complex deployment | Academic papers, CJK documents |
| **MarkItDown** (Microsoft) | Very fast (12 s per 100 pages), many input formats | Lower accuracy (82% F1), weaker tables | Quick bulk conversion where fidelity matters less |
| **OpenDataLoader PDF** | Claims top benchmark scores (0.907 overall, 0.928 tables), 100+ pages/s | Newer, less battle-tested | High-throughput batch parsing |

## Benchmark notes

- Marker benchmarks favorably against cloud services (Llamaparse, Mathpix) and other open-source tools. Its table benchmark uses the FinTabNet dataset. The `--use_llm` mode beats both Marker alone and Gemini Flash alone on table accuracy.
- Docling vs MarkItDown: Docling wins on accuracy (88% vs 82% F1) and table extraction. MarkItDown wins on speed by roughly 10x on CPU.
- Marker projected throughput: 122 pages per second on an H100 across 22 processes.
- Shared weakness across all tools: multi-level heading and section order recognition is unreliable. Manual cleanup may be needed.

## Recommended workflow (adopted by this repo)

1. For native PDFs with selectable text, use PyMuPDF4LLM first. It is fast, light, and often good enough.
2. If output quality is poor or the PDF is scanned, switch to Marker.
3. For structured output in a RAG pipeline, consider Docling instead.

This repo implements steps 1 and 2: the default engine is PyMuPDF4LLM, `--engine marker` opts into Marker, and `--engine auto` falls back to Marker when extracted text averages under 100 chars per page.

## Sources

- [Best Open-Source PDF-to-Markdown Tools in 2026 (themenonlab)](https://themenonlab.blog/blog/best-open-source-pdf-to-markdown-tools-2026)
- [Marker on GitHub](https://github.com/datalab-to/marker)
- [Best Open Source PDF to Markdown Tools 2026 (Jimmy Song)](https://jimmysong.io/blog/pdf-to-markdown-open-source-deep-dive/)
- [Evaluating Document Parsers for RAG (DEV Community)](https://dev.to/ashokan/from-pdfs-to-markdown-evaluating-document-parsers-for-air-gapped-rag-systems-58eh)
- [Benchmarking PDF to Markdown Converters (AI Advances)](https://ai.gopubby.com/benchmarking-pdf-to-markdown-document-converters-fc65a2c73bf2)
- [MarkItDown vs Docling guide (AI Builder Club)](https://www.aibuilderclub.com/blog/markitdown-microsoft-convert-files-markdown-llm)
- [OpenDataLoader PDF on GitHub](https://github.com/opendataloader-project/opendataloader-pdf)
