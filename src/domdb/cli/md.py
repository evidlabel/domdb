import sys
import os

from domdb.core.converters.json2md.convert import convert_json_to_md
from domdb.core.exceptions import ConversionError


def md(number: int, directory: str, output: str):
    """Convert JSON case files to Markdown format."""
    directory = os.path.expanduser(directory)
    number = None if number == -1 else number
    try:
        count = convert_json_to_md(directory, output, number)
        print(f"Converted {count} unique cases to {output}")
    except ConversionError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
