import os
from typing import Optional
import bibtexparser as bib
from loguru import logger

from .entry import create_bib_entry
from ..case_load import load_cases


def convert_json_to_bib(
    directory: str, output: str, number: Optional[int] = None
) -> int:
    """Convert JSON case files to BibTeX format."""
    database = bib.bibdatabase.BibDatabase()
    database.entries = []

    cases = load_cases(directory, number)
    for case in cases:
        database.entries.append(create_bib_entry(case))

    # Remove duplicate entries based on ID
    seen = set()
    unique_entries = []
    for entry in database.entries:
        if entry["ID"] not in seen:
            unique_entries.append(entry)
            seen.add(entry["ID"])
    database.entries = unique_entries
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
