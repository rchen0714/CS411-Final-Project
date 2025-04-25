import logging
import os
import requests
from typing import List

from temp_country.utils.logger import configure_logger


REST_COUNTRY_BASE_URL = os.getenv("REST_COUNTRY_BASE_URL",
                                "https://restcountries.com/v3.1")


logger = logging.getLogger(__name__)
configure_logger(logger)


def get_all_countries() -> List:
    """
    Fetches all countries from restcountries.com API.

    Args:
        None

    Returns:
        List: A list of dictionaries containing country information.

    Raises:
        RuntimeError: If the request to restcountries.com fails.
        ValueError: If the response from restcountries.com is not a valid List.
    """
    

    # Construct the full URL dynamically
    url = f"{REST_COUNTRY_BASE_URL}/all"

    try:
        # Log the request to random.org
        logger.info(f"Fetching all countries from {url}")

        response = requests.get(url, timeout=5)
        response.raise_for_status()

        countries = response.json()
        logger.info(f"Received {len(countries)} countries from {url}")

        return countries

    except requests.exceptions.Timeout:
        logger.error("Request to random.org timed out.")
        raise RuntimeError("Request to random.org timed out.")

    except requests.exceptions.RequestException as e:
        logger.error(f"Request to random.org failed: {e}")
        raise RuntimeError(f"Request to random.org failed: {e}")
