from typing import Optional
from datetime import datetime

from ...model import ModelItem


def extract_verdict_date(case: ModelItem) -> Optional[str]:
    """Extract verdict date from case documents."""
    for doc in case.documents or []:
        if doc.verdictDateTime and isinstance(doc.verdictDateTime, str):
            try:
                return datetime.strptime(
                    doc.verdictDateTime, "%Y-%m-%dT%H:%M:%S"
                ).strftime("%Y-%m-%d")
            except ValueError:
                continue
    return None


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
        "id": case.id or "unknown",
        "headline": case.headline or "No Title",
        "court": court,
        "date": verdict_date,
        "subjects": subjects,
        "case_number": case.courtCaseNumber or "Unknown",
        "url": f"https://domsdatabasen.dk/#sag/{case.id or 'unknown'}",
    }


def create_label_tex(case: ModelItem) -> str:
    """Create label.tex content for LaTeX citation."""
    headline = case.headline or "No Title"
    case_number = case.courtCaseNumber or "Unknown"
    verdict_date = extract_verdict_date(case) or "Unknown"
    return f"""\\label{{case-{case.id or 'unknown'}}}

\\textbf{{{headline}}}\\\\
Case Number: {case_number}\\\\
Date: {verdict_date}
"""
