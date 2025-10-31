Feature: Companies API

Scenario: Retrieve all companies with correct auth
Given I have valid API credentials
When I send GET request to "/companies/"
Then status code should be 200
And response format should be JSON
And the list of companies should be returned

Scenario: Retrieve a single company by ID with correct auth
Given I have valid API credentials
And there is a company in the database with specific ID
When I send GET request to "/companies/<company_id>"
Then status code should be 200
And response format should be JSON
And the requested company's data should be returned

Scenario: Create a new company with correct auth
Given I have valid API credentials
When I send POST request to "/companies/" with the following json payload
| Key            | Value                  |
|----------------|------------------------|
| name           | "Valid Company Name"   |
| logo           | "base64encodedlogo"    |
| address        | "123 Main St"          |
| phone          | "555-1234"             |
| email          | "example@company.com"   |
| website        | "www.companywebsite.com"|
| rfc            | "AAA0987654321"         |
Then status code should be 201
And response format should be JSON
And the created company's data should include the newly generated ID and timestamp

Scenario: Update an existing company with correct auth
Given I have valid API credentials
And there is a company in the database with specific ID
When I send PATCH request to "/companies/<company_id>" with the following json payload
| Key            | Value                  |
|----------------|------------------------|
| name           | "Updated Company Name" |
Then status code should be 200
And response format should be JSON
And the updated company's data should include the new name and no changes in other fields

Scenario: Delete a company with correct auth
Given I have valid API credentials
And there is a company in the database with specific ID
When I send DELETE request to "/companies/<company_id>"
Then status code should be 204

Scenario: Attempt to retrieve companies without auth
Given no API credentials provided
When I send GET request to "/companies/"
Then status code should be 401

Scenario: Attempt to access non-existent company by ID with correct auth
Given I have valid API credentials
When I send GET request to "/companies/<nonexistent_id>"
Then status code should be 404

Scenario: Attempt to create a company without required fields
Given I have valid API credentials
When I send POST request to "/companies/" with incomplete json payload
Then status code should be 400

Scenario: Attempt to update a company with invalid RFC format
Given I have valid API credentials
And there is a company in the database with specific ID
When I send PATCH request to "/companies/<company_id>" with incorrect rfc format
Then status code should be 400

Scenario: Attempt to delete a non-existent company with correct auth
Given I have valid API credentials
When I send DELETE request to "/companies/<nonexistent_id>"
Then status code should be 404