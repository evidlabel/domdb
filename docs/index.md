# Welcome to domdb

Tools for citing Danish judicial verdicts in LaTeX.

## Overview

`domdb` is a Python package that helps researchers and legal professionals work with Danish judicial verdicts by:

- Downloading verdicts from domsdatabasen.dk
- Converting verdict data to BibTeX format for LaTeX documents

## Quick Start

```bash
poetry install
poetry run domdb download-verdicts
poetry run domdb json2bib
```

See [Installation](installation.md) and [Usage](usage.md) for detailed instructions.
