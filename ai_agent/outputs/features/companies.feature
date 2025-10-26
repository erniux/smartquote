```feature
Feature: Company management

  Scenario: Create a new company with valid data
    Given I am on the "Create New Company" page
    When I fill in the required fields with valid data
      | Name           | A Company Name   |
      | Logo           | <attach logo file>         # Attach an example image for the logo field
      | Address        | Company address  |
      | Phone          | Company phone     |
      | Email          | company@email.com |
      | Website        | www.company.com   |
      | RFC            | A123456789       |
    When I submit the form
    Then I should be redirected to the company list page
    And the new company should be displayed on the list with the provided data

  Scenario: Edit an existing company with valid data
    Given I am logged in and on the company list page
    When I select a company from the list to edit
    When I fill in the required fields with valid data
      | Name           | A New Company Name   |
      | Logo           | <attach new logo file>         # Attach an example image for the new logo field, different from the previous one
      | Address        | New company address  |
      | Phone          | New company phone     |
      | Email          | newcompany@email.com |
      | Website        | www.newcompany.com   |
      | RFC            | A123456789       |
    When I submit the form
    Then I should be redirected to the company list page
    And the edited company should be displayed on the list with the provided new data

  Scenario: Validate required fields are not empty
    Given I am on the "Create New Company" or the "Edit Company" page
    When I submit the form without filling in any field
    Then I should see an error message for each missing field

  Scenario: Validate invalid email format
    Given I am on the "Create New Company" or the "Edit Company" page
    When I fill in the email field with an invalid format (e.g., example.com)
    Then I should see an error message for the email field

  Scenario: Validate RFC validation
    Given I am on the "Create New Company" or the "Edit Company" page
    When I fill in the RFC field with invalid characters or incorrect length (12 digits required)
    Then I should see an error message for the RFC field
```