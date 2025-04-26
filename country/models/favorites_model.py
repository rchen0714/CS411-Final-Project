import logging
import os
from typing import List
from country.models.country_model import CountryData
from country.utils.api_utils import get_country_with_cache
from country.utils.logger import configure_logger

logger = logging.getLogger(__name__)
configure_logger(logger)

class FavoritesModel:
    """A class to manage favorite countries with caching."""

    def __init__(self):
        self.favorites: List[str] = []
        self._country_cache: dict[str, CountryData] = {}
        self._ttl: dict[str, float] = {}
        self.ttl_seconds = int(os.getenv("TTL", 60))

    def get_country(self, name: str) -> CountryData:
        """Gets country data from cache or DB/API if not cached."""
        return get_country_with_cache(
            name,
            self._country_cache,
            self._ttl,
            self.ttl_seconds
        )

    def add_favorite(self, name: str):
        """Adds a country to the favorites list if not already present."""
        if name not in self.favorites:
            self.favorites.append(name)
            logger.info(f"Added '{name}' to favorites")

    def remove_favorite(self, name: str):
        """Removes a country from the favorites list if present."""
        if name in self.favorites:
            self.favorites.remove(name)
            logger.info(f"Removed '{name}' from favorites")

    def list_favorites(self) -> List[str]:
        """Returns the list of favorite country names."""
        return self.favorites
    
    def is_favorite(self, name: str) -> bool:
        """Returns True if the country is in the favorites list."""
        return name in self.favorites
    
    def clear_favorites(self):
        """Clears the favorites list."""
        self.favorites.clear()
        logger.info("Cleared all favorites")

    
    def compare_favorites(self, name1: str, name2: str) -> dict:
    """
    Compare two favorite countries and return key differences.
    
    Args:
        name1 (str): The name of the first country.
        name2 (str): The name of the second country.

    Returns:
        dict: Dictionary with comparison results.
    """
    if name1 not in self.favorites or name2 not in self.favorites:
        raise ValueError("Both countries must be in favorites to compare.")

    country1 = self.get_country(name1)
    country2 = self.get_country(name2)

    return {
        "countries": (country1.name, country2.name),
        "population_difference": abs(country1.population - country2.population),
        "area_difference": abs(country1.area_km2 - country2.area_km2),
        "shared_languages": list(set(country1.languages) & set(country2.languages)),
        "shared_borders": list(set(country1.borders) & set(country2.borders)),
        "currencies": (country1.currencies, country2.currencies)
    }

