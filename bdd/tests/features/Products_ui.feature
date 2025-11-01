Feature: Products UI

Scenario: Navigation
Given user is on the homepage
When user clicks "Productos" in navigation
Then user should be on Products page

Scenario: Loading Products
Given user is on Products page
When initial page load occurs
Then loading state should be true
And no products are displayed

Scenario: Fetching Products Success
Given user is on Products page with loading state as true
When fetchProducts function is called
Then loading state should be false
And products are displayed

Scenario: Fetching Products Error
Given user is on Products page with loading state as true
When an error occurs while fetching products
Then toast message "❌ No se pudieron cargar los productos" is displayed
And loading state remains false

Scenario: Search Bar Functionality
Given user is on Products page
When user enters search term in the search bar and presses enter
Then filtered products are displayed based on the entered search term

Scenario: CSV Upload Success
Given user is on Products page with file input field hidden
When user clicks "📤 Cargar CSV" button and selects a .csv file
Then file is selected and handleCSVUpload function is called
And toast message for successful CSV upload is displayed
And products are reloaded

Scenario: CSV Upload Error
Given user is on Products page with file input field hidden
When user clicks "📤 Cargar CSV" button and does not select any file
Then no file is selected
Then toast message "❌ Error al cargar CSV" is displayed

Scenario: Download Layout Success
Given user is on Products page
When user clicks "📥 Descargar Layout" button
Then downloadProductCSVLayout function is called
And toast message for successful layout download is displayed

Scenario: Download Layout Error
Given user is on Products page
When user clicks "📥 Descargar Layout" button
Then an error occurs while downloading the layout
Then toast message "❌ No se pudo descargar el layout" is displayed

Scenario: New Product Modal Open Success
Given user is on Products page
When user clicks "➕ Nuevo Producto" button
Then ProductModal opens

Scenario: New Product Modal Close Success
Given ProductModal is open
When user clicks close button or presses escape key
Then ProductModal closes

Scenario: New Product Modal Success
Given ProductModal is open
And user fills the form and submits it correctly
Then product is added successfully
And toast message for successful addition is displayed
And products are reloaded

Scenario: New Product Modal Error
Given ProductModal is open
And user fills the form with invalid data and submits it
Then an error occurs while adding the product
Then toast message "❌ Error al agregar el producto" is displayed