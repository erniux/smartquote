```feature
Feature: Companies Views - List, Detail and Create

Scenario: Validate list companies page displays all existing companies correctly
    Given I am logged in as an administrator
    And I navigate to the /companies/ list URL
    When I see a table with columns "Name", "Logo", "Address", "Phone", "Email", "Website", "RFC" and "Created At"
    And I see each row contains data from all fields of a company object
    Then the table should display all existing companies in the database

Scenario: Validate creating a new company with valid data
    Given I am logged in as an administrator
    And I navigate to the /companies/ create URL
    When I fill out the form with valid values for "Name", "Logo", "Address", "Phone", "Email", "Website", "RFC"
    And I click on the submit button
    Then a new company should be created in the database with the entered data
    And I should be redirected to the list of companies page

Scenario: Validate creating a new company with invalid data - missing required fields
    Given I am logged in as an administrator
    And I navigate to the /companies/ create URL
    When I fill out the form without entering values for some required fields like "Name" or "Email"
    And I click on the submit button
    Then I should see an error message indicating the missing fields
    And I should still be on the same page (create company)

Scenario: Validate creating a new company with invalid data - invalid email format
    Given I am logged in as an administrator
    And I navigate to the /companies/ create URL
    When I fill out the form with a non-valid email address like "example.com"
    And I click on the submit button
    Then I should see an error message indicating the invalid email format
    And I should still be on the same page (create company)

Scenario: Validate creating a new company with invalid data - logo too large
    Given I am logged in as an administrator
    And I navigate to the /companies/ create URL
    When I upload a logo image that exceeds the allowed size limit
    And I click on the submit button
    Then I should see an error message indicating the invalid logo size
    And I should still be on the same page (create company)

Scenario: Validate viewing a company detail page with existing data
    Given there is a company in the database with valid data
    And I am logged in as an administrator
    When I navigate to the /companies/ <company_id>/ URL
    Then I should see the name, logo, address, phone, email, website, rfc, and created at of the selected company

Scenario: Validate editing a company with valid data
    Given there is a company in the database with valid data
    And I am logged in as an administrator
    When I navigate to the /companies/ <company_id>/edit/ URL
    And I modify some fields like name, address, phone, email, website or rfc
    And I click on the submit button
    Then the modified data should be updated in the database for the selected company
    And I should be redirected to the detail view of the edited company

Scenario: Validate editing a company with invalid data - missing required fields
    Given there is a company in the database with valid data
    And I am logged in as an administrator
    When I navigate to the /companies/ <company_id>/edit/ URL
    And I modify some fields like name, address, phone, email, website or rfc but leave out required fields
    And I click on the submit button
    Then I should see an error message indicating the missing fields
    And I should still be on the same page (edit company)

Scenario: Validate editing a company with invalid data - logo too large
    Given there is a company in the database with valid data
    And I am logged in as an administrator
    When I navigate to the /companies/ <company_id>/edit/ URL
    And I upload a logo image that exceeds the allowed size limit
    And I click on the submit button
    Then I should see an error message indicating the invalid logo size
    And I should still be on the same page (edit company)
```