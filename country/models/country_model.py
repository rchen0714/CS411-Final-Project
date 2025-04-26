import logging

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from country.db import db
from country.utils.logger import configure_logger
# from country.utils.api_utils import get_random # Call to api, probably need more


logger = logging.getLogger(__name__)
configure_logger(logger)

class CountryData(db.Model):
    """Represents a country in the List.

    This model maps to the 'songs' table and stores metadata such as artist, --change
    title, genre, release year, and duration. It also tracks play count.  --change
    
    Used in a Flask-SQLAlchemy application for playlist (favorites) management,  --change, probably
    user interaction, and data-driven song (country) operations. --change, probably
    """
    
    ### continue
    
    __tablename__ = "CountryData"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    capital = db.Column(db.String, nullable=False)
    region = db.Column(db.String, nullable=False)
    population = db.Column(db.Integer, nullable=False)
    area_km2 = db.Column(db.Float, nullable=False)
    languages = db.Column(db.PickleType, nullable=False)  # Or JSON if supported
    currencies = db.Column(db.PickleType, nullable=False)
    borders = db.Column(db.PickleType, nullable=True)
    flag_url = db.Column(db.String, nullable=True)
    timezones = db.Column(db.PickleType, nullable=False)
    
    # def validate(self):
    #     """Validate the country data before saving."""
    #     if not self.name or not isinstance(self.name, str):
    #         raise ValueError("Country name must be a non-empty string.")
    #     if not isinstance(self.population, int) or self.population < 0:
    #         raise ValueError("Population must be a non-negative integer.")
    #     if not isinstance(self.area_km2, (float, int)) or self.area_km2 < 0:
    #         raise ValueError("Area must be a non-negative number.")