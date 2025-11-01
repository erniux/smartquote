Feature: Companies API

Scenario: Get all companies with valid parameters
Given I send a GET request to "/companies"
When I provide valid headers and an empty query string
Then status code should be 200 OK
And response body contains a list of companies objects

Scenario: Get single company by id with valid parameters
Given I send a GET request to "/companies/{company_id}"
And I provide valid headers
Then status code should be 200 OK
And response body contains the specified company object

Scenario: Get single company by id with invalid parameters
Given I send a GET request to "/companies/{invalid_id}"
And I provide valid headers
Then status code should be 404 Not Found

Scenario: Create a new company with valid parameters
Given I send a POST request to "/companies"
And I provide valid headers with authorization token
Then status code should be 201 Created
And response body contains the newly created company object

Scenario: Create a new company with missing required parameters
Given I send a POST request to "/companies"
And I provide valid headers with authorization token
Then status code should be 400 Bad Request
And response body contains error messages for missing fields

Scenario: Update a company with valid parameters
Given I send a PATCH request to "/companies/{company_id}"
And I provide valid headers with authorization token
Then status code should be 200 OK
And response body contains the updated company object

Scenario: Update a company with missing required parameters
Given I send a PATCH request to "/companies/{company_id}"
And I provide valid headers with authorization token
Then status code should be 400 Bad Request
And response body contains error messages for missing fields

Scenario: Delete a company with valid parameters
Given I send a DELETE request to "/companies/{company_id}"
And I provide valid headers with authorization token
Then status code should be 204 No Content

Scenario: Attempt to delete a non-existing company
Given I send a DELETE request to "/companies/{non_existing_id}"
And I provide valid headers with authorization token
Then status code should be 404 Not Found