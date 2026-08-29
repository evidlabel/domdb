import requests
from typing import List
from loguru import logger

from .auth import API_BASE_URL
from ..exceptions import DownloadError


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
