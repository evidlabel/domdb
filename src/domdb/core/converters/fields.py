import re
from datetime import datetime

from ..model import ModelItem


def slugify_identifier(value: str | None) -> str:
    """Reduce an identifier to a citation-key-safe fragment."""
    return re.sub(r"\W+", "", value or "").lower()


def entry_id_for(case: ModelItem) -> str:
    """Stable citation key for a case.

    The source record id is used when present; the case number is only a
    fallback, because ``courtCaseNumber`` is unique per court instance at best
    and different spellings ("B-1234/2024" vs "B 1234-2024") collapse to the
    same slug.
    """
    return (
        slugify_identifier(case.id)
        or slugify_identifier(case.courtCaseNumber)
        or "unknown"
    )


def unique_entry_id(base: str, used: set[str]) -> str:
    """Return ``base`` or a disambiguated variant, and record it in ``used``.

    Distinct records must never be dropped merely because their preferred key
    collides; the second one becomes ``<base>-2``, then ``-3``, ...
    """
    candidate = base or "unknown"
    if candidate not in used:
        used.add(candidate)
        return candidate
    counter = 2
    while f"{candidate}-{counter}" in used:
        counter += 1
    disambiguated = f"{candidate}-{counter}"
    used.add(disambiguated)
    return disambiguated


def parse_case_fields(case: ModelItem) -> dict:
    """Extract common display fields from a ModelItem."""
    author = case.author or case.officeName or "Domstol"
    profession = (
        (case.profession.displayText or "Unknown") if case.profession else "Unknown"
    )
    instance = (case.instance.displayText or "Unknown") if case.instance else "Unknown"
    case_type = (case.caseType.displayText or "Unknown") if case.caseType else "Unknown"
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
    entry_id = entry_id_for(case)

    return {
        "author": author,
        "court": court,
        "subjects": subjects,
        "verdict_date": verdict_date,
        "case_number": case_number,
        "entry_id": entry_id,
    }
