# CS411-Final-Project: World Explorer: Travel App

**World Explorer** is an appication that allows users to explore and save information about countries around the world. Users can search for countries, view detailed information about each country, save favorites, compare statistics of favorite countries, and manage their accounts. Country data is pulled from [REST Countries API] – (https://restcountries.com/)

# Features 

- Search for a country by name 
- Favorite countries 
- Remove the country from favorites 
- View all favorited countries 
- Compare stats from favorited countries 
- Filter favorited countries and search by filters (langauge, region, etc.)

## Routes
### Health Check 


Route: /api/health

Request Type: GET

Purpose: Verifies that the service is running

Request Body:
None

Response Format: JSON

Success Response Example:
Code: 200
Content: 

```json
{ "status": "healthy" }
```

Example Request:
curl -X GET http://localhost:5000/api/health

Example Response:
```json
{
  "status": "healthy"
}
```


### Create User 


Route: /api/create-user

Request Type: PUT

Purpose: Creates a new user 

Request Body:

```json
{
  "username": "testuser",
  "password": "securepassword"
}
```

Response Format: JSON

Success Response Example:
Code: 201
Content: 

```json
{
    "status": "success",
    "message": "User 'username' created successfully"
}
```

Example Request:
curl -X PUT http://localhost:5000/api/create-user -H "Content-Type: application/json" \
-d '{"username":{username}, "password":"securepassword"}'

Example Response:
```json
{
  "status": "success",
  "message": "User {username} created successfully"
}
```


### Login 


Route: /api/login

Request Type: POST

Purpose: Login as an existing user

Request Body:
```json
{
  "username": "testuser",
  "password": "securepassword"
}
```

Response Format: JSON

Success Response Example:
Code: 200
Content: 
```json
{
    "status": "success",
    "message": f"User '{username}' logged in successfully"
}
```

Example Request:
curl -X POST http://localhost:5000/api/login -H "Content-Type: application/json" \
-d '{"username":{username}, "password":{securepassword}}'

Example Response:
```json
{
  "status": "success",
  "message": "User {username} logged in successfully"
}
```


### Logout 


Route: /api/logout 

Request Type: POST 

Purpose: Logs out of current user

Request Body:
None

Response Format: JSON

Success Response Example:
Code: 200
Content: 
```json
{
  "status": "success",
  "message": "User logged out successfully"
}
```

Example Request:
curl -X POST http://localhost:5000/api/logout

Example Response:
```json
{
  "status": "success",
  "message": "User logged out successfully"
}
```



### Change Password 


Route: /api/change-password

Request Type: POST

Purpose: Changes the password for the current user 

Request Body:
```json
{
  "new_password": "newsecurepassword"
}
```

Response Format: JSON

Success Response Example:
Code: 200
Content: 
```json
{
  "status": "success",
  "message": "Password changed successfully"
}
```

Example Request:
curl -X POST http://localhost:5000/api/change-password -H "Content-Type: application/json" \
-d '{"new_password":"newsecurepassword"}'


Example Response:
```json
{
  "status": "success",
  "message": "Password changed successfully"
}
```


### Reset users 


Route: /api/reset-users

Request Type: DELETE

Purpose: Deletes all current users and recreates a new User Table 

Request Body:
None

Response Format: JSON

Success Response Example:
Code: 200
Content: 
```json
{
  "status": "success",
  "message": "Users table recreated successfully"
}
```

Example Request:
curl -X DELETE http://localhost:5000/api/reset-users

Example Response:
```json
{
  "status": "success",
  "message": "Users table recreated successfully"
}
```

### Reset Countries 

Route: /api/reset-countries

Request Type: DELETE

Purpose: Delete all countries and recreates the CountryData table

Request Body:
None

Response Format: JSON

Success Response Example:
Code: 200
Content: 
```json
{
  "status": "success",
  "message": "CountryData table recreated successfully"
}
```

Example Request:
curl -X DELETE http://localhost:5000/api/reset-countries

Example Response:
```json
{
  "status": "success",
  "message": "CountryData table recreated successfully"
}
```


### Create a Country 
Route: /api/create-country

Request Type: POST

Purpose: Adds a new country to the database 

Request Body:
```json
{
  "name": "Japan",
  "capital": "Tokyo",
  "region": "Asia",
  "population": 126476461,
  "languages": ["Japanese"],
  "currencies": ["JPY"],
  "borders": ["CHN", "KOR"],
  "flag_url": "https://flagcdn.com/jp.svg",
  "timezones": ["UTC+09:00"]
}
```


Response Format: JSON

Success Response Example:
Code: 201
Content: 
```json
{
  "status": "success",
  "message": "Country {name} added successfully"
}
```

Example Request:
curl -X POST http://localhost:5000/api/create-country -H "Content-Type: application/json" \
-d '{"name":"Japan","capital":"Tokyo","region":"Asia","population":126476461,"languages":["Japanese"],"currencies":["JPY"],"borders":["CHN","KOR"],"flag_url":"https://flagcdn.com/jp.svg","timezones":["UTC+09:00"]}'


Example Response:
```json
{
  "status": "success",
  "message": "Country {name} added successfully"
}
```

### Delete a Country

Route: /api/delete-country/<string:name>

Request Type: DELETE

Purpose: Deletes a country from the DB by its name

Request Body:
None

Response Format: JSON

Success Response Example:
Code: 200
Content:
```json
{
  "status": "success",
  "message": "Country with name Japan deleted successfully"
}
```

Example Request:
curl -X DELETE http://localhost:5000/api/delete-country/Japan

Example Response:
```json
{
  "status": "success",
  "message": "Country with name Japan deleted successfully"
}
```



### Get All Countries 

Route: /api/get-all-countries-from-database

Request Type: GET

Purpose: Retrieve all countries in the database

Request Body:
None

Response Format: JSON

Success Response Example:
Code: 200
Content: 
```json
{
  "status": "success",
  "message": "CountryData retrieved successfully",
  "countries": []
}
```

Example Request:
curl -X GET http://localhost:5000/api/get-all-countries-from-database

Example Response:
```json
{
  "status": "success",
  "message": "CountryData retrieved successfully",
  "countries": []
}
```

### Add Country to Favorites 


Route: /api/add-country-to-favorites

Request Type: POST

Purpose: Adds a country to the favorites list 

Request Body:
```json
{
  "name": "Japan"
}
```

Response Format: JSON

Success Response Example:
Code: 201
Content: 

```json
{
  "status": "success",
  "message": "Country 'Japan' added to favorites"
}
```

Example Request:
curl -X POST http://localhost:5000/api/add-country-to-favorites \
-H "Content-Type: application/json" \
-d '{"name": "Japan"}

Example Response:
```json
{
  "status": "success",
  "message": "Country 'Japan' added to favorites"
}
```


### remove Country from Favorites 


Route: /api/remove-country-from-favorites

Request Type: DELETE

Purpose: removes a country from the favorites list by name 

Request Body:
{
  "name": "Japan"
}

Response Format: JSON

Success Response Example:
Code: 200
Content: 

```json
{
  "status": "success",
  "message": "Country 'Japan' removed from favorites"
}
```

Example Request:
curl -X DELETE http://localhost:5000/api/remove-country-from-favorites \
-H "Content-Type: application/json" \
-d '{"name": "Japan"}'


Example Response:
```json
{
  "status": "success",
  "message": "Country 'Japan' removed from favorites"
}
```


### Get Length of Favorites 


Route: /api/get-favorites-length-population

Request Type: GET

Purpose: Get the total number of favorites and their combined populations 

Request Body:
None

Response Format: JSON

Success Response Example:
Code: 200
Content: 

```json
{
  "status": "success",
  "favorites_length": 2,
  "favorites_population": 389876543
}

```

Example Request:
curl -X GET http://localhost:5000/api/get-favorites-length-population

Example Response:
```json
{
  "status": "success",
  "favorites_length": 2,
  "favorites_population": 389876543
}
```


### Compare Two Favorite Countries


Route: /api/compare-two-favorites

Request Type: GET

Purpose: Compare two favorite countries and return their difference

Request Body:
```json
{
  "country1_name": "Japan",
  "country2_name": "Canada"
}
```

Response Format: JSON

Success Response Example:
Code: 200
Content: 

```json
{
  "status": "success",
  "favorites_length": 2
  "favorites_population": 15000000
}
```

Example Request:
curl -X GET http://localhost:5000/api/compare-two-favorites \
-H "Content-Type: application/json" \
-d '{"country1_name": "Japan", "country2_name": "Canada"}'

Example Response:
```json
{
  "status": "success",
  "favorites_length": 2
  "favorites_population": 15000000
}
```


<!--

# Steps to set up Virtual Environment and run unit tests:
# 1. Optional: chmod +x setup_venv.sh
# 2. ./setup_venv.sh   
# 3. source venv/bin/activate

# Check PYTHONPATH

# 4. pytest
#
#
# If PYTHONPATH isn't set:
# export PYTHONPATH="path/to/file:$PYTHONPATH"

# For my situation:
# export PYTHONPATH="/Users/gavinschoolaccount/Desktop/411_project/code/CS411-Final-Project:$PYTHONPATH"

-->