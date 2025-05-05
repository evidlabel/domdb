# domdb

Tools for citing Danish judicial verdicts in LaTeX.

## Features
- Download Danish judicial verdicts from domsdatabasen.dk
- Convert JSON verdict data to BibTeX format

## Installation

```sh
poetry install
```

**Note**: To use this tool, you must obtain a username and password from [Domstolsstyrelsen](https://www.domstol.dk/om-domstolsstyrelsen/kontakt/) to access the domsdatabasen.dk API.

## Usage Examples

### Download Verdicts
```sh
poetry run domdb download-verdicts
```

### JSON to BibTeX
```sh
# Basic conversion
poetry run domdb json2bib

# With custom paths and limit
poetry run domdb json2bib -d ./cases -o ./references.bib -n 100
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
poetry run pytest --cov=domdb
```

Format code:
```sh
poetry run black .
```

Lint code:
```sh
poetry run flake8 .
```

## License
MIT License
