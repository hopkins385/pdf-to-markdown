# Contributing

## Setup

```bash
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

To work on Marker or Claude support:

```bash
uv pip install -e ".[dev,marker,claude]"
```

## Tests

```bash
pytest
```

Please add or update tests for any behavior change. Tests build synthetic PDFs at runtime; don't commit fixture PDFs.

## Pull requests

- Keep PRs focused on a single change.
- Run `pytest` before opening a PR.
- Describe the "why" in the PR description, not just the "what".

## Reporting issues

Open an issue with the command you ran, the expected vs. actual output, and your Python version.
