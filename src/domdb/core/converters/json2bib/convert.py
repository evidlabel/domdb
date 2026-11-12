import os
from typing import Optional
import bibtexparser as bib
from loguru import logger

from .entry import create_bib_entry
from ..case_load import load_cases
from ..fields import unique_entry_id


def convert_json_to_bib(
    directory: str, output: str, number: Optional[int] = None
) -> int:
    """Convert JSON case files to BibTeX format."""
    database = bib.bibdatabase.BibDatabase()
    database.entries = []

    cases = load_cases(directory, number)
    seen_case_ids: set[str] = set()
    used_keys: set[str] = set()
    for case in cases:
        # Only an identical source id is a genuine duplicate (e.g. a page
        # fetched twice). Distinct verdicts must never be collapsed.
        if case.id and case.id in seen_case_ids:
            logger.info(f"Skipping duplicate record for case id: {case.id}")
            continue
        if case.id:
            seen_case_ids.add(case.id)
        entry = create_bib_entry(case)
        entry["ID"] = unique_entry_id(entry["ID"], used_keys)
        database.entries.append(entry)

    logger.info(f"After deduplication: {len(database.entries)} unique cases")

    database.entries = sorted(
        database.entries, key=lambda e: e.get("date", ""), reverse=True
    )
    logger.info(f"Sorted {len(database.entries)} cases by date descending")

    logger.info(f"Writing BibTeX output to {output}")
    os.makedirs(os.path.dirname(output), exist_ok=True)
    with open(output, "w", encoding="utf-8") as f:
        writer = bib.bwriter.BibTexWriter()
        f.write(writer.write(database))
    logger.info(f"Converted {len(database.entries)} unique cases to {output}")
    return len(database.entries)
