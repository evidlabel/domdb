import os
from typing import Optional
from collections import defaultdict
from loguru import logger

from .entry import create_md_entry
from .filter import case_matches_keywords, normalize_keywords
from ..case_load import load_cases


def convert_json_to_md(
    directory: str,
    output: str,
    number: Optional[int] = None,
    split_by_year: bool = False,
    keywords: Optional[list[str]] = None,
    full_text: bool = False,
) -> int:
    """Convert JSON case files to Markdown format."""
    norm_keywords = normalize_keywords(keywords)
    if norm_keywords and full_text:
        logger.info(
            "Full-text mode on: extracting verdict body text (PDF extraction may be slow)"
        )

    # Load all cases; number is applied after keyword filter so the cap counts matches.
    cases = load_cases(directory)
    entries = []
    count = 0
    for case in cases:
        if number and count >= number:
            break
        if not case_matches_keywords(case, norm_keywords, full_text=full_text):
            continue
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
    logger.info(f"After deduplication: {len(unique_entries)} unique cases")

    # Separate known and unknown dates
    known_entries = [e for e in entries if e["date"] != "Unknown"]
    unknown_entries = [e for e in entries if e["date"] == "Unknown"]
    logger.info(
        f"Cases with known dates: {len(known_entries)}, unknown: {len(unknown_entries)}"
    )

    # Sort known entries by date descending
    if known_entries:
        known_entries = sorted(known_entries, key=lambda e: e["date"], reverse=True)
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
