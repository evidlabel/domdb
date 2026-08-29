[![Tests](https://github.com/evidlabel/domdb/actions/workflows/tests.yml/badge.svg)](https://github.com/evidlabel/domdb/actions/workflows/tests.yml)
[![Release](https://img.shields.io/github/v/release/evidlabel/domdb)](https://github.com/evidlabel/domdb/releases)
[![Python](https://img.shields.io/badge/python-%3E%3D3.12-blue)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

# domdb

Tools translating Danish judicial verdicts to BibTeX, Hayagriva YAML, or Markdown, for use in LaTeX or Typst.

Agent-oriented usage: see **[`SKILL.md`](SKILL.md)** in this directory.

## Features
- Download Danish judicial verdicts from domsdatabasen.dk
- Convert JSON verdict data to BibTeX, Hayagriva YAML, Markdown, or EVID format

## Installation

```bash
uv pip install git+https://github.com/evidlabel/domdb.git
domdb -h
```

**Note**: To use this tool, you must obtain a username and password from [Domsdatabasen](https://domsdatabasen.dk/spoergsmaal-og-svar/api-adgang-til-domsdatabasen/) to access the domsdatabasen.dk API.

## Usage

### Download Verdicts
```sh
domdb download
```
Downloads the latest verdicts into the local verdicts storage. Each verdict contains the full PDF, so `download` only fetches new entries rather than re-downloading everything.

### JSON to BibTeX
```sh
# Basic conversion
domdb output bib

# With custom paths and limit
domdb output bib -d ./cases -o ./references.bib -n 100
```

### JSON to Hayagriva YAML (Typst)
```sh
# Basic conversion → resources/cases.yml
domdb output hay

# With custom paths and limit
domdb output hay -d ./cases -o ./references.yml -n 100
```

Each entry uses Hayagriva `type: Case` with title, court author, date, case number (`serial-number`), subjects, and URL. Use with Typst `#bibliography("references.yml")`.

### JSON to Markdown
```sh
# Basic conversion
domdb output md

# With custom paths and limit
domdb output md -d ./cases -o ./cases.md -n 100

# Split by year into separate files
domdb output md -s True

# Filter cases containing a keyword (matches case metadata only)
domdb output md -k "erstatning"

# Require multiple keywords (space-separated after a single -k, AND semantics)
domdb output md -k "psykisk vold" "krisecenter"

# Search the full verdict body text (HTML/PDF), not just metadata.
# This finds words like "krisecenter" that only appear in the document body.
domdb output md -k "psykisk vold" "krisecenter" --full-text -o resources/psykvold_krisecenter.md
```

### JSON to EVID
```sh
domdb output j2e
domdb output j2e -d ./cases -o ./evid -n 100
```

Scanned (image-only) PDFs are skipped during text extraction rather than emitting empty per-page sections.

### Query cached verdicts (legal research)

Build a metadata index once after downloading; queries then filter by date, court, subject, keywords, and legal paragraph references.

```sh
# Index the cache (fast date/court/subject/body filtering)
domdb -d ~/domdatabasen/cases query index

# Count verdicts citing straffeloven § 237 between 2015 and 2024
domdb -d ~/domdatabasen/cases query count -p "straffeloven § 237" --from 2015-01-01 --to 2024-12-31

# Count verdicts mentioning a paragraph in a specific year
domdb -d ~/domdatabasen/cases query count -p "§ 117 stk. 1" --from 2020-01-01 --to 2020-12-31

# Find words in verdict body text (HTML/PDF extraction)
domdb -d ~/domdatabasen/cases query count -k "krisecenter" --full-text

# List matching verdicts (JSON for scripts)
domdb -d ~/domdatabasen/cases query list -k "psykisk vold" --full-text -n 20 --format json

# Combine paragraph, keywords, court, and date range
domdb -d ~/domdatabasen/cases query list -p "straffeloven § 237" -k "vold" --court "Østre Landsret" --from 2018-01-01
```

Paragraph search checks headlines, metadata, and indexed HTML body text. Use `--full-text` to also search PDF-only verdicts (slower). Keyword search uses metadata only unless `--full-text` is set. Re-run `query index` after downloading new cases.

### Using with [typst](https://typst.app/)

```bash
# Preferred: Hayagriva YAML from the local case cache
domdb output hay -o cases.yml

echo '#bibliography("cases.yml", full: true)' > all.typ
typst compile all.typ

# Or BibTeX (also accepted by Typst)
domdb output bib -o cases.bib
echo '#bibliography("cases.bib", full: true)' > all.typ
typst compile all.typ
```

## Configuration

Set environment variables:
```sh
export DOMDB_USER_ID="your_user_id"
export DOMDB_PASSWORD="your_password"
```

Default cases directory: `~/domdatabasen/cases` — override with `-d/--directory`.

## License
MIT License

## Disclaimer

`domdb` is a tool for converting a publicly available Danish database of verdicts into BibTeX format for use in LaTeX or typst.
It does *not* provide legal advice or interpret legal content.

The tool processes and represents data from `domsdatabasen.dk` which is a public source, without modification to the original content, other than for the purposes of correct rendering in LaTeX.

Users are responsible for verifying the accuracy and applicability of the data for their purposes.

`domdb` does not publish the content of the verdicts because they may be subject to modification, in particular through updated pseudonymization. If you need the content of the verdicts, apply for API access.
