import os
import json
from typing import List
import logging

from ..exceptions import DownloadError

logger = logging.getLogger(__name__)


def get_last_saved_page(directory: str) -> int:
    """Determine the last saved page number."""
    logger.info(f"Checking last saved page in directory: {directory}")
    if not os.path.exists(directory):
        logger.info("Directory does not exist, starting from page 1")
        return 1

    try:
        files = [f for f in os.listdir(directory) if f.startswith("cases_")]
        if not files:
            logger.info("No case files found, starting from page 1")
            return 1
        return max(int(f.split("_")[-1].split(".")[0]) for f in files) + 1
    except (ValueError, IndexError):
        logger.warning("Error parsing file names, starting from page 1")
        return 1


def save_cases(page_number: int, cases: List[dict], directory: str) -> None:
    """Save cases to a JSON file."""
    logger.info(f"Saving {len(cases)} cases to directory: {directory}")
    os.makedirs(directory, exist_ok=True)
    file_path = os.path.join(directory, f"cases_{page_number}.json")
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(cases, f, ensure_ascii=False, indent=2)
        logger.info(f"Saved {len(cases)} cases to {file_path}")
    except IOError as e:
        logger.error(f"Failed to save cases: {str(e)}")
        raise DownloadError(f"Failed to save cases: {str(e)}")
