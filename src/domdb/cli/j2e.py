import sys
import os

from domdb.core.converters.json2evid.processing import convert_json_to_evid
from domdb.core.exceptions import EvidConversionError


def j2e(number: int, directory: str, output: str):
    """Convert JSON case files to EVID directory structure."""
    directory = os.path.expanduser(directory)
    number = None if number == -1 else number
    try:
        count = convert_json_to_evid(directory, output, number)
        print(f"Converted {count} cases to EVID in {output}")
    except EvidConversionError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
