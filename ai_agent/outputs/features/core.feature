Feature: Core Module - Models, Serializers and Views

Scenario: Valid product creation with all fields
  Given I have a valid product data with name, description, price, margin, unit, metal_symbol and image
  When I create the product using the ProductViewSet
  Then the product should be created successfully and returned in the response

Scenario: Invalid product creation without required fields
  Given I have an invalid product data without required fields (name or price)
  When I create the product using the ProductViewSet
  Then an error response should be returned indicating the missing field(s)

Scenario: Update dynamic price for a product
  Given I have a product with a dynamic_price_source
  When I call the update_dynamic_price method on the product instance
  Then the product's price should be updated if the API response is successful

Scenario: Update price from metal symbol
  Given I have a product with a valid metal_symbol
  When I call the update_price_from_metal method on the product instance
  Then the product's price should be updated using the last available MetalPrice for the given metal_symbol

Scenario: CSV layout retrieval
  Given I send a GET request to the csv_layout action of ProductViewSet
  When the csv_layout method is executed
  Then a valid CSV file with correct headers should be returned as an attachment

Scenario: Massive product creation from a CSV file
  Given I have a valid CSV file with required fields (name, description, price, margin, unit, metal_symbol)
  When I send a POST request to the upload_csv action of ProductViewSet with the CSV file as form data
  Then the products should be created successfully and returned in the response
