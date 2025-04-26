import pytest
import requests
from unittest import mock
from country.utils.api_utils import fetch_country_by_name, get_or_fetch_country, fetch_countries_by_language, fetch_random_country
from country.models.country_model import CountryData


@pytest.fixture
def mock_country_response():
    """Mock country response from the API."""
    mock_response = {
        "name": {"common": "Testland"},
        "capital": ["Test City"],
        "region": "Test Region",
        "population": 1234567,
        "area": 1000.0,
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


def test_get_or_fetch_country(mock_country_response):
    """Test getting or fetching a country from the DB."""
    with mock.patch('requests.get') as mock_get, \
         mock.patch('country.db.db.session.add') as mock_add, \
         mock.patch('country.db.db.session.commit') as mock_commit:
        
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = [mock_country_response]
        
        # Mock a DB query to return None (i.e., country not found)
        with mock.patch('country.models.country_model.CountryData.query.filter_by') as mock_filter:
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


def test_fetch_random_country(mock_country_response):
    """Test fetching a random country."""
    with mock.patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = [mock_country_response]
        
        random_country = fetch_random_country()
        
        assert random_country.name == "Testland"


def test_get_country_from_cache_or_db(mock_country_response):
    """Test if the country is fetched from cache or the database."""
    with mock.patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = [mock_country_response]

        # Mocking the database query
        with mock.patch('country.models.country_model.CountryData.query.filter_by') as mock_filter:
            mock_filter.return_value.first.return_value = None  # Simulate country not found in DB

            # Call the function
            country = get_or_fetch_country("Testland")

        # Assert country fetched correctly
        assert country.name == "Testland"
        
        # Make sure that we mocked the database interactions properly
        mock_filter.assert_called_once()
