import re
import glob
import json
import os
from datetime import datetime
from typing import Optional
import bibtexparser as bib
import logging

class ConversionError(Exception):
    """Custom exception for conversion errors."""
    pass

logger = logging.getLogger(__name__)

def create_bib_entry(case: dict) -> dict:
    """Create a BibTeX entry from a case dictionary."""
    try:
        author = case.get("author") or case.get("officeName", "Domstol")
        profession = case.get("profession", {}).get("displayText", "Unknown")
        instance = case.get("instance", {}).get("displayText", "Unknown")
        case_type = case.get("caseType", {}).get("displayText", "Unknown")
        court = f"{profession}, {instance}, {case_type}"

        subjects = ", ".join(
            s.get("displayText", "Unknown") for s in case.get("caseSubjects", [])
        )

        verdict_date = "Unknown"
        for doc in case.get("documents", []):
            if "verdictDateTime" in doc and isinstance(doc["verdictDateTime"], str):
                try:
                    verdict_date = datetime.strptime(
                        doc["verdictDateTime"], "%Y-%m-%dT%H:%M:%S"
                    ).strftime("%Y-%m-%d")
                    break
                except ValueError:
                    continue

        case_number = case.get("courtCaseNumber", "unknown")
        entry_id = re.sub(r"\W+", "", case_number).lower()

        entry = {
            "ENTRYTYPE": "article",
            "ID": entry_id,
            "title": str(case.get("headline", "No Title")),
            "author": str(author),
            "court": court,
            "date": verdict_date,
            "publisher": subjects,
            "pages": str(case_number),
            "url": f"https://domsdatabasen.dk/#sag/{case.get('id', 'unknown')}",
        }
        logger.info(f"Created BibTeX entry for case ID: {entry_id}")
        return entry
    except Exception as e:
        logger.error(f"Failed to create BibTeX entry: {str(e)}")
        raise ConversionError(f"Failed to create BibTeX entry: {str(e)}")

def convert_json_to_bib(directory: str, output: str, number: Optional[int] = None) -> int:
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
            cases = json.load(f)
            for case in cases:
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

    database.entries.sort(key=lambda x: x.get("date", "0000-00-00"), reverse=True)

    os.makedirs(os.path.dirname(output), exist_ok=True)
    with open(output, "w", encoding="utf-8") as f:
        writer = bib.bwriter.BibTexWriter()
        f.write(writer.write(database))
    logger.info(f"Converted {len(database.entries)} unique cases to {output}")
    return len(database.entries)
