import pytest
import requests
from app import create_app
from config import TestConfig
from unittest import mock
from country.utils.api_utils import fetch_country_by_name, get_or_fetch_country, fetch_countries_by_language, fetch_random_country, fetch_countries_by_region
from country.models.country_model import CountryData

@pytest.fixture
def test_app():
    app = create_app(TestConfig)
    with app.app_context():
        yield app

@pytest.fixture
def mock_country_response():
    """Mock country response from the API."""
    mock_response = {
        "name": {"common": "Testland"},
        "capital": ["Test City"],
        "region": "Test Region",
        "population": 1234567,
        "languages": {"eng": "English"},
        "currencies": {"USD": {"name": "US Dollar"}},
        "borders": ["Testland Border"],
        "flags": {"png": "http://testflag.png"},
        "timezones": ["UTC"]
    }
    return mock_response


def test_fetch_country_by_name(mock_country_response):
    """Test fetching country by name."""
    with mock.patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = [mock_country_response]
        
        country = fetch_country_by_name("Testland")
        
        assert country.name == "Testland"
        assert country.capital == "Test City"
        assert country.region == "Test Region"


def test_get_or_fetch_country(test_app, mock_country_response):
    """Test getting or fetching a country from the DB."""
    with test_app.app_context():
        with mock.patch('requests.get') as mock_get, \
            mock.patch('country.db.db.session.add') as mock_add, \
            mock.patch('country.db.db.session.commit') as mock_commit:
            
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = [mock_country_response]
            
            # Mock a DB query to return None (i.e., country not found)
            with mock.patch('country.utils.api_utils.CountryData.query.filter_by') as mock_filter:
                mock_filter.return_value.first.return_value = None

                # Mock the save to the database by adding it and committing it
                country = get_or_fetch_country("Testland")
            
            # Assert that the fetched country matches
            assert country.name == "Testland"
            
            # Ensure that the country was saved to the database
            mock_add.assert_called_once()
            mock_commit.assert_called_once()


def test_fetch_countries_by_language(mock_country_response):
    """Test fetching countries by language."""
    with mock.patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = [mock_country_response]
        
        countries = fetch_countries_by_language("English")
        
        assert len(countries) > 0
        assert countries[0].name == "Testland"
        
def test_fetch_countries_by_region(mock_country_response):
    """Test fetching a country by region"""
    
    with mock.patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = [mock_country_response]
        
        countries = fetch_countries_by_region("Test Region")
        
        assert len(countries) > 0
        assert countries[0].name == "Testland"
        assert countries[0].region == "Test Region"


def test_fetch_random_country(mock_country_response):
    """Test fetching a random country."""
    with mock.patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = [mock_country_response]
        
        random_country = fetch_random_country()
        
        assert random_country.name == "Testland"


def test_get_country_from_cache_or_db(test_app, mock_country_response):
    """Test if the country is fetched from cache or the database."""
    with test_app.app_context():
        with mock.patch('requests.get') as mock_get, \
             mock.patch('country.utils.api_utils.CountryData.query') as mock_query:

            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = [mock_country_response]

            # Correct patching of filter_by → first()
            mock_query.filter_by.return_value.first.return_value = None

            # Call the function
            country = get_or_fetch_country("Testland")

            # Assertions
            assert country.name == "Testland"
            mock_query.filter_by.assert_called_once_with(name="Testland")
            
            

