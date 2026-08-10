import sys
import os

from domdb.core.converters.json2hay.convert import convert_json_to_hay
from domdb.core.exceptions import ConversionError


def hay(number: int, directory: str, output: str):
    """Convert JSON case files to Hayagriva YAML format."""
    directory = os.path.expanduser(directory)
    number = None if number == -1 else number
    try:
        count = convert_json_to_hay(directory, output, number)
        print(f"Converted {count} unique cases to {output}")
    except ConversionError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
