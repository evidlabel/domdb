import os
from typing import Optional

import yaml
from loguru import logger

from .entry import create_hay_entry
from ..case_load import load_cases


def convert_json_to_hay(
    directory: str, output: str, number: Optional[int] = None
) -> int:
    """Convert JSON case files to Hayagriva YAML format."""
    cases = load_cases(directory, number)
    entries: dict[str, dict] = {}

    for case in cases:
        key, entry = create_hay_entry(case)
        if key not in entries:
            entries[key] = entry

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
