import re
from datetime import datetime

from ..model import ModelItem


def parse_case_fields(case: ModelItem) -> dict:
    """Extract common display fields from a ModelItem."""
    author = case.author or case.officeName or "Domstol"
    profession = (case.profession.displayText or "Unknown") if case.profession else "Unknown"
    instance = (case.instance.displayText or "Unknown") if case.instance else "Unknown"
    case_type = (case.caseType.displayText or "Unknown") if case.caseType else "Unknown"
    court = f"{profession}, {instance}, {case_type}"
    subjects = ", ".join(s.displayText or "" for s in case.caseSubjects or []) or "Unknown"

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

    return {
        "author": author,
        "court": court,
        "subjects": subjects,
        "verdict_date": verdict_date,
        "case_number": case_number,
        "entry_id": entry_id,
    }
