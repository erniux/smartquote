Feature: Login UI

Scenario: Valid login with correct credentials
Given the user navigates to the login page
When the user enters valid username and password
And the user clicks on the "Iniciar sesión" button
Then the system should display a success message and navigate to "/quotations"

Scenario: Invalid login with incorrect credentials
Given the user navigates to the login page
When the user enters invalid username or password
And the user clicks on the "Iniciar sesión" button
Then the system should display an error message

Scenario: Login attempt without entering username or password
Given the user navigates to the login page
When the user clicks on the "Iniciar sesión" button without filling out the form
Then the system should display an error message indicating that all fields are required

Scenario: Login attempt after reaching max attempts limit
Given the user has reached the max number of failed login attempts
When the user enters invalid credentials and clicks on the "Iniciar sesión" button
Then the system should display an error message indicating that the account is temporarily locked due to too many failed login attempts

Scenario: Login attempt after unlocking the account
Given the user's account has been temporarily locked due to too many failed login attempts
When the user enters valid credentials and clicks on the "Iniciar sesión" button
Then the system should unlock the account and display a success message, navigating to "/quotations"

Scenario: Login attempt while offline
Given the user is offline
When the user enters valid credentials and clicks on the "Iniciar sesión" button
Then the system should display an error message indicating that the network connection is unavailable