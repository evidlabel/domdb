import sys
import os
from typing import List

from loguru import logger
from domdb.core.converters.json2md.convert import convert_json_to_md
from domdb.core.exceptions import ConversionError


def md(
    number: int,
    directory: str,
    output: str,
    split_by_year: bool,
    keywords: List[str],
    full_text: bool,
):
    """Convert JSON case files to Markdown format."""
    directory = os.path.expanduser(directory)
    number = None if number == -1 else number
    logger.info(
        f"Starting Markdown conversion from {directory}, max {number or 'all'} cases, output to {output}, split by year: {split_by_year}, filter: {keywords}, full_text: {full_text}"
    )
    try:
        count = convert_json_to_md(
            directory, output, number, split_by_year, keywords, full_text
        )
        logger.info(f"Successfully converted {count} cases")
        print(f"Converted {count} unique cases")
    except ConversionError as e:
        logger.error(f"Conversion error: {e!s}")
        print(str(e), file=sys.stderr)
        sys.exit(1)
