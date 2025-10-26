Feature: User Registration and Profile View

Scenario: Register a new user with valid inputs
    Given I have the necessary data for user registration: username, password, and email
    When I send a POST request to the /api/register endpoint with the data
    Then the response status should be 201 Created and the response body should contain a message indicating successful registration

Scenario: Register a new user with an existing username
    Given I have the same username as an existing user
    When I send a POST request to the /api/register endpoint with the data
    Then the response status should be 400 Bad Request and the response body should contain an error message indicating that the user already exists

Scenario: Register a new user without email
    Given I do not provide an email in the registration data
    When I send a POST request to the /api/register endpoint with the data
    Then the response status should be 400 Bad Request and the response body should contain an error message indicating that an email is required

Scenario: Login an authenticated user and retrieve profile information
    Given I am logged in as a valid user
    When I send a GET request to the /api/profile endpoint
    Then the response status should be 200 OK and the response body should contain the user's id, username, email, role, and company name if applicable

Scenario: Logout an authenticated user by invalidating tokens
    Given I am logged in as a valid user
    When I send a POST request to the /api/logout endpoint with a valid refresh token
    Then the response status should be 205 Reset Content and the response body should contain a message indicating that the session has been closed

Scenario: Attempt to logout without a valid refresh token
    Given I do not have a valid refresh token
    When I send a POST request to the /api/logout endpoint with an invalid refresh token
    Then the response status should be 400 Bad Request and the response body should contain an error message indicating that the token is invalid
