import glob
import json
import os
from typing import Optional
from collections import defaultdict
import numpy as np
from loguru import logger
from pydantic import ValidationError

from .entry import create_md_entry
from ....core.exceptions import ConversionError
from ...model import ModelItem


def convert_json_to_md(
    directory: str,
    output: str,
    number: Optional[int] = None,
    split_by_year: bool = False,
) -> int:
    """Convert JSON case files to Markdown format."""
    logger.info(f"Loading verdicts from directory: {directory}")
    entries = []

    json_files = glob.glob(f"{directory}/*.json")
    logger.info(f"Found {len(json_files)} JSON files")
    if not json_files:
        raise ConversionError(f"No JSON files found in {directory}")

    count = 0
    for file_path in json_files:
        logger.info(f"Processing file: {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            cases_data = json.load(f)
            logger.info(f"Loaded {len(cases_data)} raw cases from {file_path}")
            processed_count = 0
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
                processed_count += 1
            logger.info(f"Processed {processed_count} valid cases from {file_path}")

    # Remove duplicates based on ID
    seen = set()
    unique_entries = []
    for entry in entries:
        if entry["id"] not in seen:
            unique_entries.append(entry)
            seen.add(entry["id"])
    entries = unique_entries
    logger.info(f"After deduplication: {len(unique_entries)} unique cases")

    # Separate known and unknown dates
    known_entries = [e for e in entries if e["date"] != "Unknown"]
    unknown_entries = [e for e in entries if e["date"] == "Unknown"]
    logger.info(
        f"Cases with known dates: {len(known_entries)}, unknown: {len(unknown_entries)}"
    )

    # Sort known entries by date descending
    if known_entries:
        dates = np.array([e["date"] for e in known_entries])
        sorted_indices = np.argsort(dates)[::-1]
        known_entries = [known_entries[i] for i in sorted_indices]
        logger.info(f"Sorted {len(known_entries)} cases with known dates descending")

    # Combine: known (sorted desc) then unknown
    entries = known_entries + unknown_entries

    if split_by_year:
        logger.info("Splitting output by year")
        year_groups = defaultdict(list)
        for entry in entries:
            year = entry["date"][:4] if entry["date"] != "Unknown" else "unknown"
            year_groups[year].append(entry)
        total_count = 0
        for year in sorted(year_groups.keys()):
            group_entries = year_groups[year]
            year_output = os.path.join(os.path.dirname(output), f"cases_{year}.md")
            os.makedirs(os.path.dirname(year_output), exist_ok=True)
            with open(year_output, "w", encoding="utf-8") as f:
                for entry in group_entries:
                    f.write(entry["md"] + "\n\n")
            logger.info(f"Wrote {len(group_entries)} cases to {year_output}")
            total_count += len(group_entries)
        return total_count
    else:
        logger.info(f"Writing Markdown output to {output}")
        os.makedirs(os.path.dirname(output), exist_ok=True)
        with open(output, "w", encoding="utf-8") as f:
            for entry in entries:
                f.write(entry["md"] + "\n\n")
        logger.info(f"Converted {len(entries)} unique cases to {output}")
        return len(entries)
