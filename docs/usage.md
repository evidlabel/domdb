# Usage

**Note**: To use this tool, you must obtain a username and password from [Domstolsstyrelsen](https://www.domstol.dk/om-domstolsstyrelsen/kontakt/) to access the domsdatabasen.dk API.

## Downloading Verdicts

```bash
domdb get
```

## Converting to BibTeX

```bash
# Basic usage
domdb bib

# With custom options
domdb bib -d ./cases -o ./refs.bib -n 100
```

## Configuration

Default cases directory: `~/domdatabasen/cases`
Override with `-d/--directory` flag in any command.
