from dotenv import load_dotenv
from flask import Flask, jsonify, make_response, Response, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

from config import ProductionConfig

from country.db import db
from country.models.country_model import CountryData
from country.models.favorites_model import FavoritesModel
from country.models.user_model import Users
from country.utils.logger import configure_logger


load_dotenv()


def create_app(config_class=ProductionConfig) -> Flask:
    """Create a Flask application with the specified configuration.

    Args:
        config_class (Config): The configuration class to use.

    Returns:
        Flask app: The configured Flask application.

    """
    app = Flask(__name__)
    configure_logger(app.logger)

    app.config.from_object(config_class)

    # Initialize database
    db.init_app(app)
    with app.app_context():
        db.create_all()

    # Initialize login manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    @login_manager.user_loader
    def load_user(user_id):
        return Users.query.filter_by(username=user_id).first()

    @login_manager.unauthorized_handler
    def unauthorized():
        return make_response(jsonify({
            "status": "error",
            "message": "Authentication required"
        }), 401)

    favorites_model = FavoritesModel()

    @app.route('/api/health', methods=['GET'])
    def healthcheck() -> Response:
        """Health check route to verify the service is running.

        Returns:
            JSON response indicating the health status of the service.

        """
        app.logger.info("Health check endpoint hit")
        return make_response(jsonify({
            'status': 'success',
            'message': 'Service is running'
        }), 200)

    ##########################################################
    #
    # User Management
    #
    #########################################################

    @app.route('/api/create-user', methods=['PUT'])
    def create_user() -> Response:
        """Register a new user account.

        Expected JSON Input:
            - username (str): The desired username.
            - password (str): The desired password.

        Returns:
            JSON response indicating the success of the user creation.

        Raises:
            400 error if the username or password is missing.
            500 error if there is an issue creating the user in the database.
        """
        try:
            data = request.get_json()
            username = data.get("username")
            password = data.get("password")

            if not username or not password:
                return make_response(jsonify({
                    "status": "error",
                    "message": "Username and password are required"
                }), 400)

            Users.create_user(username, password)
            return make_response(jsonify({
                "status": "success",
                "message": f"User '{username}' created successfully"
            }), 201)

        except ValueError as e:
            return make_response(jsonify({
                "status": "error",
                "message": str(e)
            }), 400)
        except Exception as e:
            app.logger.error(f"User creation failed: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "An internal error occurred while creating user",
                "details": str(e)
            }), 500)

    @app.route('/api/login', methods=['POST'])
    def login() -> Response:
        """Authenticate a user and log them in.

        Expected JSON Input:
            - username (str): The username of the user.
            - password (str): The password of the user.

        Returns:
            JSON response indicating the success of the login attempt.

        Raises:
            401 error if the username or password is incorrect.
        """
        try:
            data = request.get_json()
            username = data.get("username")
            password = data.get("password")

            if not username or not password:
                return make_response(jsonify({
                    "status": "error",
                    "message": "Username and password are required"
                }), 400)

            if Users.check_password(username, password):
                user = Users.query.filter_by(username=username).first()
                login_user(user)
                return make_response(jsonify({
                    "status": "success",
                    "message": f"User '{username}' logged in successfully"
                }), 200)
            else:
                return make_response(jsonify({
                    "status": "error",
                    "message": "Invalid username or password"
                }), 401)

        except ValueError as e:
            return make_response(jsonify({
                "status": "error",
                "message": str(e)
            }), 401)
        except Exception as e:
            app.logger.error(f"Login failed: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "An internal error occurred during login",
                "details": str(e)
            }), 500)

    @app.route('/api/logout', methods=['POST'])
    @login_required
    def logout() -> Response:
        """Log out the favorite user.

        Returns:
            JSON response indicating the success of the logout operation.

        """
        logout_user()
        return make_response(jsonify({
            "status": "success",
            "message": "User logged out successfully"
        }), 200)

    @app.route('/api/change-password', methods=['POST'])
    @login_required
    def change_password() -> Response:
        """Change the password for the favorite user.

        Expected JSON Input:
            - new_password (str): The new password to set.

        Returns:
            JSON response indicating the success of the password change.

        Raises:
            400 error if the new password is not provided.
            500 error if there is an issue updating the password in the database.
        """
        try:
            data = request.get_json()
            new_password = data.get("new_password")

            if not new_password:
                return make_response(jsonify({
                    "status": "error",
                    "message": "New password is required"
                }), 400)

            username = current_user.username
            Users.update_password(username, new_password)
            return make_response(jsonify({
                "status": "success",
                "message": "Password changed successfully"
            }), 200)

        except ValueError as e:
            return make_response(jsonify({
                "status": "error",
                "message": str(e)
            }), 400)
        except Exception as e:
            app.logger.error(f"Password change failed: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "An internal error occurred while changing password",
                "details": str(e)
            }), 500)

    @app.route('/api/reset-users', methods=['DELETE'])
    def reset_users() -> Response:
        """Recreate the users table to delete all users.

        Returns:
            JSON response indicating the success of recreating the Users table.

        Raises:
            500 error if there is an issue recreating the Users table.
        """
        try:
            app.logger.info("Received request to recreate Users table")
            with app.app_context():
                Users.__table__.drop(db.engine)
                Users.__table__.create(db.engine)
            app.logger.info("Users table recreated successfully")
            return make_response(jsonify({
                "status": "success",
                "message": f"Users table recreated successfully"
            }), 200)

        except Exception as e:
            app.logger.error(f"Users table recreation failed: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "An internal error occurred while deleting users",
                "details": str(e)
            }), 500)

    ##########################################################
    #
    # CountryData
    #
    ##########################################################

    @app.route('/api/reset-countries', methods=['DELETE'])
    def reset_countries() -> Response:
        """Recreate the countries table to delete countries.

        Returns:
            JSON response indicating the success of recreating the CountryData table.

        Raises:
            500 error if there is an issue recreating the CountryData table.
        """
        try:
            app.logger.info("Received request to recreate CountryData table")
            with app.app_context():
                CountryData.__table__.drop(db.engine)
                CountryData.__table__.create(db.engine)
            app.logger.info("CountryData table recreated successfully")
            return make_response(jsonify({
                "status": "success",
                "message": f"CountryData table recreated successfully"
            }), 200)

        except Exception as e:
            app.logger.error(f"CountryData table recreation failed: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "An internal error occurred while deleting users",
                "details": str(e)
            }), 500)


    @app.route('/api/create-country', methods=['POST'])
    @login_required
    def add_country() -> Response:
        """Route to add a new country to the database.

        Expected JSON Input:
            name (str): The name of the country.
            capital (str): The capital city of the country.
            region (str): The geographic region where the country is located.
            population (int): The population of the country.
            languages (list[str]): A list of languages spoken in the country.
            currencies (list[str]): A list of the country's official currencies.
            borders (list[str] | None): A list of neighboring country codes (if applicable).
            flag_url (str | None): A URL to the country's flag image.
            timezones (list[str]): A list of timezones for the country.

        Returns:
            JSON response indicating the success of the country addition.

        Raises:
            400 error if input validation fails.
            500 error if there is an issue adding the country to the favorites.

        """
        app.logger.info("Received request to add a new country")

        try:
            data = request.get_json()

            required_fields = ["name", "capital", "region", "population", "languages", "currencies", "borders", "flag_url", "timezones"]
            missing_fields = [field for field in required_fields if field not in data]

            if missing_fields:
                app.logger.warning(f"Missing required fields: {missing_fields}")
                return make_response(jsonify({
                    "status": "error",
                    "message": f"Missing required fields: {', '.join(missing_fields)}"
                }), 400)

            name = data["name"]
            capital = data["capital"]
            region = data["region"]
            population = data["population"]
            languages = data["languages"]
            currencies = data["currencies"]
            borders = data["borders"]
            flag_url = data["flag_url"]
            timezones = data["timezones"]

            if (
                not isinstance(name, str)
                or not isinstance(capital, str)
                or not isinstance(region, str)
                or not isinstance(population, int)
                or not isinstance(languages, list) or not all(isinstance(lang, str) for lang in languages)
                or not isinstance(currencies, list) or not all(isinstance(curr, str) for curr in currencies)
                or not isinstance(borders, list) or not all(isinstance(border, str) for border in borders)
                or not isinstance(flag_url, str)
                or not isinstance(timezones, list) or not all(isinstance(tz, str) for tz in timezones)
            ):

                app.logger.warning("Invalid input data types")
                return make_response(jsonify({
                    "status": "error",
                    "message": "Invalid input types: name/capital/region/flag_url should be strings, population should be an integer, languages/currencies/borders/timezones should be lists of strings."
                }), 400)

            app.logger.info(f"Adding country: {name}")
            CountryData.create_country(name=name, capital=capital, region=region, population=population,
                                       languages=languages, currencies=currencies, borders=borders,
                                       flag_url=flag_url, timezones=timezones)

            app.logger.info(f"Country added successfully: {name}")
            return make_response(jsonify({
                "status": "success",
                "message": f"Country '{name} added successfully"
            }), 201)

        except Exception as e:
            app.logger.error(f"Failed to add country: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "An internal error occurred while adding the country",
                "details": str(e)
            }), 500)


    @app.route('/api/delete-country/<string:name>', methods=['DELETE'])
    @login_required
    def delete_country(name: str) -> Response:
        """Route to delete a country by name.

        Path Parameter:
            - name (str): The name of the country to delete.

        Returns:
            JSON response indicating success of the operation.

        Raises:
            400 error if the country does not exist.
            500 error if there is an issue removing the country from the database.

        """
        try:
            app.logger.info(f"Received request to delete country with name {name}")

            # Check if the country exists before attempting to delete
            country = CountryData.get_country_by_name(name)
            if not country:
                app.logger.warning(f"Country with name {name} not found.")
                return make_response(jsonify({
                    "status": "error",
                    "message": f"Country with name {name} not found"
                }), 400)

            CountryData.delete_country(name)
            app.logger.info(f"Successfully deleted country with name {name}")

            return make_response(jsonify({
                "status": "success",
                "message": f"Country with name {name} deleted successfully"
            }), 200)

        except Exception as e:
            app.logger.error(f"Failed to delete country: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "An internal error occurred while deleting the country",
                "details": str(e)
            }), 500)


    @app.route('/api/get-all-countries-from-database', methods=['GET'])
    @login_required
    def get_all_countries() -> Response:
        """Route to retrieve all countries in the database (non-deleted), with an option to sort by play count.

        Query Parameter:
            - sort_by_play_count (bool, optional): If true, sort countries by play count.

        Returns:
            JSON response containing the list of countries.

        Raises:
            500 error if there is an issue retrieving countries from the database.

        """
        try:

            app.logger.info(f"Received request to retrieve all countries from database")

            countries = CountryData.get_all_countries()

            app.logger.info(f"Successfully retrieved {len(countries)} countries from the database")

            return make_response(jsonify({
                "status": "success",
                "message": "CountryData retrieved successfully",
                "countries": countries
            }), 200)

        except Exception as e:
            app.logger.error(f"Failed to retrieve countries: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "An internal error occurred while retrieving countries",
                "details": str(e)
            }), 500)


    @app.route('/api/get-country-from-database-by-name/<string:name>', methods=['GET'])
    @login_required
    def get_country_by_name(name: str) -> Response:
        """Route to retrieve a country by its name.

        Path Parameter:
            - name (str): The name of the country.

        Returns:
            JSON response containing the country details.

        Raises:
            400 error if the country does not exist.
            500 error if there is an issue retrieving the country.

        """
        try:
            app.logger.info(f"Received request to retrieve country with name {name}")

            country = CountryData.get_country_by_name(name)
            if not country:
                app.logger.warning(f"Country with name {name} not found.")
                return make_response(jsonify({
                    "status": "error",
                    "message": f"Country with name {name} not found"
                }), 400)

            app.logger.info(f"Successfully retrieved country: {country.name}")

            return make_response(jsonify({
                "status": "success",
                "message": "Country retrieved successfully",
                "country": country.name
            }), 200)

        except Exception as e:
            app.logger.error(f"Failed to retrieve country by name: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "An internal error occurred while retrieving the country",
                "details": str(e)
            }), 500)

    ############################################################
    #
    # Favorites Add / Remove
    #
    ############################################################


    @app.route('/api/add-country-to-favorites', methods=['POST'])
    @login_required
    def add_country_to_favorites() -> Response:
        """Route to add a country to the favorites by name.

        Expected JSON Input:
            - name (str): The name of the country.

        Returns:
            JSON response indicating success of the addition.

        Raises:
            400 error if required fields are missing or the country does not exist.
            500 error if there is an issue adding the country to the favorites.

        """
        try:
            app.logger.info("Received request to add country to favorites")

            data = request.get_json()
            required_fields = ["name"]
            missing_fields = [field for field in required_fields if field not in data]

            if missing_fields:
                app.logger.warning(f"Missing required field: {missing_fields}")
                return make_response(jsonify({
                    "status": "error",
                    "message": f"Missing required fields: {', '.join(missing_fields)}"
                }), 400)

            name = data["name"]


            app.logger.info(f"Looking up country: {name}")
            country = CountryData.get_country_by_name(name)

            if not country:
                app.logger.warning(f"Country not found: {name}")
                return make_response(jsonify({
                    "status": "error",
                    "message": f"Country '{name}' not found in database"
                }), 400)

            favorites_model.add_country_to_favorites(country.name)
            app.logger.info(f"Successfully added country to favorites: {name}")

            return make_response(jsonify({
                "status": "success",
                "message": f"Country '{name}' added to favorites"
            }), 201)

        except Exception as e:
            app.logger.error(f"Failed to add country to favorites: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "An internal error occurred while adding the country to the favorites",
                "details": str(e)
            }), 500)


    @app.route('/api/remove-country-from-favorites', methods=['DELETE'])
    @login_required
    def remove_country_by_name() -> Response:
        """Route to remove a country from the favorites by name.

        Expected JSON Input:
            - name (str): The name of the country.

        Returns:
            JSON response indicating success of the removal.

        Raises:
            400 error if required fields are missing or the country does not exist in the favorites.
            500 error if there is an issue removing the country.

        """
        try:
            app.logger.info("Received request to remove country from favorites")

            data = request.get_json()
            required_fields = ["name"]
            missing_fields = [field for field in required_fields if field not in data]

            if missing_fields:
                app.logger.warning(f"Missing required field: {missing_fields}")
                return make_response(jsonify({
                    "status": "error",
                    "message": f"Missing required field: {', '.join(missing_fields)}"
                }), 400)

            name = data["name"]

            app.logger.info(f"Looking up country to remove: {name}")
            country = CountryData.get_country_by_name(name)

            if not country:
                app.logger.warning(f"Country not found in database: {name}")
                return make_response(jsonify({
                    "status": "error",
                    "message": f"Country '{name}' not found in database"
                }), 400)

            favorites_model.remove_favorite(name)
            app.logger.info(f"Successfully removed country from favorites: {name}")

            return make_response(jsonify({
                "status": "success",
                "message": f"Country '{name}' removed from favorites"
            }), 200)

        except Exception as e:
            app.logger.error(f"Failed to remove country from favorites: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "An internal error occurred while removing the country from the favorites",
                "details": str(e)
            }), 500)


    @app.route('/api/remove-country-from-favorites-by-country-list-number/<int:country_list_number>', methods=['DELETE'])
    @login_required
    def remove_country_by_country_list_number(country_list_number: int) -> Response:
        """Route to remove a country from the favorites by country list number.

        Path Parameter:
            - country_list_number (int): The country list number of the country to remove.

        Returns:
            JSON response indicating success of the removal.

        Raises:
            404 error if the country list number does not exist.
            500 error if there is an issue removing the country.

        """
        try:
            app.logger.info(f"Received request to remove country at country list number {country_list_number} from favorites")

            favorites_model.remove_country_by_country_list_number(country_list_number)

            app.logger.info(f"Successfully removed country at country list number {country_list_number} from favorites")
            return make_response(jsonify({
                "status": "success",
                "message": f"Country at country list number {country_list_number} removed from favorites"
            }), 200)

        except ValueError as e:
            app.logger.warning(f"Country list number {country_list_number} not found in favorites: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": f"Country list number {country_list_number} not found in favorites"
            }), 404)

        except Exception as e:
            app.logger.error(f"Failed to remove country at country list number {country_list_number}: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "An internal error occurred while removing the country from the favorites",
                "details": str(e)
            }), 500)


    @app.route('/api/clear-favorites', methods=['POST'])
    @login_required
    def clear_favorites() -> Response:
        """Route to clear all countries from the favorites.

        Returns:
            JSON response indicating success of the operation.

        Raises:
            500 error if there is an issue clearing the favorites.

        """
        try:
            app.logger.info("Received request to clear the favorites")

            favorites_model.clear_favorites()

            app.logger.info("Successfully cleared the favorites")
            return make_response(jsonify({
                "status": "success",
                "message": "Favorites cleared"
            }), 200)

        except Exception as e:
            app.logger.error(f"Failed to clear favorites: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "An internal error occurred while clearing the favorites",
                "details": str(e)
            }), 500)


    @app.route('/api/go-to-country-list-number/<int:country_list_number>', methods=['POST'])
    @login_required
    def go_to_country_list_number(country_list_number: int) -> Response:
        """Route to go the favorites list number.

        Path Parameter:
            - country_list_number (int): The country list number to set as the favorite country.

        Returns:
            JSON response indicating success or an error message.

        Raises:
            400 error if the country list number is invalid.
            500 error if there is an issue updating the country list number.
        """
        try:
            app.logger.info(f"Received request to go to country list number {country_list_number}")

            if not favorites_model.is_valid_country_list_number(country_list_number):
                app.logger.warning(f"Invalid country list number: {country_list_number}")
                return make_response(jsonify({
                    "status": "error",
                    "message": f"Invalid country list number: {country_list_number}. Please provide a valid country list number."
                }), 400)

            favorites_model.go_to_country_list_number(country_list_number)
            app.logger.info(f"Favorites set to country list number {country_list_number}")

            return make_response(jsonify({
                "status": "success",
                "message": f"Now playing from country list number {country_list_number}"
            }), 200)

        except ValueError as e:
            app.logger.warning(f"Failed to set country list number {country_list_number}: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": str(e)
            }), 400)

        except Exception as e:
            app.logger.error(f"Internal error while going to country list number {country_list_number}: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "An internal error occurred while changing the country list number",
                "details": str(e)
            }), 500)



    ############################################################
    #
    # View Favorites
    #
    ############################################################


    @app.route('/api/get-all-countries-from-favorites', methods=['GET'])
    @login_required
    def get_all_countries_from_favorites() -> Response:
        """Retrieve all countries in the favorites.

        Returns:
            JSON response containing the list of countries.

        Raises:
            500 error if there is an issue retrieving the favorites.

        """
        try:
            app.logger.info("Received request to retrieve all countries from the favorites.")

            countries = favorites_model.get_all_countries()
            
            countries_dict = [country.to_dict() for country in countries]

            app.logger.info(f"Successfully retrieved {len(countries)} countries from the favorites.")
            return make_response(jsonify({
                "status": "success",
                "countries": countries_dict
            }), 200)

        except Exception as e:
            app.logger.error(f"Failed to retrieve countries from favorites: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "An internal error occurred while retrieving the favorites",
                "details": str(e)
            }), 500)


    

    @app.route('/api/get-country-from-favorites-by-country-list-number/<int:country_list_number>', methods=['GET'])
    @login_required
    def get_country_by_country_list_number(country_list_number: int) -> Response:
        """Retrieve a country from the favorites by country list number.

        Path Parameter:
            - country_list_number (int): The country list number of the country.

        Returns:
            JSON response containing country details.

        Raises:
            404 error if the country list number is not found.
            500 error if there is an issue retrieving the country.

        """
        try:
            app.logger.info(f"Received request to retrieve country at country list number {country_list_number}.")

            country = favorites_model.get_country_by_country_list_number(country_list_number)

            app.logger.info(f"Successfully retrieved country: {country.name}")
            return make_response(jsonify({
                "status": "success",
                "country": country
            }), 200)

        except ValueError as e:
            app.logger.warning(f"Country list number {country_list_number} not found: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": str(e)
            }), 404)

        except Exception as e:
            app.logger.error(f"Failed to retrieve country by country list number {country_list_number}: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "An internal error occurred while retrieving the country",
                "details": str(e)
            }), 500)


    @app.route('/api/get-favorite-country', methods=['GET'])
    @login_required
    def get_favorite_country() -> Response:
        """Retrieve the favorite country being played.

        Returns:
            JSON response containing favorite country details.

        Raises:
            500 error if there is an issue retrieving the favorite country.

        """
        try:
            app.logger.info("Received request to retrieve the favorite country.")

            favorite_country = favorites_model.get_favorite_country()

            app.logger.info(f"Successfully retrieved favorite country: {favorite_country.name}.")
            return make_response(jsonify({
                "status": "success",
                "favorite_country": favorite_country
            }), 200)

        except Exception as e:
            app.logger.error(f"Failed to retrieve favorite country: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "An internal error occurred while retrieving the favorite country",
                "details": str(e)
            }), 500)


    @app.route('/api/get-favorites-length-population', methods=['GET'])
    @login_required
    def get_favorites_length_and_population() -> Response:
        """Retrieve the length (number of countries) and population (total of people from all the countries) in favorites.

        Returns:
            JSON response containing the favorites length and population.

        Raises:
            500 error if there is an issue retrieving favorites information.

        """
        try:
            app.logger.info("Received request to retrieve favorites length and population.")

            favorites_length = favorites_model.get_favorites_length()
            favorites_population = favorites_model.get_favorites_population()

            app.logger.info(f"Favorites contains {favorites_length} countries with a total population of {favorites_population} people.")
            return make_response(jsonify({
                "status": "success",
                "favorites_length": favorites_length,
                "favorites_population": favorites_population
            }), 200)

        except Exception as e:
            app.logger.error(f"Failed to retrieve favorites length and population: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "An internal error occurred while retrieving favorites length and population details",
                "details": str(e)
            }), 500)
            
    @app.route('/api/compare-two-favorites', methods=['GET'])
    @login_required
    def compare_two_favorites() -> Response:
        """Compare two favorites and return the differences.

        Returns:
            JSON response containing the differences between the two favorites.

        Raises:
            500 error if there is an issue comparing the favorites.

        """
        try:
            app.logger.info("Received request to compare two favorites.")

            data = request.get_json()
            country1_name = data.get("country1_name")
            country2_name = data.get("country2_name")
            
            # Check for missing fields
            if not country1_name or not country2_name:
                return make_response(jsonify({
                    "status": "error",
                    "message": "Both 'country1_name' and 'country2_name' are required"
                }), 400)

            # Call your FavoritesModel compare_two_favorites method:
            comparison_result = favorites_model.compare_two_favorites(country1_name, country2_name)

            app.logger.info(f"Successfully compared {country1_name} and {country2_name}")
            return make_response(jsonify({
                "status": "success",
                "message": f"Comparison between '{country1_name}' and '{country2_name}' completed",
                "comparison": comparison_result
            }), 200)

        except ValueError as e:
            return make_response(jsonify({
                "status": "error",
                "message": str(e)
            }), 400)

        except Exception as e:
            app.logger.error(f"Failed to compare favorite countries: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "An internal error occurred while comparing countries",
                "details": str(e)
            }), 500)


    ############################################################
    #
    # Arrange Favorites
    #
    ############################################################


    @app.route('/api/move-country-to-top', methods=['POST'])
    @login_required
    def move_country_to_top() -> Response:
        """Move a country to the top of the favorites.

        Expected JSON Input:
            name (str): The name of the country to move.

        Returns:
            Response: JSON response indicating success or an error message.

        Raises:
            400 error if required fields are missing.
            500 error if an error occurs while updating the favorites.

        """
        try:
            data = request.get_json()

            required_fields = ["name"]
            missing_fields = [field for field in required_fields if field not in data]

            if missing_fields:
                app.logger.warning(f"Missing required fields: {missing_fields}")
                return make_response(jsonify({
                    "status": "error",
                    "message": f"Missing required fields: {', '.join(missing_fields)}"
                }), 400)

            name = data["name"]
            app.logger.info(f"Received request to move country to top: {name}")

            country = CountryData.get_country_by_name(name)
            favorites_model.move_country_to_top(country.id)

            app.logger.info(f"Successfully moved country to top: {name}")
            return make_response(jsonify({
                "status": "success",
                "message": f"Country '{name}' moved to top"
            }), 200)

        except Exception as e:
            app.logger.error(f"Failed to move country to top: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "An internal error occurred while moving the country",
                "details": str(e)
            }), 500)


    @app.route('/api/move-country-to-end', methods=['POST'])
    @login_required
    def move_country_to_end() -> Response:
        """Move a country to the end of the favorites.

        Expected JSON Input:
            - artist (str): The artist of the country.
            - title (str): The title of the country.
            - year (int): The year the country was released.

        Returns:
            Response: JSON response indicating success or an error message.

        Raises:
            400 error if required fields are missing.
            500 if an error occurs while updating the favorites.

        """
        try:
            data = request.get_json()

            required_fields = ["name"]
            missing_fields = [field for field in required_fields if field not in data]

            if missing_fields:
                app.logger.warning(f"Missing required fields: {missing_fields}")
                return make_response(jsonify({
                    "status": "error",
                    "message": f"Missing required fields: {', '.join(missing_fields)}"
                }), 400)

            name = data["name"]
            app.logger.info(f"Received request to move country to end: {name}")

            country = CountryData.get_country_by_name(name)
            favorites_model.move_country_to_end(country.id)

            app.logger.info(f"Successfully moved country to end: {name}")
            return make_response(jsonify({
                "status": "success",
                "message": f"Country '{name}' moved to end"
            }), 200)

        except Exception as e:
            app.logger.error(f"Failed to move country to end: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "An internal error occurred while moving the country",
                "details": str(e)
            }), 500)


    @app.route('/api/move-country-to-country-list-number', methods=['POST'])
    @login_required
    def move_country_to_country_list_number() -> Response:
        """Move a country to a specific country list number in the favorites.

        Expected JSON Input:
            name (str): The name of the country to move.
            country_list_number (int): The country list number to move the country to (1-indexed).

        Returns:
            Response: JSON response indicating success or an error message.

        Raises:
            400 error if required fields are missing.
            500 error if an error occurs while updating the favorites.
        """
        try:
            data = request.get_json()

            required_fields = ["name", "country_list_number"]
            missing_fields = [field for field in required_fields if field not in data]

            if missing_fields:
                app.logger.warning(f"Missing required fields: {missing_fields}")
                return make_response(jsonify({
                    "status": "error",
                    "message": f"Missing required fields: {', '.join(missing_fields)}"
                }), 400)

            name, country_list_number = data["name"], data["country_list_number"]
            app.logger.info(f"Received request to move country to country list number {country_list_number}: {name}")

            country = CountryData.get_country_by_name(name)
            favorites_model.move_country_to_country_list_number(country.id, country_list_number)

            app.logger.info(f"Successfully moved country to country list number {country_list_number}: {name}")
            return make_response(jsonify({
                "status": "success",
                "message": f"Country '{name}' moved to country list number {country_list_number}"
            }), 200)

        except Exception as e:
            app.logger.error(f"Failed to move country to country list number: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "An internal error occurred while moving the country",
                "details": str(e)
            }), 500)




    ############################################################
    #
    # Leaderboard / Stats
    #
    ############################################################


    @app.route('/api/country-population-leaderboard', methods=['GET'])
    def get_country_population_leaderboard() -> Response:
        """
        Route to retrieve a leaderboard of countries sorted by play count.

        Returns:
            JSON response with a sorted leaderboard of countries.

        Raises:
            500 error if there is an issue generating the leaderboard.

        """
        try:
            app.logger.info("Received request to generate country leaderboard")

            leaderboard_data = CountryData.get_all_countries(sort_by_population=True)

            app.logger.info(f"Successfully generated country population leaderboard with {len(leaderboard_data)} entries")
            return make_response(jsonify({
                "status": "success",
                "leaderboard": leaderboard_data
            }), 200)

        except Exception as e:
            app.logger.error(f"Failed to generate country population leaderboard: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "An internal error occurred while generating the leaderboard",
                "details": str(e)
            }), 500)

    return app

if __name__ == '__main__':
    app = create_app()
    app.logger.info("Starting Flask app...")
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    except Exception as e:
        app.logger.error(f"Flask app encountered an error: {e}")
    finally:
        app.logger.info("Flask app has stopped.")
