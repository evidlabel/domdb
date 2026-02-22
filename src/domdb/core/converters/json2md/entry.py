import re
from datetime import datetime
import logging

from ...model import ModelItem
from ....core.exceptions import ConversionError

logger = logging.getLogger(__name__)


def create_md_entry(case: ModelItem) -> dict:
    """Create a Markdown entry from a case dictionary."""
    try:
        author = case.author or case.officeName or "Domstol"
        profession = (
            (case.profession.displayText or "Unknown") if case.profession else "Unknown"
        )
        instance = (
            (case.instance.displayText or "Unknown") if case.instance else "Unknown"
        )
        case_type = (
            (case.caseType.displayText or "Unknown") if case.caseType else "Unknown"
        )
        court = f"{profession}, {instance}, {case_type}"

        subjects = (
            ", ".join(s.displayText or "" for s in case.caseSubjects or []) or "Unknown"
        )

        verdict_date = "Unknown"
        for doc in case.documents or []:
            if doc.verdictDateTime and isinstance(doc.verdictDateTime, str):
                try:
                    verdict_date = datetime.strptime(
                        doc.verdictDateTime, "%Y-%m-%dT%H:%M:%S"
                    ).strftime("%Y-%m-%d")
                    break
                except ValueError:
                    continue

        case_number = case.courtCaseNumber or "unknown"
        entry_id = re.sub(r"\W+", "", case_number).lower()

        md = f"""- **{case.headline or "No Title"}**
  - Author: {author}
  - Court: {court}
  - Date: {verdict_date}
  - Publisher: {subjects}
  - Pages: {case_number}
  - URL: <https://domsdatabasen.dk/#sag/{case.id or "unknown"}>
"""
        logger.info(f"Created Markdown entry for case ID: {entry_id}")
        return {"id": entry_id, "date": verdict_date, "md": md}
    except Exception as e:
        logger.error(f"Failed to create Markdown entry: {str(e)}")
        raise ConversionError(f"Failed to create Markdown entry: {str(e)}")
