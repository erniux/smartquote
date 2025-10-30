Feature: Quotation Management

Scenario: Generate Sale from Quotation (Admin Role)
Given I am authenticated as an admin user
And I have a quotation created with valid details
When I send a GET request to the API endpoint for generating a sale from the quotation
Then I should receive a successful response
And a new sale should be created associated with the quotation
And the status of the quotation should change to 'sold'

Scenario: Generate Sale from Quotation (Company Member Role)
Given I am authenticated as a company member user
And I have a quotation created with valid details that I have access to
When I send a GET request to the API endpoint for generating a sale from the quotation
Then I should receive a successful response
And a new sale should be created associated with the quotation
And the status of the quotation should change to 'sold'