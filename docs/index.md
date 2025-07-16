# domdb

Tools for citing Danish judicial verdicts in LaTeX.

## Overview

`domdb` is a Python package that helps researchers and legal professionals work with Danish judicial verdicts by:

- Downloading verdicts from domsdatabasen.dk
- Converting verdict data to BibTeX format for LaTeX documents

## Quick Start

After installation (see [Installation](installation.md)):

```bash
uv run domdb download-verdicts
uv run domdb json2bib
```

See [Installation](installation.md) and [Usage](usage.md) for detailed instructions.

## Citing verdicts 
### Typst example
```bash

wget https://raw.githubusercontent.com/evidlabel/domdb/master/resources/cases.bib  -O cases.bib
echo "#bibliography(\"cases.bib\",full:true)" > all.typ
typst compile all.typ

```
