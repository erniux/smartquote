Feature: Invoices API

Scenario: Valid Invoice Creation
Given a valid user is authenticated
And a sale exists with quotation having a customer
When a POST request is sent to /invoices with the sale id, invoice number, issue date, subtotal, tax, and total as JSON body
Then the response status code should be 201 Created
And the response contains an invoice object with correct fields

Scenario: Incorrect Sale Reference
Given a valid user is authenticated
When a POST request is sent to /invoices with an invalid sale id, invoice number, issue date, subtotal, tax, and total as JSON body
Then the response status code should be 400 Bad Request

Scenario: Invoice Number Validation
Given a valid user is authenticated
And the next invoice number already exists
When a POST request is sent to /invoices with the same invoice number as JSON body
Then the response status code should be 409 Conflict

Scenario: Invoice Number Generation
Given a valid user is authenticated
When a GET request is sent to /invoices/next-number
Then the response status code should be 200 OK
And the response contains the next invoice number

Scenario: Retrieve Invoice by ID
Given an existing invoice
When a GET request is sent to /invoices/{id}
Then the response status code should be 200 OK
And the response contains the correct invoice object

Scenario: Update Existing Invoice
Given an existing invoice
When a PATCH request is sent to /invoices/{id} with updated subtotal, tax, and total as JSON body
Then the response status code should be 200 OK
And the response contains the updated invoice object

Scenario: Delete Invoice
Given an existing invoice
When a DELETE request is sent to /invoices/{id}
Then the response status code should be 204 No Content

Scenario: Retrieve Invoices List
Given multiple existing invoices
When a GET request is sent to /invoices
Then the response status code should be 200 OK
And the response contains a list of all invoices objects

Scenario: Invalid Invoice ID
Given an invalid invoice id
When a GET request is sent to /invoices/{id} or PATCH, DELETE requests are sent to /invoices/{id}
Then the response status code should be 404 Not Found