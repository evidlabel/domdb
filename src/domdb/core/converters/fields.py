import re
from datetime import datetime

from loguru import logger

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


def verdict_date_from_datetime(value: str) -> str | None:
    """Return the ISO date part of an API ``verdictDateTime`` value.

    The API emits fractional seconds (``2024-05-14T09:30:00.000``), offsets and
    occasionally ``Z``; ``fromisoformat`` handles all three, where the old
    ``strptime("%Y-%m-%dT%H:%M:%S")`` rejected them and silently produced
    "Unknown". A leading ISO date is salvaged from otherwise unparseable values.
    """
    text = value.strip()
    try:
        return datetime.fromisoformat(text).strftime("%Y-%m-%d")
    except ValueError:
        logger.warning(f"Could not parse verdictDateTime as ISO 8601: {value!r}")
        match = re.match(r"(\d{4}-\d{2}-\d{2})", text)
        return match.group(1) if match else None


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
    unparsed: str | None = None
    for doc in case.documents or []:
        value = doc.verdictDateTime
        if not value or not isinstance(value, str):
            continue
        parsed = verdict_date_from_datetime(value)
        if parsed:
            verdict_date = parsed
            break
        if unparsed is None:
            unparsed = value.strip()
    else:
        # Nothing parsed: keep the original string rather than losing the date.
        if unparsed is not None:
            logger.warning(
                f"Keeping unparseable verdictDateTime {unparsed!r} for case {case.id!r}"
            )
            verdict_date = unparsed

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
