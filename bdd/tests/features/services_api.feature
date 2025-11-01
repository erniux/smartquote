Feature: Services API

Scenario: Retrieve a metal price with symbol parameter
Given the client sends a GET request to "/metal-price/" with "symbol" parameter
And the provided symbol exists in database
When the server processes the request
Then it returns the metal price data serialized as JSON

Scenario: Retrieve a metal price not found in database
Given the client sends a GET request to "/metal-price/" with a non-existing symbol
When the server processes the request
Then it returns an error message "No se encontró precio para [symbol]" as JSON

Scenario: Get prices from Yahoo Finance
Given the client sends a GET request to "/yfinance-prices/"
When the server processes the request
Then it returns the latest metal prices from Yahoo Finance as JSON

Scenario: Update metal prices from database
Given the client sends a POST request to "/update-prices/"
When the server processes the request and executes `update_prices` command
Then it returns a success message "Precios y tasas actualizados correctamente" as JSON

Scenario: Get prices locales (converted to MXN or another currency)
Given the client sends a GET request to "/price-local/"
When the server processes the request
Then it returns the metal prices with their corresponding local prices serialized as JSON