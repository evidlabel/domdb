from loguru import logger

from ...model import ModelItem
from ....core.exceptions import ConversionError
from ..fields import parse_case_fields


def create_bib_entry(case: ModelItem) -> dict:
    """Create a BibTeX entry from a case dictionary."""
    try:
        f = parse_case_fields(case)
        entry = {
            "ENTRYTYPE": "article",
            "ID": f["entry_id"],
            "title": case.headline or "No Title",
            "author": f["author"],
            "court": f["court"],
            "date": f["verdict_date"],
            "publisher": f["subjects"],
            "pages": f["case_number"],
            "url": f"https://domsdatabasen.dk/#sag/{case.id or 'unknown'}",
        }
        logger.info(f"Created BibTeX entry for case ID: {f['entry_id']}")
        return entry
    except Exception as e:
        logger.error(f"Failed to create BibTeX entry: {str(e)}")
        raise ConversionError(f"Failed to create BibTeX entry: {str(e)}") from e
