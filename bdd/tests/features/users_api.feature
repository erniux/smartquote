Feature: Users API

Scenario: Register a new User with valid credentials
Given the user hasn't registered before
When I send a POST request to "/users/" with parameters:
| username       | required           |
| password       | required           |
| email          | required           |
Then the response status code should be 201 Created
And the response body should contain the message: "Usuario creado correctamente"

Scenario: Register a new User with existing username
Given the user hasn't registered before but the username already exists
When I send a POST request to "/users/" with parameters:
| username       | required           |
| password       | required           |
| email          | required           |
Then the response status code should be 400 Bad Request
And the response body should contain the error: "Usuario ya existe"

Scenario: Logout an authenticated user
Given the user is already authenticated
When I send a POST request to "/logout/" with a valid refresh token
Then the response status code should be 205 Reset Content
And the response body should contain the message: "Sesión cerrada"

Scenario: Logout with invalid refresh token
Given the user is already authenticated but the refresh token is invalid
When I send a POST request to "/logout/" with an invalid refresh token
Then the response status code should be 400 Bad Request
And the response body should contain the error: "Token inválido"

Scenario: Retrieve profile of an authenticated user
Given the user is already authenticated
When I send a GET request to "/profile/"
Then the response status code should be 200 OK
And the response body should contain the user's id, username, email, role and company name if the user belongs to a company; otherwise it should contain None for company.