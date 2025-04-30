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
        self.favorite_country_int = 1
        self.favorites: List[str] = []
        self._country_cache: dict[str, CountryData] = {}
        self._ttl: dict[str, float] = {}
        self.ttl_seconds = int(os.getenv("TTL", 60))

    ##################################################
    # Country Management Functions
    ##################################################

    def get_country(self, name: str) -> CountryData:
        """
        Retrieves a country by name, using the internal cache if possible.

        This method checks whether a cached version of the country is available
        and still valid. If not, it queries the database and/or makes an "REST Countries" API call, updates the cache, and returns the country.

        Args:
            name (str): The unique name of the country to retrieve.

        Returns:
            CountryData: The CountryData object corresponding to the given name.

        Raises:
            ValueError: If the country cannot be found in the database or when calling "REST Countries" API.
        """
        return get_country_with_cache(
            name,
            self._country_cache,
            self._ttl,
            self.ttl_seconds
        )

    def add_country_to_favorites(self, name: str):
        """
        Adds a country to favorites by name, using the cache or database lookup or API.

        Args:
            name (str): The name of the country to add to favorites.

        Raises:
            ValueError: If the country name is invalid or already exists in favorites.
        """
        logger.info(f"Received request to add country with name {name} to favorites list.")

        if name in self.favorites:
            logger.error(f"Country with name {name} already exists in favorites list.")
            raise ValueError(f"Country with name '{name}' already exists in the favorites")

        name = self.validate_name(name, check_in_favorites=False)

        self.favorites.append(name)
        logger.info(f"Successfully added to Favorites: {name}")


    def remove_favorite(self, name: str):
        """Removes a country from favorites by its name.

        Args:
            name (int): The name of the country to remove from favorites.

        Raises:
            ValueError: If favorites is empty or the name is invalid.

        """
        logger.info(f"Received request to remove country with name {name}")

        self.check_if_empty()
        name = self.validate_name(name, check_in_favorites=False)
        
        if name not in self.favorites:
            logger.warning(f"Country with name {name} not found in favorites list.")
            raise ValueError(f"Country with name {name} not found in the favorites list.")

        self.favorites.remove(name)
        logger.info(f"Successfully removed country with name {name} from favorites")

    def remove_country_by_country_list_number(self, country_list_number: int) -> None:
            """Removes a country from favorites by its list number (1-indexed).
            
            Args:
                list_number (int): The list number of the country to remove.

            Raises:
                ValueError: If the country is empty or the list number is invalid.

            """
            logger.info(f"Received request to remove country at list number {country_list_number}")

            self.check_if_empty()
            country_list_number = self.validate_country_number_in_favorites(country_list_number)
            favorites_index = country_list_number - 1

            logger.info(f"Successfully removed country at country list number {country_list_number}")
            del self.favorites[favorites_index]
            
            
    def clear_favorites(self) -> None:
        """Clears all countries from favorites.

        Clears all countries from favorites. If favorites is already empty, logs a warning.

        """
        logger.info("Received request to clear favorites list")

        try:
            if self.check_if_empty():
                pass
        except ValueError:
            logger.warning("Clearing an empty favorites list")

        self.favorites.clear()
        logger.info("Successfully cleared favorites list")

    ##################################################
    # Country Retrieval Functions
    ##################################################

    def get_all_countries(self) -> List[CountryData]:
        """Returns a list of all countries in the favorites list using cached country data.

        Returns:
            List[CountryDAta]: A list of all countries in the favorites list.

        Raises:
            ValueError: If the favorites list is empty.
        """
        self.check_if_empty()
        logger.info("Retrieving all countries in the favorites list")
        return [self.get_country(name) for name in self.favorites]

    def get_country_by_name(self, name: str) -> CountryData:
        """Retrieves a country from favorites by its name using the cache, DB, or API.

        Args:
            name (str): The name of the country to retrieve.

        Returns:
            CountryData: The country with the specified name.

        Raises:
            ValueError: If the favorites list is empty or the country is not found.
        """
        self.check_if_empty()
        name = self.validate_name(name)
        logger.info(f"Retrieving country with name {name} from the favorites list")
        country = self.get_country(name)
        logger.info(f"Successfully retrieved country: {country.name})")
        return country
    
    def get_country_by_country_list_number(self, country_list_number: int) -> CountryData:
        """Retrieves a country from the favorites list by its country list number (1-indexed).

        Args:
            list_number (int): The list number of the country to retrieve.

        Returns:
            CountyData: The country at the specified list number.

        Raises:
            ValueError: If the favorites is empty or the list number is invalid.
        """
        self.check_if_empty()
        country_list_number = self.is_valid_country_list_number(country_list_number)
        favorites_index = country_list_number - 1

        logger.info(f"Retrieving country at country list number {country_list_number} from favorites list")
        name = self.favorites[favorites_index]
        country = self.get_country(name)
        logger.info(f"Successfully retrieved country: {country.name})")
        return country
    
    ##################################################
    # Retrieving information about Favorite Country
    ##################################################
    
    def test_get_favorites_length(favorites_model, sample_favorites):
        """Test that the correct length of favorites is returned."""
        favorites_model.favorites = [country.name for country in sample_favorites]
        length = favorites_model.get_favorites_length()
        assert length == len(sample_favorites)
    
    
    def get_favorite_country(self) -> CountryData:
        """Returns the favorite country in the list.

        Returns:
            CountryData: The CountryData object with index 1.

        Raises:
            ValueError: If the favorites list is empty.
        """
        self.check_if_empty()
        logger.info("Retrieving the favorite country in the list")
        return self.get_country_by_country_list_number(self.favorite_country_int)

    def get_favorites_length(self) -> int:
        """Returns the number of countries in the favorites list.

        Returns:
            int: The total number of countries in the favorites list.

        """
        length = len(self.favorites)
        logger.info(f"Retrieving total number of favorite countries: {length} countries")
        return length
    
    def get_currency_of_favorite(self, name: str) -> str:
        """ Returns the currency of a country in favorites.

        Args:
            name (str): The name of the Country 

        Returns:
            str: The Currencies of the country
            
        Raises:
            ValueError: If the favorites list is empty or the country name is invalid.
        """
        
        self.check_if_empty()
        name = self.validate_name(name)
        logger.info(f"Retrieving currency information for country: {name}")
        
        country = self.get_country(name)
        if not country.currencies:
            logger.warning(f"Country {name} has no currency information.")
            return "No currency available for this country."
        
        currency_info = ", ".join(country.currencies)
        logger.info(f"Currencies for {name}: {currency_info}")
        return currency_info
    
    def get_languages_of_favorite(self, name: str) -> str:
        """ Returns the languages of a country in favorites.

        Args:
            name (str): The name of the Country 

        Returns:
            str: The Languages of the country
            
        Raises:
            ValueError: If the favorites list is empty or the country name is invalid.
        """
        
        self.check_if_empty()
        name = self.validate_name(name)
        logger.info(f"Retrieving language information for country: {name}")
        
        country = self.get_country(name)
        if not country.languages:
            logger.warning(f"Country {name} has no language information.")
            return "No language available for this country."
        
        language_info = ", ".join(country.languages)
        logger.info(f"Languages for {name}: {language_info}")
        return language_info
    
    def get_borders_of_favorite(self, name: str) -> str:  
        """ Returns the borders of a country in favorites.

        Args:
            name (str): The name of the Country 

        Returns:
            str: The Borders of the country
            
        Raises:
            ValueError: If the favorites list is empty or the country name is invalid.
        """
        
        self.check_if_empty()
        name = self.validate_name(name)
        logger.info(f"Retrieving border information for country: {name}")
        
        country = self.get_country(name)
        if not country.borders:
            logger.warning(f"Country {name} has no border information.")
            return "No border available for this country."
        
        border_info = ", ".join(country.borders)
        logger.info(f"Borders for {name}: {border_info}")
        return border_info
    
    def get_population_of_favorite(self, name: str) -> int:
        """ Returns the population of a country in favorites.

        Args:
            name (str): The name of the Country 

        Returns:
            str: The Population of the country
            
        Raises:
            ValueError: If the favorites list is empty or the country name is invalid.
        """
        
        self.check_if_empty()
        name = self.validate_name(name)
        logger.info(f"Retrieving population information for country: {name}")
        
        country = self.get_country(name)
        logger.info(f"Population for {name}: {country.population}")
        
        return country.population
    
    def get_region_of_favorite(self, name: str) -> str:
        """ Returns the region of a country in favorites.

        Args:
            name (str): The name of the Country 

        Returns:
            str: The Region of the country
            
        Raises:
            ValueError: If the favorites list is empty or the country name is invalid.
        """
        
        self.check_if_empty()
        name = self.validate_name(name)
        logger.info(f"Retrieving region information for country: {name}")
        
        country = self.get_country(name)    
        logger.info(f"Region for {name}: {country.region}")
        
        return country.region
    
    def get_flag_of_favorite(self, name: str) -> str:
        """ Returns the flag of a country in favorites.

        Args:
            name (str): The name of the Country 

        Returns:
            str: The Flag of the country
            
        Raises:
            ValueError: If the favorites list is empty or the country name is invalid.
        """
        
        self.check_if_empty()
        name = self.validate_name(name)
        logger.info(f"Retrieving flag information for country: {name}")
        
        country = self.get_country(name)
        if not country.flag_url:
            logger.warning(f"Country {name} has no flag image uploaded.")
            return "No flag image available for this country."
        
        logger.info(f"Flag for {name}: {country.flag_url}")
        return country.flag_url
    

    ##################################################
    # Comparing Two Countries 
    ##################################################
    
    def compare_two_favorites(self, country1_name: str, country2_name: str) -> dict:
        """
        Compare two favorite countries and return key differences.
        
        Args:
            country1_name (str): The name of the first country.
            country2_name (str): The name of the second country.

        Returns:
            dict: Dictionary with comparison results.
        """
        if country1_name not in self.favorites or country2_name not in self.favorites:
            raise ValueError("Both countries must be in favorites to compare.")

        country1 = self.get_country(country1_name)
        country2 = self.get_country(country2_name)
        
        logger.info(f"Comparing countries: {country1.name} and {country2.name}")

        return {
            "countries": (country1.name, country2.name),
            "population_difference": abs(country1.population - country2.population),
            "shared_languages": list(set(country1.languages) & set(country2.languages)),
            "shared_currencies": list(set(country1.currencies) & set(country2.currencies)),
            "regions": (country1.region, country2.region),
            "flags": (country1.flag_url or "No flag available", country2.flag_url or "No flag available"),
        }
    
    ##################################################
    # Favorites Movement Functions
    ##################################################

    def go_to_country_list_number(self, country_list_number: int) -> None:
        """Sets the country list number specified to the first spot.

        Args:
            country_list_number (int): The country_list number to set as the current country_list.

        Raises:
            ValueError: If the favorites is empty or the country_list number is invalid.

        """
        self.check_if_empty()
        
        if not self.is_valid_country_list_number(country_list_number):
            raise ValueError(f"Invalid country list number: {country_list_number}")
    
        logger.info(f"Setting favorite country number to {country_list_number}")
        self.favorite_country_int = country_list_number

    # Delete this one, don't add to unit tests
    # def go_to_random_country_list(self) -> None:
    #     """Sets the favorite country list number to a randomly selected country in favorites.

    #     Raises:
    #         ValueError: If the favorites is empty.

    #     """
    #     self.check_if_empty()

    #     # Get a random index using the random.org API
    #     random_country_list = get_random(self.get_favorites_length())

    #     logger.info(f"Setting current country_list number to random country_list: {random_country_list}")
    #     self.current_country_list_number = random_country_list

    def move_country_to_top(self, name: str) -> None:
        """Moves a country to the top of the favorites list .

        Args:
            name (int): The name of the country to move.
       
        Raises:
            ValueError: If the favorites list is empty or the country name is invalid.

        """
        logger.info(f"Moving country with name {name} to the top of the favorites list")
        self.check_if_empty()
        name = self.validate_name(name)

        self.favorites.remove(name)
        self.favorites.insert(0, name)

        logger.info(f"Successfully moved country with name {name} to the top")

    def move_country_to_bottom(self, name: str) -> None:
        """Moves a country to the bottom of the favorites list.

        Args:
            name (int): The name of the country to move.

        Raises:
            ValueError: If the favorites list is empty or the country name is invalid.

        """
        logger.info(f"Moving country with name {name} to the bottom of the favorites list")
        self.check_if_empty()
        name = self.validate_name(name)

        self.favorites.remove(name)
        self.favorites.append(name)

        logger.info(f"Successfully moved country with name {name} to the bottom of the favorites list")

    def move_country_to_country_list_number(self, name: str, country_list_number: int) -> None:
        """Moves a country to a specific country list number in the favorites list.

        Args:
            name (str): The name of the country to move.
            country_list_number (int): The country list number to move the country to (1-indexed).

        Raises:
            ValueError: If the favorites list is empty, the country name is invalid, or the country list number is out of range.

        """
        logger.info(f"Moving country with name {name} to country list number {country_list_number}")
        self.check_if_empty()
        name = self.validate_name(name)
        if not self.is_valid_country_list_number(country_list_number):
            raise ValueError(f"Invalid country list number: {country_list_number}")
        
        favorites_index = country_list_number - 1

        self.favorites.remove(name)
        self.favorites.insert(favorites_index, name)

        logger.info(f"Successfully moved country with name {name} to country_list number {country_list_number}")


    ##################################################
        # Validation Functions
    ##################################################

    def validate_name(self, name: str, check_in_favorites: bool = True) -> str:
        """
            Validates the given name.

            Args:
                name (str): The name to validate.
                check_in_favorites (bool, optional): If True, verifies the name is present in favorites.
                                                    If False, skips that check. Defaults to True.

            Returns:
                str: The validated name.

            Raises:
                ValueError: If the name is not found in favorites (if check_in_favorites=True),
                            or not found in the database
                            ???or not found in API call???.
        """
        if check_in_favorites and name not in self.favorites:
            logger.error(f"Country with name {name} not found in favorites")
            raise ValueError(f"Song with id {name} not found in favorites")

        try:
            self.get_country(name)
        except Exception as e:
            logger.error(f"Country with name {name} not found in database: {e}")
            raise ValueError(f"Country with name {name} not found in database")

        return name
    
    def validate_country_number_in_favorites(self, country_list_number: int) -> int:
        """
        Validates the given country list number in favorites, ensuring it is within the favorites range.

        Args:
            country_list_number (int): The list number to validate.

        Returns:
            int: The validated country list number.

        Raises:
            ValueError: If the country list number is not a valid positive integer or is out of range.

        """
        try:
            country_list_number = int(country_list_number)
            if not (1 <= country_list_number <= self.get_favorites_length()):
                raise ValueError(f"Invalid list number: {country_list_number}")
        except ValueError as e:
            logger.error(f"Invalid list number: {country_list_number}")
            raise ValueError(f"Invalid list number: {country_list_number}") from e

        return country_list_number
    
    def check_if_empty(self) -> None:
        """
        Checks if favorites is empty and raises a ValueError if it is.

        Raises:
            ValueError: If favorites is empty.

        """
        if not self.favorites:
            logger.error("Favorites is empty")
            raise ValueError("Favorites is empty")
        
    def is_valid_country_list_number(self, country_list_number: int) -> bool:
        """
        Checks if the given country list number is valid (within the range of the favorites list).

        Args:
            country_list_number (int): The list number to check (1-indexed).

        Returns:
            bool: True if valid, False otherwise.
        """
        return 1 <= country_list_number <= len(self.favorites)

