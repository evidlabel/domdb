import sys
import os

from domdb.core.download.main import load_next_batch
from domdb.core.exceptions import DownloadError


def download(directory: str):
    """Download verdicts from domsdatabasen.dk."""
    directory = os.path.expanduser(directory)
    try:
        count = load_next_batch(directory)
        print(f"Successfully fetched {count} cases")
    except DownloadError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {str(e)}", file=sys.stderr)
        sys.exit(1)
