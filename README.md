![Deploy](https://github.com/evidlabel/domdb/actions/workflows/tests.yml/badge.svg)![Version](https://img.shields.io/github/v/release/evidlabel/domdb)

# domdb

Tools translating Danish judicial verdicts to bibtex, for use in LaTeX or typst.

## Features
- Download Danish judicial verdicts from domsdatabasen.dk
- Convert JSON verdict data to BibTeX format

## Installation

```bash
uv pip install https://github.com/evidlabel/domdb.git
domdb -h
```

**Note**: To use this tool, you must obtain a username and password from [Domsdatabasen](https://domsdatabasen.dk/spoergsmaal-og-svar/api-adgang-til-domsdatabasen/) to access the domsdatabasen.dk API.

## Usage 

### Download Verdicts
The `get` command downloads the latest verdicts into the local verdicts storage. 
```sh
domdb get
```
**Note** that each verdict contains the full pdf, which is why `get` only adds the latest and doesn't rerun a full download. 

**Note** that you need to apply for API access in order to use `domdb`.

### JSON to BibTeX
```sh
# Basic conversion
domdb bib

# With custom paths and limit
domdb bib -d ./cases -o ./references.bib -n 100
```

### Using the db using [typst](https://typst.app/)

```bash
wget https://raw.githubusercontent.com/evidlabel/domdb/master/resources/cases.bib  -O cases.bib
echo "Citing all verdicts:
#bibliography(\"cases.bib\",full:true)" > all.typ
typst compile all.typ
```

## Configuration

1. Set environment variables:
```sh
export DOMDB_USER_ID="your_user_id"
export DOMDB_PASSWORD="your_password"
```

2. Default cases directory: `~/domdatabasen/cases`
- Override with `-d/--directory` flag

## Development

Run tests:
```sh
uv run pytest --cov=domdb
```

Serve documentation locally:
```sh
uv run mkdocs serve
```


## License
MIT License


## Disclaimer

`domdb` is a tool for converting a publicly available Danish database of verdicts into BibTeX format for use in LaTeX or typst. 
It does *not* provide legal advice or interpret legal content. 

The tool processes and represents data from `domsdatabasen.dk` which is a public source, without modification to the original content, other than for the purposes of correct rendering in LaTeX. 

Users are responsible for verifying the accuracy and applicability of the data for their purposes.

`domdb` does not publish the content of the verdicts because they may be subject to modification, in particular through updated pseudonymization. If you need the content of the verdicts, apply for API access.
