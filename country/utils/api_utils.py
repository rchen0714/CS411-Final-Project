import logging
import os
import requests
import random
import time
from typing import List

from country.db import db
from country.utils.logger import configure_logger
from country.models.country_model import CountryData

logger = logging.getLogger(__name__)
configure_logger(logger)

REST_COUNTRY_BASE_URL = os.getenv("REST_COUNTRY_BASE_URL", "https://restcountries.com/v3.1")

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
    """Fetch a single country by name from the REST Countries API."""
    logger.info(f"Fetching country by name: {name}")
    try:
        response = requests.get(f"{REST_COUNTRY_BASE_URL}/name/{name}")
        if response.status_code == 200:
            return normalize_country(response.json()[0])
        logger.warning(f"Country '{name}' not found.")
    except requests.RequestException as e:
        logger.error(f"Error fetching country '{name}': {e}")
    return None

def get_or_fetch_country(name: str) -> CountryData | None:
    """
    Get a country from the database or fetch from the API if not found.
    
    Args:
        name (str): The name of the country.

    Returns:
        CountryData or None: The country data object or None if not found.
    """
    logger.info(f"Looking for country '{name}' in database")
    country = CountryData.query.filter_by(name=name).first()
    if country:
        logger.info(f"Found '{name}' in database")
        return country

    logger.info(f"Fetching '{name}' from API")
    fetched = fetch_country_by_name(name)
    if fetched:
        try:
            db.session.add(fetched)
            db.session.commit()
            logger.info(f"Saved '{name}' to database")
            return fetched
        except Exception as e:
            logger.error(f"Failed to save '{name}' to DB: {e}")
            db.session.rollback()
    return None

def get_country_with_cache(name: str, cache: dict, ttl: dict, ttl_seconds: int) -> CountryData:
    """
    Retrieves a country by name, using the provided cache if possible, 
    otherwise calls get_or_fetch_country and caches the result.

    Args:
        name (str): The name of the country.
        cache (dict): Cache dictionary for storing CountryData.
        ttl (dict): Time-to-live dictionary for cache expiration.
        ttl_seconds (int): Duration to cache each entry.

    Returns:
        CountryData: The retrieved country data.

    Raises:
        ValueError: If the country cannot be found.
    """
    now = time.time()

    if name in cache and ttl.get(name, 0) > now:
        logger.debug(f"Country '{name}' retrieved from cache")
        return cache[name]

    country = get_or_fetch_country(name)
    if not country:
        logger.error(f"Country '{name}' not found via API or DB")
        raise ValueError(f"Country '{name}' could not be found")

    cache[name] = country
    ttl[name] = now + ttl_seconds
    return country

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
