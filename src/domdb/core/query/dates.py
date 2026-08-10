from datetime import date, datetime

from ..converters.json2evid.date_utils import extract_verdict_date
from ..model import ModelItem


def parse_query_date(value: str | None) -> date | None:
    if not value:
        return None
    return datetime.strptime(value, "%Y-%m-%d").date()


def case_verdict_date(case: ModelItem) -> date | None:
    raw = extract_verdict_date(case)
    if not raw or raw == "Unknown":
        return None
    return datetime.strptime(raw, "%Y-%m-%d").date()


def date_in_range(
    verdict: date | None,
    from_date: date | None,
    to_date: date | None,
) -> bool:
    if from_date is None and to_date is None:
        return True
    if verdict is None:
        return False
    if from_date and verdict < from_date:
        return False
    if to_date and verdict > to_date:
        return False
    return True