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
def country_canada(session):
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
def sample_favorites(country_usa, country_canada):
    """Fixture for a sample favorites list."""
    return [country_usa, country_canada]

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

##################################################
# Tesing Country Retrieval Functions
##################################################

def test_get_all_countries_returns_list(favorites_model, country_usa, country_canada, mocker):
    """Test get_all_countries returns a list of CountryData objects."""
    
    def mimick_cache(name, cache=None, ttl=None, ttl_seconds=60):
        if name == "United States":
            return country_usa
        elif name == "Canada":
            return country_canada
        else:
            return ValueError("Unknown country")
        
    mocker.patch(
        "country.models.favorites_model.get_country_with_cache", 
        side_effect=mimick_cache
    )
    favorites_model.favorites = ["United States", "Canada"]
    result = favorites_model.get_all_countries()
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0].name == "United States"
    assert result[1].name == "Canada"

def test_get_country_by_name(favorites_model, country_usa, mocker):
    """Test get_country_by_name returns the correct country object."""
    mocker.patch(
        "country.models.favorites_model.get_country_with_cache", 
        return_value=country_usa
    )
    favorites_model.favorites = ["United States"]
    result = favorites_model.get_country_by_name("United States")
    assert isinstance(result, CountryData)
    assert result.name == "United States"
    
def test_get_country_by_country_list_number(favorites_model, country_canada, mocker):
    """Test retrieving a country by its list number (1-indexed)."""
    mocker.patch(
        "country.models.favorites_model.get_country_with_cache", 
        return_value=country_canada
    )
    favorites_model.favorites = ["Canada"]
    result = favorites_model.get_country_by_country_list_number(1)
    
    assert isinstance(result, CountryData)
    assert result.name == "Canada"


##############################################################
# Get Info of Favorite Test Cases
##############################################################

def test_get_currency_favorite(favorites_model, sample_favorites):
    """Test getting the currency of a favorite."""
    favorites_model.favorites = [country.name for country in sample_favorites]
    
    assert favorites_model.get_currency_of_favorite("United States") == "USD"
    assert favorites_model.get_currency_of_favorite("Canada") == "CAD"
    
def test_get_languages_of_favorite(favorites_model, sample_favorites):
    """Test getting the languages of a favorite."""
    favorites_model.favorites = [country.name for country in sample_favorites]
    
    assert favorites_model.get_languages_of_favorite("United States") == "English"
    assert favorites_model.get_languages_of_favorite("Canada") == "English, French"
    
def test_get_borders_of_favorite(favorites_model, sample_favorites):
    """Test getting the borders of a favorite."""
    favorites_model.favorites = [country.name for country in sample_favorites]
    
    assert favorites_model.get_borders_of_favorite("United States") == "CAN, MEX"
    assert favorites_model.get_borders_of_favorite("Canada") == "USA"
    
def test_get_population_of_favorite(favorites_model, sample_favorites):
    """Test getting the population of a favorite."""
    favorites_model.favorites = [country.name for country in sample_favorites]
    
    assert favorites_model.get_population_of_favorite("United States") == 331000000
    assert favorites_model.get_population_of_favorite("Canada") == 38000000
    
def test_get_region_of_favorite(favorites_model, sample_favorites):
    """Test getting the region of a favorite."""
    favorites_model.favorites = [country.name for country in sample_favorites]
    
    assert favorites_model.get_region_of_favorite("United States") == "Americas"
    assert favorites_model.get_region_of_favorite("Canada") == "Americas"
    
def test_get_flag_of_favorite(favorites_model, sample_favorites):
    """Test getting the flag URL of a favorite."""
    favorites_model.favorites = [country.name for country in sample_favorites]
    
    assert favorites_model.get_flag_of_favorite("United States") == "https://example.com/flag_usa.png"
    assert favorites_model.get_flag_of_favorite("Canada") == "https://example.com/flag_canada.png"
    
    
##############################################################
# Managing Favorite List Test Cases
##############################################################



##############################################################
# Test case for comparing two countries 
##############################################################

def test_compare_two_favorites(favorites_model, sample_favorites):
    """Test comparing two favorites."""
    favorites_model.favorites = [country.name for country in sample_favorites]
    comparison = favorites_model.compare_two_favorites("United States", "Canada")
    
    assert comparison["countries"] == ("United States", "Canada")
    assert "population_difference" in comparison
    assert "shared_languages" in comparison
    assert "shared_currencies" in comparison
    assert "regions" in comparison
    assert "flags" in comparison

##############################################################
# Moving Favorites test cases
##############################################################

def test_move_country_to_top(favorites_model, sample_favorites):
    """Test moving a country to the top of the favorites list."""
    favorites_model.favorites = [country.name for country in sample_favorites]
    favorites_model.move_country_to_top("Canada")
    
    assert favorites_model.favorites[0] == "Canada"

def test_move_country_to_bottom(favorites_model, sample_favorites):
    """Test moving a country to the bottom of the favorites list."""
    favorites_model.favorites = [country.name for country in sample_favorites]
    favorites_model.move_country_to_bottom("United States")
    
    assert favorites_model.favorites[-1] == "United States"
    
def test_move_country_to_country_list_number(favorites_model, sample_favorites):
    """Test moving a country to a specific position in the favorites list."""
    favorites_model.favorites = [country.name for country in sample_favorites]
    favorites_model.move_country_to_country_list_number("Canada", 1)
    
    assert favorites_model.favorites[0] == "Canada"
    
def test_go_to_country_list_number(favorites_model, sample_favorites):
    """Test going to a specific position in the favorites list."""
    favorites_model.favorites = [country.name for country in sample_favorites]
    favorites_model.go_to_country_list_number(2)
    
    assert favorites_model.favorite_country_int == 2