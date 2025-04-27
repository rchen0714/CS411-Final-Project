# pytest tests/test_favorites_model.py

from unittest import mock
import pytest
from country.models.favorites_model import FavoritesModel
from country.models.country_model import CountryData

@pytest.fixture
def favorites_model():
    """Provides a fresh instance of FavoritesModel for each test."""
    return FavoritesModel()

""" Fixtures providing sample CountryData objects for tests"""
@pytest.fixture
def country_usa(session):
    """Fixture for a USA country."""
    country = CountryData(
        name="United States",
        capital="Washington, D.C.",
        region="Americas",
        population=331000000,
        languages=["English"],
        currencies=["USD"],
        borders=["CAN", "MEX"],
        flag_url="https://example.com/flag_usa.png",
        timezones=["UTC-5"]
    )
    session.add(country)
    session.commit()
    return country

@pytest.fixture
def country_cananda(session):
    """Fixture for a Canada country."""
    country = CountryData(
        name="Canada",
        capital="Ottawa",
        region="Americas",
        population=38000000,
        languages=["English", "French"],
        currencies=["CAD"],
        borders=["USA"],
        flag_url="https://example.com/flag_canada.png",
        timezones=["UTC-5"]
    )
    session.add(country)
    session.commit()
    return country

@pytest.fixture
def sample_favorites(country_usa, country_cananda):
    """Fixture for a sample favorites list."""
    return [country_usa, country_cananda]

##############################################################
# Favorites API Test Cases
##############################################################

# This test might be better suited for api_utils tests
def test_get_country_calls_api_utils(favorites_model, country_usa, mocker):
    """Test that FavoritesModel calls get_country_with_cache properly."""
    mock_get_cache = mocker.patch(
    "country.models.favorites_model.get_country_with_cache",
    return_value=country_usa
    )
    
    country = favorites_model.get_country("United States")
    
    mock_get_cache.assert_called_once_with(
        "United States",
        favorites_model._country_cache,
        favorites_model._ttl,
        favorites_model.ttl_seconds
    )
    assert country.name == "United States"

##############################################################
# Add / Remove from Favorites Test Cases
##############################################################

def test_add_country_to_favorites(favorites_model, country_usa, mocker):
    """Test adding a country to the favorites."""
    mocker.patch(
        "country.models.favorites_model.get_country_with_cache",
        return_value=country_usa
    )
    favorites_model.add_country_to_favorites("United States")
    assert len(favorites_model.favorites) == 1
    assert favorites_model.favorites[0] == "United States"
    

def test_add_duplicate_country_to_favorites(favorites_model, country_usa, mocker):
    """Test error when adding a duplicate country to the favorites by name."""
    mocker.patch(
        "country.models.favorites_model.get_country_with_cache",
        side_effect=[country_usa] * 2
    )
    favorites_model.add_country_to_favorites("United States")
    with pytest.raises(ValueError, match="Country with name 'United States' already exists in the favorites"):
        favorites_model.add_country_to_favorites("United States")


def test_remove_country_from_favorites_by_name(favorites_model, mocker):
    """Test removing a country from the favorites by name."""
    mocker.patch(
        "country.models.favorites_model.get_country_with_cache",
        return_value=country_usa
    )
    favorites_model.favorites = ["United States", "Canada"]

    favorites_model.remove_favorite("United States")
    assert len(favorites_model.favorites) == 1, f"Expected 1 country, but got {len(favorites_model.favorites)}"
    assert favorites_model.favorites[0] == "Canada", "Expected country with id 2 to remain"


def test_remove_country_by_country_list_number(favorites_model):
    """Test removing a country from the favorites by country list number."""
    favorites_model.favorites = ["United States", "Canada"]
    assert len(favorites_model.favorites) == 2

    favorites_model.remove_country_by_country_list_number(1)
    assert len(favorites_model.favorites) == 1, f"Expected 1 country, but got {len(favorites_model.favorites)}"
    assert favorites_model.favorites[0] == "Canada", "Expected 'Canada' to remain"


def test_clear_favorites(favorites_model):
    """Test clearing the entire favorites."""
    favorites_model.favorites.append("United States")

    favorites_model.clear_favorites()
    assert len(favorites_model.favorites) == 0, "Playlist should be empty after clearing"
