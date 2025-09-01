# Usage

**Note**: To use this tool, you must obtain a username and password from [Domsdatabasen](https://domsdatabasen.dk/spoergsmaal-og-svar/api-adgang-til-domsdatabasen/) to access the domsdatabasen.dk API.

## Downloading Verdicts

```bash
domdb download
```

## Converting to BibTeX

```bash
# Basic usage
domdb output bib

# With custom options
domdb output bib -d ./cases -o ./refs.bib -n 100
```

## Configuration

Default cases directory: `~/domdatabasen/cases`
Override with `-d/--directory` flag in any command.
