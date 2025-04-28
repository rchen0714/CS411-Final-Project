import logging
from typing import List, Optional
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from country.db import db
from country.utils.logger import configure_logger
# from country.utils.api_utils import get_random # Call to api, probably need more


logger = logging.getLogger(__name__)
configure_logger(logger)

class CountryData(db.Model):
    """Represents a country in the List.

    This model maps to the 'country' table and stores metadata such as name, capital,
    region, population, languages, currencies, borders, and flag URL. It also tracks play count.  --change
    
    Used in a Flask-SQLAlchemy application for playlist (favorites) management,
    user interaction, and data-driven country (country) operations.
    """
    
    ### continue
    
    __tablename__ = "CountryData"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    capital = db.Column(db.String, nullable=False)
    region = db.Column(db.String, nullable=False)
    population = db.Column(db.Integer, nullable=False)
    languages = db.Column(db.PickleType, nullable=False)  # Or JSON if supported
    currencies = db.Column(db.PickleType, nullable=False)
    borders = db.Column(db.PickleType, nullable=True)
    flag_url = db.Column(db.String, nullable=True)
    timezones = db.Column(db.PickleType, nullable=False)
    
    def validate(self) -> None:
        """Validates the country instance before committing to the database.

        Raises:
            ValueError: If any required fields are invalid.
        """
        if not self.name or not isinstance(self.name, str):
            raise ValueError("Country name must be a non-empty string.")
        if not self.capital or not isinstance(self.capital, str):
            raise ValueError("Capital must be a non-empty string.")
        if not self.region or not isinstance(self.region, str):
            raise ValueError("Region must be a non-empty string.")
        if not isinstance(self.population, int) or self.population <= 0:
            raise ValueError("Population must be a positive integer.")
        if not isinstance(self.languages, list) or len(self.languages) == 0 or not all(isinstance(lang, str) for lang in self.languages):
            raise ValueError("Languages must be a non-empty list of strings.")
        if not isinstance(self.currencies, list) or len(self.currencies) == 0 or not all(isinstance(currency, str) for currency in self.currencies):
            raise ValueError("Currencies must be a non-empty list of strings.")
        if self.borders is not None:
            if not isinstance(self.borders, list) or not all(isinstance(border, str) for border in self.borders):
                raise ValueError("Borders must be a list of strings if provided.")
        if self.flag_url is not None and not isinstance(self.flag_url, str):
            raise ValueError("Flag URL must be a string if provided.")
        if not isinstance(self.timezones, list) or len(self.timezones) == 0 or not all(isinstance(timezone, str) for timezone in self.timezones):
            raise ValueError("Timezones must be a non-empty list of strings.")


    @classmethod
    def create_country(cls, name: str, capital: str, region: str, population: int, languages: List[str], 
                       currencies: List[str], borders: List[str] | None, flag_url: Optional[str], timezones: List[str]) -> None:
        """
        Creates a new country in the countries table using SQLAlchemy.

        Args:
            name (str): The name of the country.
            capital (str): The capital city of the country.
            region (str): The geographic region where the country is located.
            population (int): The population of the country.
            languages (List[str]): A list of languages spoken in the country.
            currencies (List[str]): A list of the country's official currencies.
            borders (List[str] | None): A list of neighboring country codes (if applicable).
            flag_url (str | None): A URL to the country's flag image.
            timezones (List[str]): A list of timezones for the country.

        Raises:
            ValueError: If any field is invalid or if a country with the same name already exists.
            SQLAlchemyError: For any other database-related issues.
        """
        logger.info(f"Received request to create country: {name}")

        try:
            country = CountryData(
                name=name.strip(),
                capital=capital.strip(),
                region=region.strip(),
                population=population,
                languages=languages,
                currencies=currencies,
                borders=borders,              # Optional
                flag_url=flag_url,             # Optional
                timezones=timezones
            )
            country.validate()
        except ValueError as e:
            logger.warning(f"Validation failed: {e}")
            raise

        try:
            # Check for existing country with same name
            existing = CountryData.query.filter_by(name=name).first()
            if existing:
                logger.error(f"Country already exists: {name}")
                raise ValueError(f"Country with name '{name}' already exists.")

            db.session.add(country)
            db.session.commit()
            logger.info(f"Country successfully added: {name}")

        except IntegrityError:
            logger.error(f"Country already exists: {name}")
            db.session.rollback()
            raise ValueError(f"Country with name '{name}' already exists.")

        except SQLAlchemyError as e:
            logger.error(f"Database error while creating country: {e}")
            db.session.rollback()
            raise

    @classmethod
    def delete_country(cls, name: str) -> None:
        """
        Permanently deletes a country from the catalog by name.

        Args:
            name (str): The name of the country to delete.

        Raises:
            ValueError: If the country with the given name does not exist.
            SQLAlchemyError: For any database-related issues.
        """
        logger.info(f"Received request to delete country with name {name}")

        try:
            country = cls.query.filter_by(name=name).first()
            if not country:
                logger.warning(f"Attempted to delete non-existent country with name {name}")
                raise ValueError(f"Country with name {name} not found")

            db.session.delete(country)
            db.session.commit()
            logger.info(f"Successfully deleted country with name {name}")

        except SQLAlchemyError as e:
            logger.error(f"Database error while deleting country with name {name}: {e}")
            db.session.rollback()
            raise

    @classmethod
    def get_country_by_name(cls, name: str) -> "CountryData":
        """
        Retrieves a country from the catalog by its name.

        Args:
            name (str): The name of the country to retrieve.

        Returns:
            CountryData: The country instance corresponding to the name.

        Raises:
            ValueError: If no country with the given name is found.
            SQLAlchemyError: If a database error occurs.
        """
        logger.info(f"Attempting to retrieve country with name {name}")

        try:
            country = cls.query.filter_by(name=name).first()

            if not country:
                logger.info(f"Country with name {name} not found")
                raise ValueError(f"Country with name {name} not found")

            logger.info(f"Successfully retrieved country: {country.name}")
            return country

        except SQLAlchemyError as e:
            logger.error(f"Database error while retrieving country by name {name}: {e}")
            raise
            
    @classmethod
    def get_all_countries(cls, sort_by_population: bool = False) -> list[dict]:
        """
        Retrieves all countries from the catalog as dictionaries.

        Args:
            sort_by_population (bool): If True, sort the countries by population in descending order.
        Returns:
            list[dict]: A list of dictionaries representing all countries in database.

        Raises:
            SQLAlchemyError: If any database error occurs.
        """
        logger.info("Attempting to retrieve all countries from the catalog")

        try:
            query = cls.query
            if sort_by_population:
                query = query.order_by(cls.population.desc())

            countries = query.all()

            if not countries:
                logger.warning("The country catalog is empty.")
                return []

            results = [
                {
                    "id": country.id,
                    "name": country.name,
                    "capital": country.capital,
                    "region": country.region,
                    "population": country.population,
                    "languages": country.languages,
                    "currencies": country.currencies,
                    "borders": country.borders,
                    "flag_url": country.flag_url,
                    "timezones": country.timezones,
                }
                for country in countries
            ]

            logger.info(f"Retrieved {len(results)} countries from the catalog")
            return results

        except SQLAlchemyError as e:
            logger.error(f"Database error while retrieving all countries: {e}")
            raise


    
