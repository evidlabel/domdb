import os
import requests
import json
from typing import List, Optional

API_BASE_URL = "https://domsdatabasen.dk/webapi/kapi/v1"
USER_ID = os.getenv("DOMDB_USER_ID")
PASSWORD = os.getenv("DOMDB_PASSWORD")
CASES_DIR = os.path.expanduser("~/domdatabasen/cases")


class DownloadError(Exception):
    """Custom exception for download-related errors."""

    pass


def get_access_token() -> Optional[str]:
    """Authenticate and retrieve an access token.

    Returns:
        str: Access token if successful
        None: If authentication fails

    Raises:
        DownloadError: If API request fails
    """
    try:
        url = f"{API_BASE_URL}/autoriser"
        headers = {"Content-Type": "application/json"}
        body = {"Email": USER_ID, "Password": PASSWORD}

        if not USER_ID or not PASSWORD:
            raise DownloadError("Missing USER_ID or PASSWORD environment variables")

        response = requests.post(url, json=body, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()["tokenString"]
    except requests.exceptions.RequestException as e:
        raise DownloadError(f"Failed to get access token: {str(e)}")


def get_sager(token: str, page_number: int = 1, per_page: int = 100) -> List[dict]:
    """Fetch cases from the API.

    Args:
        token: Authentication token
        page_number: Page number to fetch
        per_page: Number of cases per page

    Returns:
        List of case dictionaries

    Raises:
        DownloadError: If API request fails
    """
    try:
        url = f"{API_BASE_URL}/sager"
        headers = {"Authorization": f"Bearer {token}"}
        params = {"sideNr": page_number, "perSide": per_page}

        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise DownloadError(f"Failed to fetch cases: {str(e)}")


def get_last_saved_page(directory: str = CASES_DIR) -> int:
    """Determine the last saved page number."""
    if not os.path.exists(directory):
        return 1

    try:
        files = [f for f in os.listdir(directory) if f.startswith("cases_")]
        if not files:
            return 1
        return max(int(f.split("_")[-1].split(".")[0]) for f in files) + 1
    except (ValueError, IndexError):
        return 1


def save_cases(page_number: int, cases: List[dict], directory: str = CASES_DIR) -> None:
    """Save cases to a JSON file."""
    os.makedirs(directory, exist_ok=True)
    file_path = os.path.join(directory, f"cases_{page_number}.json")
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(cases, f, ensure_ascii=False, indent=2)
        print(f"Saved {len(cases)} cases to {file_path}")
    except IOError as e:
        raise DownloadError(f"Failed to save cases: {str(e)}")


def load_next_batch(directory: str = CASES_DIR) -> int:
    """Load and save the next batch of cases."""
    try:
        token = get_access_token()
        page_number = get_last_saved_page(directory)
        print(f"Fetching page {page_number}...")

        cases = get_sager(token, page_number=page_number, per_page=25)
        if cases:
            save_cases(page_number, cases, directory)
            return len(cases)
        return 0
    except DownloadError as e:
        print(f"Error: {str(e)}")
        return 0
