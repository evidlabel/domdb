import logging

from ..config import load_config
from .auth import get_access_token
from .fetch import get_sager
from .storage import get_last_saved_page, save_cases

logger = logging.getLogger(__name__)


def load_next_batch(directory: str) -> int:
    """Load and save the next batch of cases."""
    config = load_config()
    logger.info(f"Starting to load next batch in directory: {directory}")
    token = get_access_token()
    page_number = get_last_saved_page(directory)
    logger.info(f"Fetching page {page_number}...")
    cases = get_sager(token, page_number=page_number, per_page=config["batch_size"])
    if cases:
        for case in cases:
            headline = case.get("headline", "No headline")
            case_id = case.get("id", "No ID")
            logger.info(f"Fetched case: {headline} (ID: {case_id})")
        save_cases(page_number, cases, directory)
        logger.info(f"Successfully fetched and saved {len(cases)} cases")
        return len(cases)
    logger.info("No cases fetched")
    return 0
