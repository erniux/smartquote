Feature: Sales Module Tests

Scenario: Valid Scenarios for Sale Model
  Given a new sale is created with valid data
  When the sale is saved
  Then its status should be "pending" by default
  And its quotation should exist and contain customer details
  And it should have an initial date of sale
  And its total amount should be zero if not provided
  And it should not have delivery or warranty dates set initially
  And it should have no notes

Scenario: Setting Delivery and Warranty Dates for a Sale
  Given a new sale is created with valid data
  When the deliver_and_warranty method is called with delivery_days and warranty_days
  Then the delivery date should be set to current date plus delivery_days
  And the warranty end date should be set to current date plus warranty_days

Scenario: Updating Sale Status based on Payments
  Given a new sale is created with valid data
  When a payment with an amount less than total amount is added
  Then the status of the sale should be "partially_paid"
  When all payments equal or exceed the total amount
  Then the status of the sale should be "paid"

Scenario: Creating Invoices for Paid Sales
  Given a paid sale exists with valid data
  When the mark_as_closed method is called
  Then an invoice should be created
  And the invoice number should be generated automatically
  And subtotal, tax and total amount of the invoice should match the sale's amounts
  And the invoice PDF file should be saved and its URL returned
  And an email with the invoice PDF attached should be sent to the customer

Scenario: Invalid Scenarios for Sale Model
  Given a new sale is created with invalid data (e.g., missing quotation or total_amount)
  When the save method is called
  Then it should raise a validation error
