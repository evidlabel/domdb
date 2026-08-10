import glob
import json
import os
from typing import Optional

import yaml
from loguru import logger
from pydantic import ValidationError

from .entry import create_hay_entry
from ....core.exceptions import ConversionError
from ...model import ModelItem


def convert_json_to_hay(
    directory: str, output: str, number: Optional[int] = None
) -> int:
    """Convert JSON case files to Hayagriva YAML format."""
    logger.info(f"Loading verdicts from directory: {directory}")
    entries: dict[str, dict] = {}

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
                key, entry = create_hay_entry(case)
                if key not in entries:
                    entries[key] = entry
                    count += 1
                    processed_count += 1
            logger.info(f"Processed {processed_count} valid cases from {file_path}")

    logger.info(f"After deduplication: {len(entries)} unique cases")

    # Sort by date descending (newest first), stable key fallback
    sorted_items = sorted(
        entries.items(),
        key=lambda kv: kv[1].get("date") or "",
        reverse=True,
    )
    ordered = dict(sorted_items)
    logger.info(f"Sorted {len(ordered)} cases by date descending")

    logger.info(f"Writing Hayagriva YAML output to {output}")
    parent = os.path.dirname(output)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(output, "w", encoding="utf-8") as f:
        f.write("# generated-by: domdb output hay\n")
        yaml.safe_dump(
            ordered,
            f,
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False,
            width=1000,
        )
    logger.info(f"Converted {len(ordered)} unique cases to {output}")
    return len(ordered)
