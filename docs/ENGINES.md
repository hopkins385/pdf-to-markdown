# Engines

See the engine overview table in the [README](../README.md#engines) for a quick comparison.

## Auto mode

`--engine auto` runs PyMuPDF4LLM first. If the text yield is below 100 characters per page on average, it switches to Marker if installed, or prints an install hint otherwise.

## Claude model pricing

`--engine claude` prints a cost summary (tokens + estimated USD) after conversion, based on this table:

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

PDFs with more than 50 pages prompt for confirmation before starting, since each page is a separate API call. `--images` has no effect with `--engine claude`; it doesn't extract embedded images.
