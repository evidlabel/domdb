#!/usr/bin/env python
import re
import glob
import json
import os
from datetime import datetime
from typing import List, Optional
from domdb.core.download_verdicts import CASES_DIR
import bibtexparser as bib


class ConversionError(Exception):
    """Custom exception for conversion errors."""

    pass


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

        return {
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
    except Exception as e:
        raise ConversionError(f"Failed to create BibTeX entry: {str(e)}")


def main(args=None):
    """Convert JSON case files to BibTeX format."""
    database = bib.bibdatabase.BibDatabase()
    database.entries = []

    try:
        json_files = glob.glob(f"{args.directory}/*.json")
        if not json_files:
            raise ConversionError(f"No JSON files found in {args.directory}")

        count = 0
        for file_path in json_files:
            with open(file_path, "r", encoding="utf-8") as f:
                cases = json.load(f)
                for case in cases:
                    if args.number and count >= args.number:
                        break
                    database.entries.append(create_bib_entry(case))
                    count += 1

        database.entries.sort(key=lambda x: x.get("date", "0000-00-00"), reverse=True)

        os.makedirs(os.path.dirname(args.output), exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            writer = bib.bwriter.BibTexWriter()
            f.write(writer.write(database))
        print(f"Converted {count} cases to {args.output}")

    except ConversionError as e:
        print(f"Error: {str(e)}")
        exit(1)


if __name__ == "__main__":
    from src.cli.cli import main as cli_main

    cli_main()
