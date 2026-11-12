from typing import Optional

from ...model import ModelItem
from ..fields import verdict_date_from_datetime


def extract_verdict_date(case: ModelItem) -> Optional[str]:
    """Extract verdict date from case documents."""
    for doc in case.documents or []:
        if doc.verdictDateTime and isinstance(doc.verdictDateTime, str):
            parsed = verdict_date_from_datetime(doc.verdictDateTime)
            if parsed:
                return parsed
    return None
