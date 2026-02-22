import glob
import json
import os
from typing import Optional
import logging
import numpy as np
from pydantic import ValidationError

from .entry import create_md_entry
from ....core.exceptions import ConversionError
from ...model import ModelItem

logger = logging.getLogger(__name__)


def convert_json_to_md(
    directory: str, output: str, number: Optional[int] = None
) -> int:
    """Convert JSON case files to Markdown format."""
    entries = []

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
                entry = create_md_entry(case)
                entries.append(entry)
                count += 1

    # Remove duplicates based on ID
    seen = set()
    unique_entries = []
    for entry in entries:
        if entry["id"] not in seen:
            unique_entries.append(entry)
            seen.add(entry["id"])
    entries = unique_entries

    # Separate known and unknown dates
    known_entries = [e for e in entries if e["date"] != "Unknown"]
    unknown_entries = [e for e in entries if e["date"] == "Unknown"]

    # Sort known entries by date descending
    if known_entries:
        dates = np.array([e["date"] for e in known_entries])
        sorted_indices = np.argsort(dates)[::-1]
        known_entries = [known_entries[i] for i in sorted_indices]

    # Combine: known (sorted desc) then unknown
    entries = known_entries + unknown_entries

    os.makedirs(os.path.dirname(output), exist_ok=True)
    with open(output, "w", encoding="utf-8") as f:
        for entry in entries:
            f.write(entry["md"] + "\n\n")
    logger.info(f"Converted {len(entries)} unique cases to {output}")
    return len(entries)
