import os
import requests
import json
from typing import List, Optional
import logging
from .config import load_config

API_BASE_URL = "https://domsdatabasen.dk/webapi/kapi/v1"
USER_ID = os.getenv("DOMDB_USER_ID")
PASSWORD = os.getenv("DOMDB_PASSWORD")

logger = logging.getLogger(__name__)

class DownloadError(Exception):
    """Custom exception for download-related errors."""
    pass

def get_access_token() -> Optional[str]:
    """Authenticate and retrieve an access token."""
    try:
        url = f"{API_BASE_URL}/autoriser"
        headers = {"Content-Type": "application/json"}
        body = {"Email": USER_ID, "Password": PASSWORD}

        if not USER_ID or not PASSWORD:
            logger.error("Missing USER_ID or PASSWORD environment variables")
            raise DownloadError("Missing USER_ID or PASSWORD environment variables")

        response = requests.post(url, json=body, headers=headers, timeout=10)
        response.raise_for_status()
        logger.info("Successfully obtained access token")
        return response.json()["tokenString"]
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to get access token: {str(e)}")
        raise DownloadError(f"Failed to get access token: {str(e)}")

def get_sager(token: str, page_number: int = 1, per_page: int = 100) -> List[dict]:
    """Fetch cases from the API."""
    try:
        url = f"{API_BASE_URL}/sager"
        headers = {"Authorization": f"Bearer {token}"}
        params = {"sideNr": page_number, "perSide": per_page}

        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        logger.info(f"Fetched {len(response.json())} cases from page {page_number}")
        return response.json()
    except Exception as e:
        logger.error(f"Failed to fetch cases: {str(e)}")
        raise DownloadError(f"Failed to fetch cases: {str(e)}")

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

def load_next_batch(directory: str) -> int:
    """Load and save the next batch of cases."""
    config = load_config()
    logger.info(f"Starting to load next batch in directory: {directory}")
    token = get_access_token()
    page_number = get_last_saved_page(directory)
    logger.info(f"Fetching page {page_number}...")
    cases = get_sager(token, page_number=page_number, per_page=config["batch_size"])
    if cases:
        save_cases(page_number, cases, directory)
        logger.info(f"Successfully fetched and saved {len(cases)} cases")
        return len(cases)
    logger.info("No cases fetched")
    return 0
