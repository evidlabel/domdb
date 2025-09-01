import sys

from domdb.core.converters.json2bib.convert import convert_json_to_bib
from domdb.core.exceptions import ConversionError


def bib(number: int, directory: str, output: str):
    """Convert JSON case files to BibTeX format."""
    number = None if number == -1 else number
    try:
        count = convert_json_to_bib(directory, output, number)
        print(f"Converted {count} unique cases to {output}")
    except ConversionError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
