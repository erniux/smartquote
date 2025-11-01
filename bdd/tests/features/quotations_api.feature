Feature: Quotation Management API

Scenario: Retrieve a list of all quotes
Given I have an instance of QuotationViewSet
When I call the get_list method
Then the response should contain a list of quotes

Scenario: Retrieve details of a specific quote by its ID
Given I have an instance of QuotationViewSet and a valid quote ID
When I call the retrieve method with the quote ID
Then the response should contain the details of the specified quote

Scenario: Create a new quote
Given I have an instance of QuotationViewSet
And I have the necessary data to create a new quote
When I call the create method with the quote data
Then the response should contain the created quote

Scenario: Update an existing quote
Given I have an instance of QuotationViewSet and a valid quote ID
And I have the necessary data to update the quote
When I call the update method with the quote ID and updated data