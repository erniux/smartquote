Feature: Sales API

Scenario: List sales with pagination and filtering
Given I am authenticated as an admin user
When I send a GET request to '/api/sales/'
Then the status code should be 200
And the content-type should be 'application/json'
And the response contains a JSON object with keys "count", "next", "previous", and "results"
And each result in "results" contains keys "id", "quotation_id", "quotation_name", "quotation_email", "total_amount", "status", "sale_date", "delivery_date", "warranty_end", "notes"
But if a filter query parameter "status" is provided, the results should only contain sales with the specified status
And if pagination query parameters "page" and "page_size" are provided, the results should be paginated accordingly
And if no filter or pagination parameters are provided, all sales should be returned (default page is 1, default page size is 20)

Scenario: Create a new sale with valid data
Given I am authenticated as an admin user
When I send a POST request to '/api/sales/' with valid JSON data for a new sale
Then the status code should be 201
And the content-type should be 'application/json'
And the response contains a JSON object with keys "id", "quotation_id", "total_amount", "status", "sale_date", "delivery_date", "warranty_end", "notes"
And if delivery_date and warranty_end are not provided, they should be set to their default values
And if I send a GET request to '/api/sales/{id}', the returned sale should match the created one
And if I send a PUT request to '/api/sales/{id}/update_status' with a valid status, the sale's status should be updated
And if I send a PUT request to '/api/sales/{id}/set_delivery_and_warranty' with valid delivery_days and warranty_days, the sale's delivery_date and warranty_end should be set accordingly

Scenario: Update a sale with valid data
Given I am authenticated as an admin user
When I send a PUT request to '/api/sales/{id}' with valid JSON data for updating a sale
Then the status code should be 200
And the content-type should be 'application/json'
And the response contains a JSON object with keys "id", "quotation_id", "total_amount", "status", "sale_date", "delivery_date", "warranty_end", "notes"
And if I send a GET request to '/api/sales/{id}', the returned sale should match the updated one

Scenario: Retrieve an invoice for a sale
Given I am authenticated as an admin user
When I send a GET request to '/api/sales/{sale_id}/invoice/'
Then the status code should be 200
And the content-type should be 'application/json'
And if there is no invoice for the sale, the response should contain an empty JSON object
And if there is an invoice for the sale, the response contains a JSON object with keys "id", "invoice_number", "subtotal", "tax", and "total"

Scenario: Mark a sale as delivered
Given I am authenticated as an admin user
When I send a POST request to '/api/sales/{id}/mark_delivered'
Then the status code should be 200
And the content-type should be 'application/json'
And if I send a GET request to '/api/sales/{id}', the returned sale's status should be "delivered" and its delivery_date should be set to the current date

Scenario: Mark a sale as closed, generate invoice, and send email
Given I am authenticated as an admin user
When I send a POST request to '/api/sales/{id}/mark_closed'
Then the status code should be 200
And the content-type should be 'application/json'
And if I send a GET request to '/api/sales/{id}', the returned sale's status should be "closed"
And if I check the invoices, there should be an invoice for the sale with the correct subtotal, tax, and total
And if I check my emails, I should receive an email with the invoice as an attachment

Scenario: Create a new payment for a sale
Given I am authenticated as an admin user
When I send a POST request to '/api/sales/{id}/add_payment' with valid JSON data for a new payment
Then the status code should be 201
And the content-type should be 'application/json'
And the response contains a JSON object with keys "id", "payment_date", "amount", "method"
And if I send a GET request to '/api/sales/{id}', the returned sale's payments should contain the new payment

Scenario: Retrieve a list of payments for a sale
Given I am authenticated as an admin user
When I send a GET request to '/api/sales/{id}/payments/'
Then the status code should be 200
And the content-type should be 'application/json'
And the response contains a JSON array of payments with keys "id", "payment_date", "amount", "method"

Scenario: Check permissions for updating sales, adding payments, and marking as delivered or closed
Given I am authenticated as a user without proper permissions
When I try to perform any of the following actions: create/update a sale, add a payment, or mark as delivered or closed
Then the status code should be 403
And the content-type should be 'application/json'
And the response contains an error message indicating that the user does not have permission to perform the action