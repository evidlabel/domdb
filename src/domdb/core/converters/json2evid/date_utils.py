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
