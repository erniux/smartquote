Feature: Quotation Management API
  As a salesperson or manager,
  I want to manage quotations for sales transactions
  So that I can create, update, delete, and search quotations effectively.

  Scenario: Create a new quotation
    Given the user is authenticated as a manager
    When the user sends a POST request to '/api/quotations/' with valid data for a new quotation
    Then the server should return a 201 Created response
    And the created quotation should have a 'draft' status
    And the 'subtotal', 'tax', and 'total' fields should be calculated correctly based on the items and expenses

  Scenario: Retrieve a single quotation
    Given the user is authenticated as a salesperson or manager
    When the user sends a GET request to '/api/quotations/{id}/' where {id} is the ID of an existing quotation
    Then the server should return a 200 OK response
    And the response body should contain the details of the requested quotation

  Scenario: Update an existing quotation
    Given the user is authenticated as a manager
    When the user sends a PUT request to '/api/quotations/{id}/' where {id} is the ID of an existing quotation, with updated data for the quotation
    Then the server should return a 200 OK response
    And the updated fields in the response body should match the sent data

  Scenario: Delete a quotation
    Given the user is authenticated as a manager
    When the user sends a DELETE request to '/api/quotations/{id}/' where {id} is the ID of an existing quotation
    Then the server should return a 204 No Content response

  Scenario: Generate a sale from a quotation
    Given the user is authenticated as a manager
    When the user sends a POST request to '/api/quotations/{id}/generate_sale/' where {id} is the ID of an existing 'confirmed' quotation
    Then the server should return a 201 Created response
    And a new sale should be created with the delivery and warranty dates set correctly
    And the status of the original quotation should be updated to 'confirmed'

  Scenario: Duplicate a quotation
    Given the user is authenticated as a manager
    When the user sends a POST request to '/api/quotations/{id}/duplicate/' where {id} is the ID of an existing quotation
    Then the server should return a 201 Created response
    And a new draft quotation should be created with the same items and expenses as the original quotation

  Scenario: Cancel a quotation
    Given the user is authenticated as a manager or admin
    When the user sends a POST request to '/api/quotations/{id}/cancel_quotation/' where {id} is the ID of an existing quotation, with a valid cancellation reason
    Then the server should return a 200 OK response
    And the status of the cancelled quotation should be updated to 'cancelled' in the response body
    And the cancellation reason and timestamp should be saved in the database for the cancelled quotation
```