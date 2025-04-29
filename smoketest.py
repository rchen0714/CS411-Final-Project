import requests


def run_smoketest():
    base_url = "http://localhost:5000/api"
    username = "test"
    password = "test"


    test_country = {
        "name": "Testlandia",
        "capital": "Testville",
        "region": "Test Region",
        "population": 123456,
        "languages": ["Testish"],
        "currencies": ["Testcoin"],
        "borders": ["Testlandia2"],
        "flag_url": "https://cdn.britannica.com/33/4833-050-F6E415FE/Flag-United-States-of-America.jpg",
        "timezones": ["UTC+0"]
    }

    test_country2 = {
        "name": "Testlandia2",
        "capital": "Testville2",
        "region": "Test Region2",
        "population": 5563543,
        "languages": ["Testish2"],
        "currencies": ["Testcoin2"],
        "borders": ["Testlandia"],
        "flag_url": "https://cdn.britannica.com/90/7490-050-5D33348F/Flag-China.jpg",
        "timezones": ["UTC+0"]
    }

    health_response = requests.get(f"{base_url}/health")
    assert health_response.status_code == 200
    assert health_response.json()["status"] == "success"

    delete_user_response = requests.delete(f"{base_url}/reset-users")
    assert delete_user_response.status_code == 200
    assert delete_user_response.json()["status"] == "success"
    print("Reset users successful")

    delete_country_response = requests.delete(f"{base_url}/reset-countries")
    assert delete_country_response.status_code == 200
    assert delete_country_response.json()["status"] == "success"
    print("Reset countries successful")

    create_user_response = requests.put(f"{base_url}/create-user", json={
        "username": username,
        "password": password
    })
    assert create_user_response.status_code == 201
    assert create_user_response.json()["status"] == "success"
    print("User creation successful")

    session = requests.Session()
    
    ##################################################
    # Testing Login and Logouts 
    ##################################################

    # Log in
    login_resp = session.post(f"{base_url}/login", json={
        "username": username,
        "password": password
    })
    assert login_resp.status_code == 200
    assert login_resp.json()["status"] == "success"
    print("Login successful")
    
     # Change password
    change_password_resp = session.post(f"{base_url}/change-password", json={
        "new_password": "new_password"
    })
    assert change_password_resp.status_code == 200
    assert change_password_resp.json()["status"] == "success"
    print("Password change successful")
    
     # Log out
    logout_resp = session.post(f"{base_url}/logout")
    assert logout_resp.status_code == 200
    assert logout_resp.json()["status"] == "success"
    print("Logout successful")
    
    create_country_logged_out_resp = session.post(f"{base_url}/create-country", json=test_country2)
    
    # This should fail because we are logged out
    assert create_country_logged_out_resp.status_code == 401
    assert create_country_logged_out_resp.json()["status"] == "error"
    print("Country creation failed after logout (as expected)")
    
    # Log in with new password
    login_resp = session.post(f"{base_url}/login", json={
        "username": username,
        "password": "new_password"
    })
    assert login_resp.status_code == 200
    assert login_resp.json()["status"] == "success"
    print("Login with new password successful")
    
    ##################################################
    # API smoketest for countries
    ##################################################
    
    #Creating countries 
    create_country_resp = session.post(f"{base_url}/create-country", json=test_country)
    assert create_country_resp.json()["status"] == "success"
    assert create_country_resp.status_code == 201
    print("Country creation successful")
    
    create_country_resp2 = session.post(f"{base_url}/create-country", json=test_country2)
    assert create_country_resp2.status_code == 201
    assert create_country_resp2.json()["status"] == "success"
    print("Second country creation successful")

    # Get all countries
    get_all_countries_resp = session.get(f"{base_url}/get-all-countries-from-database")
    assert get_all_countries_resp.status_code == 200
    assert get_all_countries_resp.json()["status"] == "success"
    assert len(get_all_countries_resp.json()["countries"]) == 2
    print("Get all countries successful")
    
    # Get country by name
    get_country_by_name_resp = session.get(f"{base_url}/get-country-from-database-by-name/Testlandia")
    assert get_country_by_name_resp.status_code == 200
    assert get_country_by_name_resp.json()["status"] == "success"
    assert get_country_by_name_resp.json()["country"] == "Testlandia"
    print("Get country by name successful")
    
    #Add country to favorites
    add_favorite_resp = session.post(f"{base_url}/add-country-to-favorites", json={
    "name": "Testlandia"
    })
    assert add_favorite_resp.status_code == 201
    assert add_favorite_resp.json()["status"] == "success"
    print("Add country to favorites successful")
    
    add_favorite_resp2 = session.post(f"{base_url}/add-country-to-favorites", json={
        "name": "Testlandia2"
    })
    assert add_favorite_resp2.status_code == 201
    assert add_favorite_resp2.json()["status"] == "success"
    print("Add second country to favorites successful")
    
    # Get all favorites
    get_all_favorites_resp = session.get(f"{base_url}/get-all-countries-from-favorites")
    assert get_all_favorites_resp.status_code == 200
    assert get_all_favorites_resp.json()["status"] == "success"
    assert len(get_all_favorites_resp.json()["countries"]) >= 2
    print("Get all favorites successful")
    
    # Compare favorites
    compare_favorites_resp = session.get(f"{base_url}/compare-two-favorites", json={
        "country1_name": "Testlandia",
        "country2_name": "Testlandia2"
    })
    assert compare_favorites_resp.status_code == 200
    assert compare_favorites_resp.json()["status"] == "success"
    print("Compare two favorites successful")
    
    # remove favorites
    remove_favorite_resp = session.delete(f"{base_url}/remove-country-from-favorites", json={
        "name": "Testlandia"
    })
    assert remove_favorite_resp.status_code == 200
    assert remove_favorite_resp.json()["status"] == "success"
    print("Remove one country from favorites successful")
    
    # clear favorites
    clear_favorites_resp = session.post(f"{base_url}/clear-favorites")
    assert clear_favorites_resp.status_code == 200
    assert clear_favorites_resp.json()["status"] == "success"
    print("Clear favorites successful")
    
    # Get all favorites again after clearing 
    get_all_favorites_resp = session.get(f"{base_url}/get-all-countries-from-favorites")
    assert get_all_favorites_resp.status_code == 200
    assert get_all_favorites_resp.json()["status"] == "success"
    assert len(get_all_favorites_resp.json()["countries"]) == 0
    print("Favorites list is empty after clearing (expected)")
    
if __name__ == "__main__":
    run_smoketest()
