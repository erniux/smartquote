Feature: Quotation Management API

Scenario: A user with proper permissions can list quotations
Given I am authenticated as an authorized user or admin user
When I send a GET request to the "/quotations/" endpoint
Then I should receive a response containing a JSON array of quotation objects, including fields such as id, customer_name, email, currency, notes, subtotal, tax, total, status, etc.
And the response status code should be 200 OK

Scenario: An unauthenticated user cannot list quotations
Given I am not authenticated
When I send a GET request to the "/quotations/" endpoint
Then I should receive a response with an error message and a status code of 401 Unauthorized

Scenario: A user can create a new quotation
Given I am authenticated as an authorized user or admin user
And I have a valid Quotation creation payload in JSON format
When I send a POST request to the "/quotations/" endpoint with the JSON payload
Then I should receive a response containing a newly created quotation object, including fields such as id, customer_name, email, currency, notes, subtotal, tax, total, status, etc.
And the response status code should be 201 Created

Scenario: A user cannot create a new quotation without proper permissions
Given I am authenticated as an unauthorized user
And I have a valid Quotation creation payload in JSON format
When I send a POST request to the "/quotations/" endpoint with the JSON payload
Then I should receive a response with an error message and a status code of 403 Forbidden

Scenario: A user can retrieve a single quotation
Given I am authenticated as an authorized user or admin user
And I have the id of an existing quotation
When I send a GET request to the "/quotations/{quotation_id}/" endpoint
Then I should receive a response containing the specified quotation object, including fields such as id, customer_name, email, currency, notes, subtotal, tax, total, status, etc.
And the response status code should be 200 OK

Scenario: A user cannot retrieve a single quotation without proper permissions
Given I am authenticated as an unauthorized user
And I have the id of an existing quotation
When I send a GET request to the "/quotations/{quotation_id}/" endpoint
Then I should receive a response with an error message and a status code of 403 Forbidden

Scenario: A user can update an existing quotation
Given I am authenticated as an authorized user or admin user
And I have the id of an existing quotation
And I have a valid Quotation update payload in JSON format
When I send a PUT request to the "/quotations/{quotation_id}/" endpoint with the JSON payload
Then I should receive a response containing the updated quotation object, including fields such as id, customer_name, email, currency, notes, subtotal, tax, total, status, etc.
And the response status code should be 200 OK

Scenario: A user cannot update an existing quotation without proper permissions
Given I am authenticated as an unauthorized user
And I have the id of an existing quotation
And I have a valid Quotation update payload in JSON format
When I send a PUT request to the "/quotations/{quotation_id}/" endpoint with the JSON payload
Then I should receive a response with an error message and a status code of 403 Forbidden

Scenario: A user can delete an existing quotation
Given I am authenticated as an authorized user or admin user
And I have the id of an existing quotation
When I send a DELETE request to the "/quotations/{quotation_id}/" endpoint
Then I should receive a response containing the deleted quotation object, including fields such as id, customer_name, email, currency, notes, subtotal, tax, total, status, etc.
And the response status code should be 204 No Content

Scenario: A user cannot delete an existing quotation without proper permissions
Given I am authenticated as an unauthorized user
And I have the id of an existing quotation
When I send a DELETE request to the "/quotations/{quotation_id}/" endpoint
Then I should receive a response with an error message and a status code of 403 Forbidden

Scenario: A user can generate sales from a quotation
Given I am authenticated as an authorized user or admin user
And I have the id of an existing quotation
When I send a POST request to the "/quotations/{quotation_id}/generate-sales/" endpoint
Then I should receive a response containing information about the generated sales, including fields such as id, customer_name, email, currency, notes, subtotal, tax, total, status, etc.
And the response status code should be 201 Created

Scenario: A user cannot generate sales from a quotation without proper permissions
Given I am authenticated as an unauthorized user
And I have the id of an existing quotation
When I send a POST request to the "/quotations/{quotation_id}/generate-sales/" endpoint
Then I should receive a response with an error message and a status code of 403 Forbidden

Scenario: A user can duplicate a quotation
Given I am authenticated as an authorized user or admin user
And I have the id of an existing quotation
When I send a POST request to the "/quotations/{quotation_id}/duplicate/" endpoint
Then I should receive a response containing information about the duplicated quotation, including fields such as id, customer_name, email, currency, notes, subtotal, tax, total, status, etc.
And the response status code should be 201 Created

Scenario: A user cannot duplicate a quotation without proper permissions
Given I am authenticated as an unauthorized user
And I have the id of an existing quotation
When I send a POST request to the "/quotations/{quotation_id}/duplicate/" endpoint
Then I should receive a response with an error message and a status code of 403 Forbidden

Scenario: A user can cancel a quotation
Given I am authenticated as an authorized user or admin user
And I have the id of an existing quotation
When I send a POST request to the "/quotations/{quotation_id}/cancel/" endpoint
Then I should receive a response containing information about the canceled quotation, including fields such as id, customer_name, email, currency, notes, subtotal, tax, total, status, etc.
And the response status code should be 201 Created

Scenario: A user cannot cancel a quotation without proper permissions
Given I am authenticated as an unauthorized user
And I have the id of an existing quotation
When I send a POST request to the "/quotations/{quotation_id}/cancel/" endpoint
Then I should receive a response with an error message and a status code of 403 Forbidden