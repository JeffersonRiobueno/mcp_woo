import requests
from typing import Dict, Optional
from .config import WOO_URL, WOO_CONSUMER_KEY, WOO_CONSUMER_SECRET, logger

def make_request(endpoint: str, method: str = "GET", params: Optional[Dict] = None, data: Optional[Dict] = None) -> Dict:
    """Make authenticated request to WooCommerce API"""
    try:
        url = f"{WOO_URL}/wp-json/wc/v3/{endpoint}"
        auth = (WOO_CONSUMER_KEY, WOO_CONSUMER_SECRET)

        logger.info(f"Making {method} request to {url}")

        if method == "GET":
            response = requests.get(url, auth=auth, params=params, timeout=30)
        elif method == "POST":
            response = requests.post(url, auth=auth, json=data, timeout=30)
        else:
            raise ValueError(f"Unsupported method: {method}")

        response.raise_for_status()
        logger.info(f"Request successful, status: {response.status_code}")
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed for endpoint {endpoint}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in make_request: {e}")
        raise
