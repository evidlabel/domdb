# Contributing

## Development Setup

```bash
uv venv
source .venv/bin/activate  # On Unix-like systems
uv sync --dev  # Assuming dev dependencies are configured
uv run pytest
```

## Building Documentation

```bash
uv run mkdocs serve  # Local preview
uv run mkdocs build  # Build static site
```

## Submitting Changes

1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Push to your fork
5. Create a pull request
