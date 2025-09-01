import os

import requests
import logging

from ..exceptions import DownloadError

logger = logging.getLogger(__name__)

API_BASE_URL = "https://domsdatabasen.dk/webapi/kapi/v2"


def get_access_token() -> str:
    """Authenticate and retrieve an access token."""
    try:
        USER_ID = os.getenv("DOMDB_USER_ID")
        PASSWORD = os.getenv("DOMDB_PASSWORD")
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
