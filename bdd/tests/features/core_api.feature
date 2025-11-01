Feature: Core API

Scenario: Auth and List Products
Given user is authenticated
When user sends GET request to /products
Then status code should be 200
And response should contain a list of products with keys: name, id, description, price, margin, unit, metal_symbol, created_at, updated_at

Scenario: CRUD Product with Valid Data
Given user is authenticated
When user sends POST request to /products with valid data
Then status code should be 201
And response should contain created product details with keys: name, id, description, price, margin, unit, metal_symbol, created_at, updated_at

Scenario: CRUD Product with Missing Data
Given user is authenticated
When user sends POST request to /products with missing data
Then status code should be 400
And response should contain error message for missing fields

Scenario: Update Product Valid Data
Given user is authenticated and product exists
When user sends PUT request to /products/<product_id> with valid data
Then status code should be 200
And response should contain updated product details with keys: name, id, description, price, margin, unit, metal_symbol, created_at, updated_at

Scenario: Update Product Invalid Data
Given user is authenticated and product exists
When user sends PUT request to /products/<product_id> with invalid data
Then status code should be 400
And response should contain error message for invalid fields

Scenario: Delete Product
Given user is authenticated and product exists
When user sends DELETE request to /products/<product_id>
Then status code should be 204
And response should be empty

Scenario: Get Product by ID
Given user is authenticated and product exists
When user sends GET request to /products/<product_id>
Then status code should be 200
And response should contain product details with keys: name, id, description, price, margin, unit, metal_symbol, created_at, updated_at

Scenario: Validate Dynamic Price Source
Given user is authenticated and product with dynamic_price_source exists
When user sends GET request to /products/<product_id>/update_dynamic_price
Then status code should be 200 or 404 (if product not found)
And response should contain updated price if successful or error message otherwise

Scenario: Update Price from Metal Symbol
Given user is authenticated and product with metal_symbol exists
When user sends GET request to /products/<product_id>/update_price_from_metal
Then status code should be 200, 404 (if product or metal_price not found) or 500 (exception thrown during execution)
And response should contain updated price if successful or error message otherwise

Scenario: Upload CSV with Products
Given user is authenticated
When user sends POST request to /products/csv_layout
Then status code should be 200
And response should contain csv layout for products (column headers)

Scenario: Upload CSV with Products (Valid Data)
Given user is authenticated and has CSV with valid product data
When user sends POST request to /products/upload_csv with CSV data
Then status code should be 201
And response should contain number of products created and list of names of the created products

Scenario: Upload CSV with Products (Invalid Data)
Given user is authenticated and has CSV with invalid product data
When user sends POST request to /products/upload_csv with CSV data
Then status code should be 400
And response should contain error message for each row with errors