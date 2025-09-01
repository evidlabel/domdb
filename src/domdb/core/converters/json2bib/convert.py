import glob
import json
import os
from typing import Optional
import bibtexparser as bib
import logging
import numpy as np  # Added for potential vectorization, e.g., in sorting
from pydantic import ValidationError

from .entry import create_bib_entry
from ....core.exceptions import ConversionError
from ...model import ModelItem

logger = logging.getLogger(__name__)


def convert_json_to_bib(
    directory: str, output: str, number: Optional[int] = None
) -> int:
    """Convert JSON case files to BibTeX format."""
    database = bib.bibdatabase.BibDatabase()
    database.entries = []

    json_files = glob.glob(f"{directory}/*.json")
    logger.info(f"Searching for JSON files in: {directory}")
    if not json_files:
        raise ConversionError(f"No JSON files found in {directory}")

    count = 0
    for file_path in json_files:
        logger.info(f"Processing file: {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            cases_data = json.load(f)
            for case_data in cases_data:
                try:
                    case = ModelItem.model_validate(case_data)
                    if not case.id:
                        logger.error("Skipping case without id")
                        continue
                except ValidationError as e:
                    logger.error(f"Invalid case data: {str(e)}")
                    continue
                if number and count >= number:
                    break
                database.entries.append(create_bib_entry(case))
                count += 1

    # Remove duplicate entries based on ID
    seen = set()
    unique_entries = []
    for entry in database.entries:
        if entry["ID"] not in seen:
            unique_entries.append(entry)
            seen.add(entry["ID"])
    database.entries = unique_entries

    # Sort using numpy for vectorization example (though simple sort suffices)
    dates = np.array([entry.get("date", "0000-00-00") for entry in database.entries])
    sorted_indices = np.argsort(dates)[::-1]
    database.entries = [database.entries[i] for i in sorted_indices]

    os.makedirs(os.path.dirname(output), exist_ok=True)
    with open(output, "w", encoding="utf-8") as f:
        writer = bib.bwriter.BibTexWriter()
        f.write(writer.write(database))
    logger.info(f"Converted {len(database.entries)} unique cases to {output}")
    return len(database.entries)
