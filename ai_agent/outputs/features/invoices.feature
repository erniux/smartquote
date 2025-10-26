```
Feature: Invoices - View Invoice Details
  As a user, I want to view the details of an invoice so that I can verify its information.

  Scenario: View valid invoice details
    Given I am on the invoice details page for a valid invoice
    When I view the page
    Then I should see the following details:
      | Field           | Expected Value                               |
      |-----------------|---------------------------------------------|
      | Invoice Number  | [Invoice number]                            |
      | Issue Date      | [Issue date]                                |
      | Subtotal        | [Subtotal]                                 |
      | Tax             | [Tax]                                       |
      | Total           | [Total]                                    |
      | PDF File        | A link to download the invoice PDF file is present |

  Scenario: View non-existing invoice details
    Given I am on the invoice details page for a non-existing invoice number
    When I view the page
    Then I should see an error message stating "Invoice not found"

Feature: Invoices - Create new invoice
  As a system, I want to create a new invoice when a sale is created so that sales can be invoiced.

  Scenario: Create valid invoice for valid sale
    Given A valid sale exists
    When The system creates an invoice for the sale
    Then A new invoice should be created with:
      | Field           | Expected Value                               |
      |-----------------|---------------------------------------------|
      | Invoice Number  | [Newly generated invoice number]            |
      | Issue Date      | [Current date and time]                     |
      | Subtotal        | [Sale subtotal]                             |
      | Tax             | [Calculated tax based on subtotal and tax rate]|
      | Total           | [Subtotal + calculated tax]                  |
      | PDF File        | A PDF file is generated and saved in the correct location   |

  Scenario: Create invoice for sale with no items
    Given A valid sale exists but it has no items
    When The system creates an invoice for the sale
    Then An error message should be displayed stating "Sale cannot have zero items"

Feature: Invoices - Update existing invoice
  As a user, I want to update the details of an existing invoice so that I can make corrections.

  Scenario: Update valid invoice details
    Given I am on the invoice details page for an existing invoice
    When I update the invoice details and submit the form
    Then The updated invoice details should be saved:
      | Field           | New Value                                |
      |-----------------|----------------------------------------|
      | Subtotal        | [New subtotal value]                   |
      | Tax             | [New tax value]                         |
      | Total           | [New total value]                      |
      | PDF File        | If uploaded, the new PDF file replaces the old one |

  Scenario: Update invoice details with invalid data
    Given I am on the invoice details page for an existing invoice
    When I update the invoice details with incorrect data (e.g., invalid tax percentage) and submit the form
    Then An error message should be displayed stating "Invalid data entered"
```