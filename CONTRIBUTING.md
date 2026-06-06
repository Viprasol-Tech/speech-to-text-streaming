# Contributing

Thanks for your interest in improving **Speech To Text Streaming** by Viprasol Tech!

## Getting started

```bash
pip install -e ".[dev]"
```

## Before you open a PR

Please make sure all checks pass locally:

```bash
python -m ruff check .
python -m ruff format --check .
python -m mypy src
python -m pytest
```

## Guidelines

- Keep changes focused and well tested — the suite must stay fully offline (no network, models, or keys).
- New public functions and classes should be typed and documented.
- Follow the existing code style; `ruff format` is the source of truth.
- For larger features, open an issue first to discuss the design.

## Reporting issues

Use the issue templates. For security reports, see [SECURITY.md](SECURITY.md).

By contributing you agree that your contributions are licensed under the MIT License.
