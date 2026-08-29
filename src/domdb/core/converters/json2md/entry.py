from loguru import logger

from ...model import ModelItem
from ....core.exceptions import ConversionError
from ..fields import parse_case_fields


def create_md_entry(case: ModelItem) -> dict:
    """Create a Markdown entry from a case dictionary."""
    try:
        f = parse_case_fields(case)
        md = f"""- **{case.headline or "No Title"}**
  - {f["author"]}
  - {f["court"]}
  - {f["verdict_date"]}
  - {f["subjects"]}
  - {f["case_number"]}
  - <https://domsdatabasen.dk/#sag/{case.id or "unknown"}>
"""
        logger.info(f"Created Markdown entry for case ID: {f['entry_id']}")
        return {"id": f["entry_id"], "date": f["verdict_date"], "md": md}
    except Exception as e:
        logger.error(f"Failed to create Markdown entry: {str(e)}")
        raise ConversionError(f"Failed to create Markdown entry: {str(e)}") from e
