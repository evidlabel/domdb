import uuid
from datetime import datetime
from .date_utils import extract_verdict_date
from ...model import ModelItem

def create_info_yml(case: ModelItem) -> dict:
    """Create info.yml content from case."""
    verdict_date = extract_verdict_date(case) or "Unknown"
    profession = (case.profession.displayText or "Unknown") if case.profession else "Unknown"
    instance = (case.instance.displayText or "Unknown") if case.instance else "Unknown"
    case_type = (case.caseType.displayText or "Unknown") if case.caseType else "Unknown"
    court = f"{profession}, {instance}, {case_type}"
    subjects = ", ".join(
        s.displayText or "" for s in case.caseSubjects or []
    ) or "Unknown"
    return {
        "original_name": case.courtCaseNumber or "unknown",
        "uuid": str(uuid.uuid5(uuid.NAMESPACE_OID, case.id or "unknown")),
        "time_added": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "dates": verdict_date,
        "title": case.headline or "No Title",
        "authors": case.author or case.officeName or "Domstol",
        "tags": subjects,
        "label": court,
        "url": f"https://domsdatabasen.dk/#sag/{case.id or 'unknown'}",
    }
