Feature: Quote List Component

Scenario: Viewing a quote
Given I am on the quote list page
When I select a quote from the list
Then I should see a modal with details of the selected quote

Scenario: Editing a draft quote
Given I am on the quote list page
And I have a quote in draft status
When I select the quote and click edit
Then I should be able to modify the quote details

Scenario: Duplicating a cancelled or sold quote
Given I am on the quote list page
And I have a quote that is cancelled or sold
When I select the quote and click duplicate
Then I should see a new quote with the same details as the original one but with different id

Scenario: Cancelling a quote
Given I am on the quote list page
And I have a quote that can be cancelled
When I click cancel on the quote card or in the modal
Then a modal should appear asking for a reason for cancellation
And after providing a reason, the quote should be cancelled and removed from the list

Scenario: Generating a sale from a confirmable quote
Given I am on the quote list page
And I have a quote that is not confirmed or cancelled and does not have a sale
When I click generate sale on the quote card or in the modal
Then a new sale should be created with details of the selected quote