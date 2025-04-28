# pytest tests/test_country_model.py
import pytest

from country.models.country_model import CountryData


# --- Fixtures ---

@pytest.fixture
def country_usa(session):
    """Fixture for USA country object."""
    country_usa = CountryData(name='United States', capital='Washington, D.C.', region='Americas', population=331000000, languages=['English'], currencies=['USD'], borders=['CAN', 'MEX'], flag_url='https://example.com/flag_usa.png', timezones=['UTC-5'])
    session.add(country_usa)
    session.commit()
    return country_usa

@pytest.fixture
def country_canada(session):
    """Fixture for Canada country object."""
    country_canada = CountryData(name='Canada', capital='Ottawa', region='Americas', population=38000000, languages=['English', 'French'], currencies=['CAD'], borders=['USA'], flag_url='https://example.com/flag_canada.png', timezones=['UTC-5'])
    session.add(country_canada)
    session.commit()
    return country_canada


# --- Create Country ---

def test_create_country(session):
    """Test creating a new country."""
    CountryData.create_country("United States", "Washington, D.C.", "Americas", 331000000, ["English"], ["USD"], ["CAN", "MEX"], "https://example.com/flag_usa.png", ["UTC-5"])
    country = session.query(CountryData).filter_by(name="United States").first()
    assert country is not None
    assert country.name == "United States"


def test_create_duplicate_country(session, country_usa):
    """Test creating a country with a duplicate name."""
    with pytest.raises(ValueError, match="already exists"):
        CountryData.create_country(
            "United States",
            "Washington, D.C.",
            "Americas",
            331000000,
            ["English"],
            ["USD"],
            ["CAN", "MEX"],
            "https://example.com/flag_usa.png",
            ["UTC-5"]
        )


@pytest.mark.parametrize(
    "name, capital, region, population, languages, currencies, borders, flag_url, timezones",
    [
        ("", "Washington, D.C.", "Americas", 331000000, ["English"], ["USD"], ["CAN", "MEX"], "https://example.com/flag.png", ["UTC-5"]),
        ("United States", "", "Americas", 331000000, ["English"], ["USD"], ["CAN", "MEX"], "https://example.com/flag.png", ["UTC-5"]),
        ("United States", "Washington, D.C.", "Americas", -100, ["English"], ["USD"], ["CAN", "MEX"], "https://example.com/flag.png", ["UTC-5"]),
        ("United States", "Washington, D.C.", "Americas", 331000000, [], ["USD"], ["CAN", "MEX"], "https://example.com/flag.png", ["UTC-5"]),
        ("United States", "Washington, D.C.", "Americas", 331000000, ["English"], [], ["CAN", "MEX"], "https://example.com/flag.png", ["UTC-5"]),
    ]
)
def test_create_country_invalid_data(app, name, capital, region, population, languages, currencies, borders, flag_url, timezones):
    """Test validation errors when creating a country with bad data."""
    with app.app_context():
        with pytest.raises(ValueError):
            CountryData.create_country(name, capital, region, population, languages, currencies, borders, flag_url, timezones)

# --- Get Country ---

def test_get_country_by_name(country_usa):
    """Test fetching a country by name."""
    fetched = CountryData.get_country_by_name("United States")
    assert fetched.name == "United States"

def test_get_country_by_name_not_found(app):
    """Test error when fetching nonexistent country by name."""
    with pytest.raises(ValueError, match="not found"):
        CountryData.get_country_by_name("InvalidCountry")


# --- Delete Country ---

def test_delete_country_by_name(session, country_usa):
    """Test deleting a country by name."""
    CountryData.delete_country("United States")
    assert session.query(CountryData).filter_by(name="United States").first() is None


def test_delete_country_not_found(app):
    """Test deleting a non-existent country by name."""
    with pytest.raises(ValueError, match="not found"):
        CountryData.delete_country("InvalidCountry")


# --- Get All CountryData ---

def test_get_all_countries(session, country_usa, country_canada):
    """Test retrieving all countries."""
    countries = CountryData.get_all_countries()
    assert len(countries) == 2

def test_get_all_countries_sorted(session, country_usa, country_canada):
    """Test retrieving countries sorted by population."""
    
    session.commit()
    sorted_countries = CountryData.get_all_countries(sort_by_population=True)
    assert sorted_countries[0]["population"] == 331000000
    assert sorted_countries[1]["population"] == 38000000
