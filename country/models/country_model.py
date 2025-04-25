import logging

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from country.db import db
from country.utils.logger import configure_logger
from country.utils.api_utils import get_random # Call to api, probably need more


logger = logging.getLogger(__name__)
configure_logger(logger)

class CountryData(db.Model):
    """Represents a country in the List.

    This model maps to the 'songs' table and stores metadata such as artist, --change
    title, genre, release year, and duration. It also tracks play count.  --change

    Used in a Flask-SQLAlchemy application for playlist (favorites) management,  --change, probably
    user interaction, and data-driven song (country) operations. --change, probably
    """
    
    __tablename__ = "Country"
    
    ### continue