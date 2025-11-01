Feature: Metals UI

Scenario: Navigation and layout loading
Given the user navigates to the "Metals" page
Then the page title should display "Metales y Divisas"
And a banner with exchange rate information is visible

Scenario: Search functionality
Given the user enters "gold" in the search bar
When the user clicks the search button or presses enter
Then only gold related metals and currencies are displayed

Scenario: Currency selection
Given the user selects MXN as currency
When the user navigates to the Metals page again
Then the displayed prices should be converted to Mexican pesos

Scenario: Error state for empty data
Given no metals or currencies are available
When the user navigates to the Metals page
Then the message "No hay metales registrados." is displayed

Scenario: Success/error messages
Given the user tries to update exchange rate
Then a success toast message with the updated exchange rate should be displayed
And an error toast message should be displayed if an error occurs during the process

Scenario: Route guards
Given the user navigates to the Metals page without being authenticated
Then the user should be redirected to the login page or display a message about authentication required