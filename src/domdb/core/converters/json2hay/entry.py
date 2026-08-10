from loguru import logger

from ...model import ModelItem
from ....core.exceptions import ConversionError
from ..fields import parse_case_fields


def create_hay_entry(case: ModelItem) -> tuple[str, dict]:
    """Create a Hayagriva YAML entry (key, fields) from a case."""
    try:
        f = parse_case_fields(case)
        entry: dict = {
            "type": "Case",
            "title": case.headline or "No Title",
            "author": f["author"],
            "serial-number": f["case_number"],
            "url": f"https://domsdatabasen.dk/#sag/{case.id or 'unknown'}",
        }
        if f["verdict_date"] and f["verdict_date"] != "Unknown":
            entry["date"] = f["verdict_date"]
        if f["subjects"] and f["subjects"] != "Unknown":
            entry["publisher"] = f["subjects"]
        if f["court"] and f["court"] != "Unknown, Unknown, Unknown":
            entry["organization"] = f["court"]
        logger.info(f"Created Hayagriva entry for case ID: {f['entry_id']}")
        return f["entry_id"], entry
    except Exception as e:
        logger.error(f"Failed to create Hayagriva entry: {str(e)}")
        raise ConversionError(f"Failed to create Hayagriva entry: {str(e)}") from e
