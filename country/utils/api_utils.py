import logging
import os
import requests
import random
from typing import List

from country.utils.logger import configure_logger
from country.models.country_model import CountryData


logger = logging.getLogger(__name__)
configure_logger(logger)


REST_COUNTRY_BASE_URL = os.getenv("REST_COUNTRY_BASE_URL",
                                "https://restcountries.com/v3.1")


def normalize_country(data: dict) -> CountryData:
	"""Converts raw REST Countries API data to a CountryData object."""
	return CountryData(
    	name=data.get("name", {}).get("common", "Unknown"),
    	capital=data.get("capital", ["Unknown"])[0],
    	region=data.get("region", "Unknown"),
    	population=data.get("population", 0),
    	area_km2=data.get("area", 0.0),
    	languages=list(data.get("languages", {}).values()),
    	currencies=list(data.get("currencies", {}).keys()),
    	borders=data.get("borders", []),
    	flag_url=data.get("flags", {}).get("png", ""),
    	timezones=data.get("timezones", [])
	)
 
def fetch_country_by_name(name: str) -> CountryData | None:
    """Fetch a single country by name."""
    logger.info(f"Fetching country by name: {name}")

    try:
        response = requests.get(f"{REST_COUNTRY_BASE_URL}/name/{name}")
        if response.status_code == 200:
            return normalize_country(response.json()[0])
        logger.warning(f"Country '{name}' not found.")
    except requests.RequestException as e:
        logger.error(f"Error fetching country '{name}': {e}")

    return None

def fetch_countries_by_language(language: str) -> List[CountryData]:
    """Fetch a list of countries that speak a given language."""
    logger.info(f"Fetching countries by language: {language}")
    try:
        response = requests.get(f"{REST_COUNTRY_BASE_URL}/lang/{language}")
        if response.status_code == 200:
            return [normalize_country(c) for c in response.json()]
        logger.warning(f"No countries found for language: {language}")
    except requests.RequestException as e:
        logger.error(f"Error fetching countries by language '{language}': {e}")
    return []

def fetch_random_country() -> CountryData | None:
    """Fetch a random country."""
    logger.info("Fetching a random country")
    try:
        response = requests.get(f"{REST_COUNTRY_BASE_URL}/all")
        if response.status_code == 200:
            countries = response.json()
            if countries:
                return normalize_country(random.choice(countries))
        logger.warning("Failed to fetch random country.")
    except requests.RequestException as e:
        logger.error(f"Error fetching random country: {e}")
    return None


# def get_all_countries() -> List:
#     """
#     Fetches all countries from restcountries.com API.

#     Args:
#         None

#     Returns:
#         List: A list of dictionaries containing country information.

#     Raises:
#         RuntimeError: If the request to restcountries.com fails.
#         ValueError: If the response from restcountries.com is not a valid List.
#     """
    

#     # Construct the full URL dynamically
#     url = f"{REST_COUNTRY_BASE_URL}/all"

#     try:
#         # Log the request to random.org
#         logger.info(f"Fetching all countries from {url}")

#         response = requests.get(url, timeout=5)
#         response.raise_for_status()

#         countries = response.json()
#         logger.info(f"Received {len(countries)} countries from {url}")

#         return countries

#     except requests.exceptions.Timeout:
#         logger.error("Request to random.org timed out.")
#         raise RuntimeError("Request to random.org timed out.")

#     except requests.exceptions.RequestException as e:
#         logger.error(f"Request to random.org failed: {e}")
#         raise RuntimeError(f"Request to random.org failed: {e}")
