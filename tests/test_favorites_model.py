import pytest
from country.models.favorites_model import FavoritesModel
from country.models.country_model import CountryData

@pytest.fixture
def favorites_model():
    """Provides a fresh instance of FavoritesModel for each test."""
    return FavoritesModel()

@pytest.fixture
def country_usa():
    """Sample CountryData object for mocking."""
    return CountryData(
        name="United States",
        capital="Washington, D.C.",
        region="Americas",
        population=331000000,
        area_km2=9833517,
        languages=["English"],
        currencies=["USD"],
        borders=["CAN", "MEX"],
        flag_url="https://example.com/flag_usa.png",
        timezones=["UTC-5"]
    )


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

def test_add_favorite(favorites_model):
    favorites_model.add_favorite("United States")
    assert "United States" in favorites_model.list_favorites()

def test_remove_favorite(favorites_model):
    favorites_model.add_favorite("United States")
    favorites_model.remove_favorite("United States")
    assert "United States" not in favorites_model.list_favorites()

def test_add_duplicate_favorite_only_once(favorites_model):
    favorites_model.add_favorite("United States")
    favorites_model.add_favorite("United States")
    assert favorites_model.list_favorites().count("United States") == 1

