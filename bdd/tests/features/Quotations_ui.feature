Feature: Jewelry Quotation and Search

Scenario: Requesting a quotation
Given the user is on the quote form page
When the user enters their name, email, selects a jewelry type, and enters the quantity
And the user clicks the "Submit" button
Then the request should be sent to the server
And the user should receive a quotation response

Scenario: Searching for products
Given the user is on the product search page
When the user enters a product name in the search field
Then the system should display the matching product results
And each result should include the product name and current metal price (if applicable)