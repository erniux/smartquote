Feature: Reports UI

Scenario: Navigation
Given the user is on the homepage
When the user clicks on "Reports" in the navigation bar
Then the user should be redirected to the QuotationsReport page

Scenario: Login
Given the user is not logged in
When the user tries to access a protected report page (QuotationsReport or SalesReport)
Then the user should be redirected to the login page

Scenario: Logout
Given the user is logged in
When the user clicks on "Logout" in the navigation bar
Then the user should be logged out and redirected to the homepage

Scenario: QuotationsReport - Fetch Data
Given the user is on the QuotationsReport page
When the user does not select a status filter
Then the system should fetch all quotations and display them in the table

Scenario: QuotationsReport - Filter by Status
Given the user is on the QuotationsReport page
When the user selects a specific status filter
Then the system should fetch quotations with that status and display them in the table

Scenario: QuotationsReport - Export CSV
Given the user is on the QuotationsReport page with filtered quotations
When the user clicks on "Export CSV"
Then a CSV file should be downloaded containing the displayed data

Scenario: SalesReport - Fetch Data
Given the user is on the SalesReport page
When the user does not set any date filter
Then the system should fetch all sales and display them in the table

Scenario: SalesReport - Filter by Date Range
Given the user is on the SalesReport page
When the user sets a start and end date for the filter
Then the system should fetch sales within that date range and display them in the table

Scenario: SalesReport - Export CSV
Given the user is on the SalesReport page with filtered sales
When the user clicks on "Export CSV"
Then a CSV file should be downloaded containing the displayed data