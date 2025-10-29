Feature: Create a new quotation

Scenario: Successful creation of a new quotation
Given I have authenticated as a member user
When I send a POST request to "/quotations/" with valid data for Quotation serializer
Then the status code returned should be 201 Created
And the response body should contain the newly created quotation's data

Scenario: Unsuccessful creation of a new quotation due to invalid data
Given I have authenticated as a member user
When I send an invalid POST request to "/quotations/" with incomplete or incorrect data for Quotation serializer
Then the status code returned should be 400 Bad Request
And the response body should contain error messages for the invalid fields