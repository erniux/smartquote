# ==== Tests para models.py ====
**models.py**

```python
from django.db import models

class Company(models.Model):
    name = models.CharField(max_length=150, verbose_name="Nombre de la empresa")
    logo = models.ImageField(upload_to="uploads/companies/", blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    rfc = models.CharField(max_length=13, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
```

**tests/test_models.py**

```python
import pytest
from django.test import TestCase
from .models import Company

@pytest.mark.django_db
class TestCompanyModel(TestCase):

    @pytest.mark.parametrize("name,expected_name", [
        ("Empresa S.A.", "Empresa S.A."),
        ("", None),
        (None, None)
    ])
    def test_str(self, name, expected_name):
        company = Company(name=name)
        assert company.__str__() == expected_name

    def test_create_company(self):
        company = Company(name="Empresa S.A.")
        company.save()
        assert company.name == "Empresa S.A."
        assert company.created_at is not None
```

**gherkin.feature**

```feature
Feature: Company Model Tests
  As a developer, I want to ensure the Company model behaves correctly

Scenario Outline: Str Representation
  Given a Company instance with name "<name>"
  When I call __str__()
  Then it should return the same value as "<expected_name>"

Examples:
| name | expected_name |
| "Empresa S.A." | "Empresa S.A." |
| "" | None |
| None | None |

Scenario: Create and Save a Company
  Given no companies exist in the database
  When I create a new Company with name "Empresa S.A."
  Then it should have been saved correctly
```
Note that I've kept the code concise and focused on testing the `Company` model. The tests cover the `__str__` method and the creation of a new company instance, including checking the `created_at` field.

# ==== Tests para views.py ====
**views.py**

```python
from django.shortcuts import render

class HelloWorldView:
    def get(self, request):
        return render(request, 'hello_world.html', {'message': 'Hello World!'})

def hello_view(request):
    return render(request, 'hello_world.html', {'message': 'Hello View!'})
```

**tests.py**

```python
import pytest
from django.test import TestCase
from views import HelloWorldView, hello_view

class TestViews(TestCase):
    @pytest.mark.django_db(transaction=True)
    def test_hello_world_view(self):
        request = lambda: None  # Mock request
        view = HelloWorldView()
        response = view.get(request)
        assert response.status_code == 200
        assert 'Hello World!' in str(response.content)

    @pytest.mark.django_db(transaction=True)
    def test_hello_view(self):
        request = lambda: None  # Mock request
        view = hello_view()
        response = view(request)
        assert response.status_code == 200
        assert 'Hello View!' in str(response.content)
```

**gherkin.feature**

```gherkin
Feature: Views

Scenario: Hello World View
    Given the "hello_world" view is requested via GET
    Then the response status code should be 200
    And the response content should contain "Hello World!"

Scenario: Hello View
    Given the "hello_view" view is requested via GET
    Then the response status code should be 200
    And the response content should contain "Hello View!"
```

# ==== Tests para models.py ====
**models.py**
```python
from django.db import models
from decimal import Decimal

class Product(models.Model):
    # ...

    def update_dynamic_price(self):
        """Actualiza el precio si tiene fuente externa"""
        from services.api_clients import get_metal_price
        if self.dynamic_price_source:
            new_price = get_metal_price(self.dynamic_price_source)
            if new_price:
                self.price = new_price
                self.save()

    def update_price_from_metal(self):
        """
        Si el producto tiene un símbolo de metal asignado, 
        actualiza su precio automáticamente con el último valor guardado.
        """
        if not self.metal_symbol:
            return None

        from services.models import MetalPrice
        try:
            metal = MetalPrice.objects.filter(symbol=self.metal_symbol).order_by("-last_updated").first()
            if metal:
                old_price = self.price
                self.price = Decimal(metal.price_usd)
                self.save()
                return f"Precio actualizado de {old_price} → {self.price} USD"
        except Exception as e:
            print(f"⚠️ Error al actualizar precio de {self.name}: {e}")
            return None

    # ...
```

**pruebas_unitarias.py**
```python
import pytest
from django.test import TestCase
from .models import Product

class TestProductModel(TestCase):
    @pytest.mark.django_db(transaction=True)
    def test_update_dynamic_price(self):
        product = Product(name="Test", dynamic_price_source="API-TEST")
        product.update_dynamic_price()
        assert product.price != Decimal(0)

    @pytest.mark.django_db(transaction=True)
    def test_update_price_from_metal(self):
        metal_price = MetalPrice(symbol="ALU", price_usd=Decimal("10.50"))
        metal_price.save()

        product = Product(name="Test", metal_symbol="ALU")
        result = product.update_price_from_metal()
        assert product.price == Decimal("10.50")
        if result:
            print(result)

    @pytest.mark.django_db(transaction=True)
    def test_update_price_from_metal_no_metal(self):
        product = Product(name="Test", metal_symbol="")
        result = product.update_price_from_metal()
        assert result is None
```

**gherkin.feature**
```gherkin
Feature: Product model tests

Scenario: Update dynamic price
  Given a product with name "Test" and dynamic price source "API-TEST"
  When the product updates its dynamic price
  Then the product's price should be updated

Scenario: Update price from metal
  Given a metal price with symbol "ALU" and price USD 10.50
  And a product with name "Test" and metal symbol "ALU"
  When the product updates its price from metal
  Then the product's price should be 10.50 USD

Scenario: Update price from metal (no metal)
  Given a product with name "Test" and no metal symbol
  When the product updates its price from metal
  Then the result should be None
```
Nota: Reemplaza `services.models` con el path correcto para tu proyecto.

# ==== Tests para serializers.py ====
**serializers.py**
```
from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "description",
            "price",
            "margin",
            "unit",
            "image",
            "image_url",
            "metal_symbol",
            "created_at",
            "updated_at",
        ]

    def get_image_url(self, obj):
        request = self.context.get("request")
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None

# Tests
import pytest

@pytest.mark.parametrize(
    "product_data, expected_image_url",
    [
        ({}, None),
        (
            {"image": "/path/to/image.jpg"},
            "/path/to/serializers/product/image.jpg",
        ),
    ],
)
def test_product_serializer(product_data, expected_image_url):
    serializer = ProductSerializer(data=product_data)
    assert serializer.is_valid()
    if product_data.get("image"):
        assert serializer.data["image_url"] == expected_image_url
    else:
        assert serializer.data.get("image_url") is None

# Gherkin Feature/Scenario
Feature: Product Serializer
  As a developer, I want to test the ProductSerializer to ensure it correctly serializes product data and generates image URLs.

Scenario: Valid product data with an image URL
  Given a valid product with an image
  When the product serializer is used
  Then the serialized product should have the correct image URL

Scenario: Invalid product data without an image URL
  Given an invalid product with no image
  When the product serializer is used
  Then the serialized product should not have an image URL

# ==== Tests para views.py ====
**views.py**

```python
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import HttpResponse
import csv
from io import TextIOWrapper
from .models import Product
from .serializers import ProductSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by("-created_at")
    serializer_class = ProductSerializer
    search_fields = ["name", "metal_symbol"]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @action(detail=False, methods=["get"])
    def csv_layout(self, request):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="productos_layout.csv"'

        writer = csv.writer(response)
        headers = ["name", "description", "price", "margin", "unit", "metal_symbol"]
        writer.writerow(headers)
        writer.writerow(["Ejemplo Tornillo", "Acero galvanizado", "1.25", "5", "pieza", "IRON"])
        writer.writerow(["Ejemplo PVC", "Tubo presión", "0.95", "3", "metro", "PVC"])

        return response

    @action(detail=False, methods=["post"])
    def upload_csv(self, request):
        try:
            file = request.FILES.get("file")
            if not file:
                return Response({"error": "No se recibió ningún archivo CSV."},
                                status=status.HTTP_400_BAD_REQUEST)

            decoded_file = TextIOWrapper(file, encoding="utf-8")
            reader = csv.DictReader(decoded_file)

            created = []
            for row in reader:
                product = Product.objects.create(
                    name=row.get("name"),
                    description=row.get("description", ""),
                    price=row.get("price") or 0,
                    margin=row.get("margin") or 0,
                    unit=row.get("unit", "pieza"),
                    metal_symbol=row.get("metal_symbol", ""),
                )
                created.append(product.name)

            return Response(
                {"message": f"{len(created)} productos creados correctamente.", "productos": created},
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response({"error": f"Error procesando CSV: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
```

**tests.py**

```python
import unittest
from django.test import TestCase, RequestFactory
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED
from rest_framework.exceptions import ParseError

from .views import ProductViewSet


class TestProductViewSet(unittest.TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_csv_layout(self):
        request = self.factory.get("products/csv-layout/")
        view = ProductViewSet()
        response = view.csv_layout(request)
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_upload_csv_valid_file(self):
        request = self.factory.post("products/upload-csv/", data={"file": "valid_file.csv"})
        view = ProductViewSet()
        response = view.upload_csv(request)
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertIn("message", response.data)

    def test_upload_csv_invalid_file(self):
        request = self.factory.post("products/upload-csv/", data={"file": "invalid_file.txt"})
        view = ProductViewSet()
        response = view.upload_csv(request)
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_upload_csv_error_processing(self):
        request = self.factory.post("products/upload-csv/", data={"file": "error_file.csv"})
        view = ProductViewSet()
        response = view.upload_csv(request)
        self.assertEqual(response.status_code, HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("error", response.data)


if __name__ == "__main__":
    unittest.main()


**features/product_view_set.feature**

Feature: Product View Set
  As a developer
  I want to interact with the Product View Set API
  So that I can create, read, update and delete products

Scenario 1: Get CSV layout
  Given I send a GET request to the "products/csv-layout/" endpoint
  Then the response status code should be 200 OK
  And the response content type is text/csv

Scenario 2: Upload valid CSV file
  Given I send a POST request to the "products/upload-csv/" endpoint with a valid CSV file
  Then the response status code should be 201 Created
  And the response contains the message "X products created correctly"

Scenario 3: Upload invalid CSV file
  Given I send a POST request to the "products/upload-csv/" endpoint with an invalid CSV file
  Then the response status code should be 400 Bad Request
  And the response contains the error "No se recibió ningún archivo CSV."

Scenario 4: Error processing CSV file
  Given I send a POST request to the "products/upload-csv/" endpoint with a CSV file that causes an error
  Then the response status code should be 500 Internal Server Error
  And the response contains the error "Error procesando CSV: X"


# ==== Tests para models.py ====
**models.py**
```
from django.db import models
from sales.models import Sale
from django.utils import timezone

class Invoice(models.Model):
    sale = models.OneToOneField("sales.Sale",
        on_delete=models.CASCADE,
        related_name="invoice", 
        verbose_name="Venta asociada")
    invoice_number = models.CharField(max_length=20, unique=True)
    issue_date = models.DateField(default=timezone.now)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    tax = models.DecimalField(max_digits=12, decimal_places=2)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    pdf_file = models.FileField(upload_to="invoices/pdfs/", blank=True, null=True)

    @staticmethod
    def next_invoice_number():
        """Genera el siguiente número de factura consecutivo."""
        last = Invoice.objects.order_by("-id").first()
        if not last:
            return "INV-0001"
        last_num = int(last.invoice_number.split("-")[1])
        return f"INV-{last_num+1:04d}"

    def __str__(self):
        return f"Factura {self.invoice_number} - {self.sale.quotation.customer_name}"


# Tests using pytest
import pytest

@pytest.mark.django_db
def test_next_invoice_number():
    # Test 1: First invoice number
    assert Invoice.next_invoice_number() == "INV-0001"
    
    # Test 2: Second invoice number (incremented)
    Invoice.objects.create(invoice_number="INV-0001")
    assert Invoice.next_invoice_number() == "INV-0002"

@pytest.mark.django_db
def test_invoice_str():
    sale = Sale()
    sale.quotation.customer_name = "John Doe"
    invoice = Invoice(sale=sale, invoice_number="INV-1234", issue_date=timezone.now())
    assert str(invoice) == "Factura INV-1234 - John Doe"


# Gherkin feature
Feature: Invoice Model

Scenario 1: Next invoice number generation
    Given the database is empty
    When we generate the next invoice number
    Then it should be "INV-0001"
    
Scenario 2: Incremental invoice numbering
    Given there are invoices in the database
    When we generate the next invoice number
    Then it should be incremented by one (e.g. "INV-0002")
    
Scenario 3: Invoice string representation
    Given an existing sale and invoice
    When we convert the invoice to a string
    Then it should contain the invoice number and customer name

# ==== Tests para views.py ====
**views.py**
```python
from django.shortcuts import render

def index(request):
    return render(request, 'index.html')

def detail(request, pk):
    return render(request, 'detail.html', {'pk': pk})
```

**tests_views.py**
```python
import pytest
from views import index, detail

@pytest.mark.django_db
class TestViews:
    def test_index(self):
        request = {'GET': {}, 'POST': {}}
        response = index(request)
        assert response.status_code == 200

    def test_detail(self):
        request = {'GET': {}, 'POST': {}}
        response = detail(request, pk=1)
        assert response.status_code == 200
```

**gherkin.feature**
```feature
Feature: Views
  As a user
  I want to ensure the views are functioning correctly
  So that I can trust my application

Scenario: Index view returns 200
  Given the index view is called with GET request
  Then the response status code should be 200

Scenario: Detail view returns 200 with correct pk
  Given the detail view is called with GET request and pk=1
  Then the response status code should be 200
```

# ==== Tests para models.py ====
**models.py**
```python
from django.db import models
from django.utils import timezone
from decimal import Decimal, ROUND_HALF_UP
from core.models import Product
from services.models import MetalPrice, CurrencyRate
from companies.models import Company


MONEY_FIELD = dict(max_digits=14, decimal_places=2, default=0)

class Quotation(models.Model):
    # ...

    def test_calculate_totals(self):
        quotation = Quotation()
        item1 = QuotationItem(quotation=quotation, product=Product(), quantity=2, unit_price=10.5)
        expense1 = QuotationExpense(quotation=quotation, name="Material A", quantity=3, unit_cost=5.25)

        quotation.items.add(item1)
        quotation.expenses.add(expense1)

        subtotal, tax, total = quotation.calculate_totals()

        assert subtotal.quantize(Decimal("0.01")) == Decimal("20.50")
        assert tax.quantize(Decimal("0.01")) == Decimal("3.30")
        assert total.quantize(Decimal("0.01")) == Decimal("23.80")

    def test_confirm(self):
        quotation = Quotation()
        sale = quotation.confirm()

        assert quotation.status == "confirmed"
        assert quotation.confirmed_at is not None
        assert sale.total_amount.quantize(Decimal("0.01")) == quotation.total.quantize(Decimal("0.01"))

    def test_save(self):
        quotation = Quotation(status="confirmed")
        quotation.save()

        assert quotation.confirmed_at is not None

    def test_str(self):
        quotation = Quotation(customer_name="John Doe", date=timezone.now())

        assert str(quotation) == f"Cotización #{quotation.id} - John Doe"
```

**gherkin.feature**
```python
Feature: Quotation model
  As a developer
  I want to test the Quotation model
  So that I can ensure it works correctly

Scenario: Calculate totals
  Given a quotation with two items and one expense
  When the calculate_totals method is called
  Then the subtotal, tax, and total should be calculated correctly

Scenario: Confirm a quotation
  Given a draft quotation
  When the confirm method is called
  Then the quotation status should be updated to confirmed
  And the sale should be created with the correct total amount

Scenario: Save a quotation
  Given a confirmed quotation
  When the save method is called
  Then the quotation's confirmed at date should be updated

Scenario: String representation of a quotation
  Given a quotation with a customer name
  When I print the quotation string
  Then it should contain the correct customer name and id

# ==== Tests para serializers.py ====
**pruebas_unitarias.py**

```python
import pytest
from .serializers import QuotationItemSerializer, QuotationExpenseSerializer, QuotationSerializer

@pytest.fixture
def quotation_item():
    return {
        "id": 1,
        "name": "Product 1",
        "metal_symbol": "Au",
        "price": Decimal("100.00"),
        "quantity": Decimal("10.0"),
        "unit_price": Decimal("10.0"),
    }

@pytest.fixture
def quotation_expense():
    return {
        "id": 1,
        "name": "Expense 1",
        "description": "Description 1",
        "category": "other",
        "quantity": Decimal("1.0"),
        "unit_cost": Decimal("10.0"),
        "total_cost": Decimal("10.0"),
    }

@pytest.fixture
def quotation():
    return {
        "id": 1,
        "customer_name": "Customer 1",
        "customer_email": "customer@example.com",
        "currency": "USD",
        "date": "2023-02-20T00:00:00Z",
        "subtotal": Decimal("1000.0"),
        "tax": Decimal("100.0"),
        "total": Decimal("1100.0"),
        "notes": "Notes 1",
        "items": [quotation_item()],
        "expenses": [quotation_expense()],
        "status": "active",
    }

def test_quotation_item_serializer(quotation_item):
    serializer = QuotationItemSerializer(data=quotation_item)
    assert serializer.is_valid()
    assert serializer.data["name"] == quotation_item["product"]["name"]
    assert serializer.data["metal_symbol"] == quotation_item["product"]["metal_symbol"]
    assert serializer.data["price"] == quotation_item["product"]["price"]
    assert serializer.data["quantity"] == quotation_item["quantity"]
    assert serializer.data["unit_price"] == quotation_item["unit_price"]

def test_quotation_expense_serializer(quotation_expense):
    serializer = QuotationExpenseSerializer(data=quotation_expense)
    assert serializer.is_valid()
    assert serializer.data["name"] == quotation_expense["name"]
    assert serializer.data["description"] == quotation_expense["description"]
    assert serializer.data["category"] == quotation_expense["category"]
    assert serializer.data["quantity"] == quotation_expense["quantity"]
    assert serializer.data["unit_cost"] == quotation_expense["unit_cost"]
    assert serializer.data["total_cost"] == quotation_expense["total_cost"]

def test_quotation_serializer(quotation):
    serializer = QuotationSerializer(data=quotation)
    assert serializer.is_valid()
    assert serializer.data["customer_name"] == quotation["customer_name"]
    assert serializer.data["customer_email"] == quotation["customer_email"]
    assert serializer.data["currency"] == quotation["currency"]
    assert serializer.data["date"] == quotation["date"]
    assert serializer.data["subtotal"] == quotation["subtotal"]
    assert serializer.data["tax"] == quotation["tax"]
    assert serializer.data["total"] == quotation["total"]
    assert serializer.data["notes"] == quotation["notes"]

def test_quotation_serializer_create(quotation):
    serializer = QuotationSerializer(data=quotation)
    instance = serializer.create(serializer.validated_data)
    assert instance.id is not None

def test_quotation_serializer_update(quotation):
    serializer = QuotationSerializer(instance=Quotation(**quotation), data=quotation, partial=True)
    instance = serializer.update(Quotation(**quotation), serializer.validated_data)
    assert instance.id is not None
```

**gherkin.feature**

```gherkin
Feature: Quotation Serializers
  As a developer, I want to ensure that the quotation serializers are working correctly.

Scenario: Create Quotation Item
  Given a valid quotation item payload
  When I create a new quotation item with the serializer
  Then the instance should be created successfully

Scenario: Update Quotation Item
  Given a existing quotation item
  And a valid updated quotation item payload
  When I update the quotation item with the serializer
  Then the instance should be updated successfully

Scenario: Create Quotation Expense
  Given a valid quotation expense payload
  When I create a new quotation expense with the serializer
  Then the instance should be created successfully

Scenario: Update Quotation Expense
  Given a existing quotation expense
  And a valid updated quotation expense payload
  When I update the quotation expense with the serializer
  Then the instance should be updated successfully

Scenario: Create Quotation
  Given a valid quotation payload
  When I create a new quotation with the serializer
  Then the instance should be created successfully

Scenario: Update Quotation
  Given a existing quotation
  And a valid updated quotation payload
  When I update the quotation with the serializer
  Then the instance should be updated successfully

# ==== Tests para views.py ====
**Pruebas unitarias con pytest**

```python
import pytest
from rest_framework import status
from .views import QuotationViewSet, QuotationSerializer
from .models import Sale, Quotation, QuotationItem, QuotationExpense
from django.db import transaction

@pytest.mark.django_db
class TestQuotationViewSet:
    def test_get_queryset_admin(self):
        view = QuotationViewSet()
        request = None  # Mocked request
        user = None  # Mocked user (admin)
        queryset = view.get_queryset(request, user)
        assert queryset.count() > 0

    def test_get_queryset_company_member(self):
        view = QuotationViewSet()
        request = None  # Mocked request
        user = None  # Mocked user (company member)
        queryset = view.get_queryset(request, user)
        assert queryset.count() == 1

    def test_generate_sale_manager(self):
        view = QuotationViewSet()
        request = None  # Mocked request
        user = None  # Mocked user (manager)
        quotation = None  # Mocked quotation
        response = view.generate_sale(request, pk=quotation.id)
        assert response.status_code == status.HTTP_201_CREATED

    def test_generate_sale_not_manager(self):
        view = QuotationViewSet()
        request = None  # Mocked request
        user = None  # Mocked user (not manager)
        quotation = None  # Mocked quotation
        response = view.generate_sale(request, pk=quotation.id)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_duplicate_quotation_manager(self):
        view = QuotationViewSet()
        request = None  # Mocked request
        user = None  # Mocked user (manager)
        original = None  # Mocked quotation
        response = view.duplicate(request, pk=original.id)
        assert response.status_code == status.HTTP_201_CREATED

    def test_duplicate_quotation_not_manager(self):
        view = QuotationViewSet()
        request = None  # Mocked request
        user = None  # Mocked user (not manager)
        original = None  # Mocked quotation
        response = view.duplicate(request, pk=original.id)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_cancel_quotation_manager(self):
        view = QuotationViewSet()
        request = None  # Mocked request
        user = None  # Mocked user (manager)
        quotation = None  # Mocked quotation
        response = view.cancel_quotation(request, pk=quotation.id)
        assert response.status_code == status.HTTP_200_OK

    def test_cancel_quotation_not_manager(self):
        view = QuotationViewSet()
        request = None  # Mocked request
        user = None  # Mocked user (not manager)
        quotation = None  # Mocked quotation
        response = view.cancel_quotation(request, pk=quotation.id)
        assert response.status_code == status.HTTP_403_FORBIDDEN


# Bloque de Gherkin para los casos de prueba
Feature: QuotationViewSet

Scenario: Get all quotations (admin)
    Given the user is an admin
    When I send a GET request to the quotations endpoint
    Then the response status code should be 200 and the list of quotations should not be empty

Scenario: Get own quotations (company member)
    Given the user is a company member
    When I send a GET request to the quotations endpoint
    Then the response status code should be 200 and the list of quotations should contain only one quotation

Scenario: Generate sale (manager)
    Given the user is a manager
    And there is an existing quotation
    When I send a POST request to the generate-sale endpoint for that quotation
    Then the response status code should be 201 and the quotation should have been updated with a new sale

Scenario: Duplicate quotation (manager)
    Given the user is a manager
    And there is an existing quotation
    When I send a POST request to the duplicate endpoint for that quotation
    Then the response status code should be 201 and a new quotation should have been created

Scenario: Cancel quotation (manager)
    Given the user is a manager
    And there is an existing quotation
    When I send a POST request to the cancel endpoint for that quotation
    Then the response status code should be 200 and the quotation should have been updated with a cancelled status

# ==== Tests para models.py ====
Aquí te presento las pruebas unitarias y de integración para el archivo `models.py` utilizando pytest:

**tests/test_models.py**
```python
# Test Sale model
import unittest
from models import Sale, Payment

class TestSaleModel(unittest.TestCase):
    def test_set_delivery_and_warranty(self):
        sale = Sale()
        sale.set_delivery_and_warranty(delivery_days=7, warranty_days=90)
        self.assertEqual(sale.delivery_date.date(), date.today() + timedelta(days=7))
        self.assertEqual(sale.warranty_end.date(), date.today() + timedelta(days=90))

    def test_update_status(self):
        sale = Sale()
        payment1 = Payment(sale=sale, amount=models.DecimalField(**MONEY_FIELD) - 1000)
        payment2 = Payment(sale=sale, amount=models.DecimalField(**MONEY_FIELD) - 2000)
        self.assertEqual(sale.status, "pending")
        sale.save()  # Trigger update_status
        self.assertEqual(sale.status, "partially_paid")
        payment3 = Payment(sale=sale, amount=models.DecimalField(**MONEY_FIELD))
        self.assertEqual(sale.status, "paid")
        payment4 = Payment(sale=sale, amount=models.DecimalField(**MONEY_FIELD) + 1000)
        self.assertEqual(sale.status, "paid")

# Test Payment model
class TestPaymentModel(unittest.TestCase):
    def test_save(self):
        payment = Payment(sale=Sale(), amount=models.DecimalField(**MONEY_FIELD))
        payment.save()
        sale = payment.sale
        self.assertEqual(sale.status, "partially_paid")
```
Y aquí te presento el bloque de Gherkin que describe los mismos casos de prueba:
```gherkin
Feature: Sale and Payment models

Scenario: Set delivery and warranty dates
  Given a new sale is created
  When the set_delivery_and_warranty method is called with 7 days of delivery and 90 days of warranty
  Then the delivery date is 7 days from today
  And the warranty end date is 90 days from today

Scenario: Update sale status based on payments
  Given a new sale is created
  When three payments are made, one for half the total amount, one for the remaining balance, and one for the full amount
  Then the sale status is "pending" initially
  And the sale status becomes "partially_paid" after the first payment
  And the sale status becomes "paid" after the second payment
  And the sale status remains "paid" after the third payment
```

# ==== Tests para serializers.py ====
**serializers.py**
```python
from rest_framework import serializers
from .models import Sale, Payment
from invoices.models import Invoice
from invoices.pdf_utils import generate_invoice_pdf
from invoices.email_utils import send_invoice_email
from django.core.files.base import ContentFile
from decimal import Decimal
from datetime import date

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ["id", "payment_date", "amount", "method"]

class SaleSerializer(serializers.ModelSerializer):
    quotation_id = serializers.PrimaryKeyRelatedField(source="quotation", read_only=True)
    quotation_name = serializers.CharField(source="quotation.customer_name", read_only=True)
    quotation_email = serializers.EmailField(source="quotation.customer_email", read_only=True)
    quotation_company = serializers.CharField(source="quotation.company", read_only=True)
    invoice_id = serializers.SerializerMethodField()
    invoice_pdf_url = serializers.SerializerMethodField()

    def get_invoice_pdf_url(self, obj):
        """Devuelve la URL del PDF de la factura si existe."""
        if hasattr(obj, "invoice") and getattr(obj.invoice, "pdf_file", None):
            return obj.invoice.pdf_file.url
        return None

    def get_invoice_id(self, obj):
        """Devuelve el ID de la factura si existe."""
        if hasattr(obj, "invoice"):
            return obj.invoice.id
        return None

    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = Sale
        fields = [
            "id",
            "quotation_id",
            "quotation_name",
            "quotation_email",
            "quotation_company",
            "total_amount",
            "status",
            "sale_date",
            "delivery_date",
            "warranty_end",
            "notes",
            "payments",
            "invoice_id",
            "invoice_pdf_url"
        ]

    def update(self, instance, validated_data):
        """Permite actualizar estado o notas desde el frontend."""
        instance.status = validated_data.get("status", instance.status)
        instance.notes = validated_data.get("notes", instance.notes)
        instance.save()
        return instance

    # --- Acciones especiales ---
    def mark_as_delivered(self, sale: Sale):
        if sale.status in ["pending", "partially_paid", "paid"]:
            sale.status = "delivered"
            sale.delivery_date = date.today()
            sale.save()
        return sale

    def mark_as_closed(self, sale: Sale):
        """Cierra venta, genera factura y envía correo."""
        if sale.status == "delivered":
            sale.status = "closed"
            sale.warranty_end = date.today()
            sale.save()

            iva = Decimal("1.16")
            subtotal = sale.total_amount / iva
            tax = sale.total_amount - subtotal

            invoice = Invoice.objects.create(
                sale=sale,
                invoice_number=Invoice.next_invoice_number(),
                subtotal=subtotal,
                tax=tax,
                total=sale.total_amount,
            )

            pdf_response = generate_invoice_pdf(invoice)
            invoice.pdf_file.save(
                f"{invoice.invoice_number}.pdf",
                ContentFile(pdf_response.content),
                save=True,
            )

            send_invoice_email(invoice)

        return sale

    def get_invoice_id(self, obj):
        return getattr(obj.invoice, "id", None) if hasattr(obj, "invoice") else None

    def get_invoice_pdf_url(self, obj):
        """Devuelve la URL del PDF de la factura si existe."""
        try:
            if hasattr(obj, "invoice") and getattr(obj.invoice, "pdf_file", None):
                return obj.invoice.pdf_file.url
        except Exception:
            return None
        return None

# Test cases using pytest
import pytest

@pytest.mark.django_db(transaction=True)
def test_sale_serializer():
    # Create a new sale instance
    sale = Sale.objects.create(
        quotation=Quotation.objects.create(customer_name="John Doe", customer_email="john@example.com", company="ABC Inc."),
        total_amount=1000,
        status="pending",
        sale_date=date.today(),
        delivery_date=None,
        warranty_end=None,
        notes="Initial note",
    )

    # Test the serializer
    serializer = SaleSerializer(sale)
    assert serializer.data["quotation_name"] == "John Doe"
    assert serializer.data["total_amount"] == 1000
    assert serializer.data["status"] == "pending"

    # Update the sale instance
    validated_data = {"status": "delivered", "notes": "Updated note"}
    updated_sale = SaleSerializer(instance=sale, data=validated_data).update(sale, validated_data)
    assert updated_sale.status == "delivered"
    assert updated_sale.notes == "Updated note"

    # Test the mark_as_delivered method
    sale.mark_as_delivered()
    assert sale.status == "delivered"
    assert sale.delivery_date == date.today()

    # Test the mark_as_closed method
    sale.mark_as_closed()
    assert sale.status == "closed"
    assert sale.warranty_end == date.today()

# Feature file in Gherkin format
Feature: Sale Serializers
  As a developer, I want to ensure that the Sale serializers work correctly.

Scenario: Create and update a sale instance
  Given I have a quotation with customer name "John Doe", email "john@example.com", and company "ABC Inc."
  And I create a new sale instance with total amount 1000, status "pending", and notes "Initial note"
  When I serialize the sale instance using SaleSerializer
  Then the serialized data contains the correct quotation name, total amount, and status

Scenario: Update a sale instance
  Given I have an existing sale instance with status "pending" and notes "Initial note"
  And I update the sale instance with new status "delivered" and notes "Updated note"
  When I serialize the updated sale instance using SaleSerializer
  Then the serialized data contains the correct updated status and notes

Scenario: Mark a sale as delivered
  Given I have an existing sale instance with status "pending"
  When I mark the sale as delivered
  Then the sale instance has status "delivered" and delivery date set to today's date

Scenario: Mark a sale as closed
  Given I have an existing sale instance with status "delivered"
  When I mark the sale as closed
  Then the sale instance has status "closed" and warranty end date set to today's date

# ==== Tests para views.py ====
**Pruebas unitarias con pytest**
```python
# tests/test_views.py
import pytest
from rest_framework.test import APIClient
from .views import SaleViewSet

@pytest.mark.django_db
class TestSaleViews:
    def test_mark_delivered(self):
        client = APIClient()
        sale = Sale.objects.create(quotation="Quotation 1", total=100)
        response = client.post(f"/sales/{sale.id}/mark-delivered/")
        assert response.status_code == 200
        assert response.data["message"] == "Venta marcada como entregada"

    def test_mark_closed(self):
        client = APIClient()
        sale = Sale.objects.create(quotation="Quotation 1", total=100)
        response = client.post(f"/sales/{sale.id}/mark-closed/")
        assert response.status_code == 200
        assert response.data["message"] == "Venta cerrada y factura generada"

    def test_add_payment(self):
        client = APIClient()
        sale = Sale.objects.create(quotation="Quotation 1", total=100)
        data = {"amount": 50, "payment_method": "Cash"}
        response = client.post(f"/sales/{sale.id}/add-payment/", data=data)
        assert response.status_code == 201
        assert response.data["payment"]["amount"] == 50

    def test_add_payment_invalid_data(self):
        client = APIClient()
        sale = Sale.objects.create(quotation="Quotation 1", total=100)
        data = {"invalid_field": "Invalid value"}
        response = client.post(f"/sales/{sale.id}/add-payment/", data=data)
        assert response.status_code == 400
```

**Feature / Scenario**
```gherkin
Feature: Sale Views
  As a user of the sales system
  I want to be able to mark sales as delivered and closed, and add payments
  So that the sales are updated correctly

Scenario: Mark sale as delivered
  Given I have a sale with ID 1
  When I send a POST request to "/sales/1/mark-delivered/"
  Then the response status code is 200
  And the response message is "Venta marcada como entregada"

Scenario: Mark sale as closed
  Given I have a sale with ID 2
  When I send a POST request to "/sales/2/mark-closed/"
  Then the response status code is 200
  And the response message is "Venta cerrada y factura generada"

Scenario: Add payment to sale
  Given I have a sale with ID 3 and no payments
  When I send a POST request to "/sales/3/add-payment/" with data {"amount": 50, "payment_method": "Cash"}
  Then the response status code is 201
  And the response data includes a payment with amount 50

Scenario: Add payment to sale with invalid data
  Given I have a sale with ID 4 and no payments
  When I send a POST request to "/sales/4/add-payment/" with data {"invalid_field": "Invalid value"}
  Then the response status code is 400

# ==== Tests para models.py ====
**models.py**
```python
from django.db import models
from django.utils import timezone

class MetalPrice(models.Model):
    name = models.CharField(max_length=50)
    symbol = models.CharField(max_length=20)
    price_usd = models.DecimalField(max_digits=12, decimal_places=4)
    measure_units = models.CharField(max_length=20, default="")
    base_quantity = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    last_updated = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.name} ({self.symbol}) - {self.price_usd} USD"

class CurrencyRate(models.Model):
    base_currency = models.CharField(max_length=10, default="USD")
    target_currency = models.CharField(max_length=10)
    rate = models.DecimalField(max_digits=12, decimal_places=6)
    last_updated = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"1 {self.base_currency} = {self.rate} {self.target_currency}"

# test cases
import pytest

@pytest.mark.django_db(transaction=True)
def test_metal_price():
    price_usd = 100.0
    metal_price = MetalPrice(name="Aluminum", symbol="ALM", price_usd=price_usd, measure_units="tonelada métrica")
    assert metal_price.price_usd == price_usd

@pytest.mark.django_db(transaction=True)
def test_currency_rate():
    rate = 0.5
    currency_rate = CurrencyRate(base_currency="USD", target_currency="EUR", rate=rate)
    assert currency_rate.rate == rate

# Gherkin feature file
Feature: Metal Prices and Currency Rates
  As a developer, I want to ensure that metal prices and currency rates are properly stored in the database.

Scenario: Metal Price Creation
  Given a metal price with name "Aluminum", symbol "ALM" and price $100.00 USD
  When I create the metal price in the database
  Then the metal price should be stored correctly

Scenario: Currency Rate Creation
  Given a currency rate from USD to EUR with rate 0.5
  When I create the currency rate in the database
  Then the currency rate should be stored correctly

# ==== Tests para serializers.py ====
**serializers.py**
```python
from rest_framework import serializers
from decimal import Decimal
from .models import MetalPrice, CurrencyRate


class MetalPriceSerializer(serializers.ModelSerializer):
    price_with_margin_usd = serializers.SerializerMethodField()
    price_local = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()

    class Meta:
        model = MetalPrice
        fields = [
            "symbol",
            "price_usd",
            "currency",
            "last_updated",
            "base_quantity",
            "last_updated",
            "price_with_margin_usd",
            "price_local",
            "measure_units",
            "currency",
        ]

    def get_price_with_margin_usd(self, obj):
        margin = Decimal("0.00")
        request = self.context.get("request")
        if request:
            margin_param = request.query_params.get("margin")
            if margin_param:
                try:
                    margin = Decimal(margin_param)
                except:
                    pass
        return (obj.price_usd * (Decimal("1.00") + margin / Decimal("100"))).quantize(Decimal("0.01"))

    def get_currency(self, obj):
        request = self.context.get("request")
        return request.query_params.get("currency", "MXN")

    def get_price_local(self, obj):
        request = self.context.get("request")
        currency = request.query_params.get("currency", "MXN")
        rate = Decimal("1.00")

        if currency != "USD":
            rate_obj = (
                CurrencyRate.objects.filter(base_currency="USD", target_currency=currency)
                .order_by("-last_updated")
                .first()
            )
            if rate_obj:
                rate = rate_obj.rate

        margin_param = request.query_params.get("margin")
        margin = Decimal(margin_param) if margin_param else Decimal("0.00")

        price_with_margin_usd = obj.price_usd * (Decimal("1.00") + margin / Decimal("100"))
        price_local = price_with_margin_usd * rate
        return price_local.quantize(Decimal("0.01"))
```

**pruebas_unitarias.py**
```python
import pytest
from .serializers import MetalPriceSerializer

@pytest.fixture
def metal_price_serializer():
    return MetalPriceSerializer()

def test_get_price_with_margin_usd(metal_price_serializer):
    serializer = metal_price_serializer()
    obj = {"price_usd": Decimal("100.00")}
    result = serializer.get_price_with_margin_usd(obj)
    assert isinstance(result, Decimal) and result.quantize(Decimal("0.01")) == Decimal("110.00")

def test_get_currency(metal_price_serializer):
    serializer = metal_price_serializer()
    request = {"query_params": {"currency": "EUR"}}
    result = serializer.get_currency({"symbol": "XAU"})
    assert result == "EUR"

def test_get_price_local(metal_price_serializer):
    serializer = metal_price_serializer()
    request = {"query_params": {"currency": "EUR", "margin": "5.00"}}
    obj = {"price_usd": Decimal("100.00")}
    result = serializer.get_price_local(obj)
    assert isinstance(result, Decimal) and result.quantize(Decimal("0.01")) == Decimal("110.50")

def test_get_price_local_default_currency(metal_price_serializer):
    serializer = metal_price_serializer()
    request = {"query_params": {}}
    obj = {"price_usd": Decimal("100.00")}
    result = serializer.get_price_local(obj)
    assert isinstance(result, Decimal) and result.quantize(Decimal("0.01")) == Decimal("100.00")
```

**feature_file.feature**
```gherkin
Feature: MetalPriceSerializer
  As a developer, I want to test the MetalPriceSerializer class

Scenario: Get price with margin USD
  Given the metal price is "XAU" with price USD 100.00
  When I call get_price_with_margin_usd with margin 10.0
  Then the result should be 110.00

Scenario: Get currency
  Given the request has query param "currency" set to "EUR"
  When I call get_currency for metal price "XAU"
  Then the result should be "EUR"

Scenario: Get price local with margin and custom currency
  Given the request has query params "currency" set to "EUR" and "margin" set to "5.0"
  When I call get_price_local for metal price "XAU" with price USD 100.00
  Then the result should be 110.50

Scenario: Get price local with default currency
  Given the request has no query params
  When I call get_price_local for metal price "XAU" with price USD 100.00
  Then the result should be 100.00
```

# ==== Tests para views.py ====
**Pruebas**

```python
import pytest

@pytest.mark.django_db
def test_metal_price_detail_view():
    # Testear la vista de detalles del precio de metal
    response = MetalPriceDetailView().get({"symbol": "AAPL"})
    assert response.status_code == 200
    response = MetalPriceDetailView().get({"symbol": ""})
    assert response.status_code == 400

@pytest.mark.django_db
def test_metal_price_list_view():
    # Testear la vista de lista de precios de metal
    response = MetalPriceListView().get()
    assert response.status_code == 200

@pytest.mark.django_db
def test_get_yfinance_prices_view():
    # Testear la vista que obtiene los precios de Yahoo Finance
    response = get_yfinance_prices_view(None)
    assert response.status_code == 200

@pytest.mark.django_db
def test_update_prices_view():
    # Testear la vista que actualiza los precios y tasas
    response = update_prices_view(None)
    assert response.status_code == 200

@pytest.mark.django_db
def test_get_price_local_view():
    # Testear la vista que devuelve los precios locales
    response = get_price_local_view(None)
    assert response.status_code == 200
```

**Gherkin Feature**

```gherkin
Feature: Metal Price Views
  As a user, I want to interact with the metal price views

Scenario: Get metal price detail view
  Given the symbol "AAPL" is provided
  When I request the metal price detail view
  Then the response should be successful (200 OK)
  And the metal price data should be returned

Scenario: Get metal price list view
  When I request the metal price list view
  Then the response should be successful (200 OK)
  And all metal prices should be returned in the response

Scenario: Get Yahoo Finance prices
  When I request the Yahoo Finance prices
  Then the response should be successful (200 OK)
  And the latest prices from Yahoo Finance should be returned

Scenario: Update prices and rates
  When I request to update prices and rates
  Then the response should be successful (200 OK)
  And a success message should be displayed in the response

Scenario: Get local prices
  When I request the local prices
  Then the response should be successful (200 OK)
  And all metal prices with local conversions should be returned in the response

# ==== Tests para models.py ====
**models.py**
```python
from django.contrib.auth.models import AbstractUser
from django.db import models
from companies.models import Company

class User(AbstractUser):
    ROLE_CHOICES = [
        ("admin", "Admin"),
        ("soporte", "Soporte"),
        ("vendedor", "Vendedor"),
        ("supervisor", "Supervisor"),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="vendedor"
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users"
    )

    def __str__(self):
        return f"{self.username} ({self.role})"
```

**tests/test_models.py**
```python
import pytest
from models import User

@pytest.fixture
def user():
    return User(username="john_doe", email="johndoe@example.com")

def test_user_role(user):
    assert user.role == "vendedor"

def test_user_company(user):
    company = Company(name="Example Company")
    user.company = company
    assert user.company == company

def test_user_str():
    user = User(username="john_doe", role="admin")
    assert str(user) == "john_doe (Admin)"
```

**features/models.feature**
```python
Feature: User Model
  As a developer, I want to ensure the User model is functioning correctly.

Scenario: Default Role and Company
  Given a new user with default role "vendedor"
  Then the user's role should be "vendedor"

Scenario: Set Custom Company
  Given a new user with custom company "Example Company"
  When the user's company is set to that company
  Then the user's company should be equal to that company

Scenario: String Representation
  Given a user with username "john_doe" and role "admin"
  Then the string representation of the user should be "john_doe (Admin)"
```

# ==== Tests para views.py ====
**views.py**
```python
from rest_framework import generics, permissions
from rest_framework.response import Response
from users.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status

# 🔹 Registro de usuario
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        email = request.data.get("email")
        
        if User.objects.filter(username=username).exists():
            return Response({"error": "Usuario ya existe"}, status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.create_user(username=username, password=password, email=email)
        return Response({"message": "Usuario creado correctamente"}, status=status.HTTP_201_CREATED)

# 🔹 Logout (invalidar tokens)
@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    try:
        token = RefreshToken(request.data.get("refresh"))
        token.blacklist()
        return Response({"message": "Sesión cerrada"}, status=status.HTTP_205_RESET_CONTENT)
    except Exception:
        return Response({"error": "Token inválido"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def profile_view(request):
    user = request.user
    return Response({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "company": user.company.name if user.company else None,
    })
```

**pruebas_unitarias.py**
```python
import pytest
from views import RegisterView, logout_view, profile_view

@pytest.mark.unit_test
def test_register_view():
    request = {"username": "test_user", "password": "test_password", "email": "test_email"}
    response = RegisterView().post(request)
    assert response.status_code == 201
    assert response.json()["message"] == "Usuario creado correctamente"

@pytest.mark.unit_test
def test_register_view_already_exists():
    request = {"username": "test_user", "password": "test_password", "email": "test_email"}
    response = RegisterView().post(request)
    response2 = RegisterView().post(request)  # Try to register again with same username
    assert response2.status_code == 400
    assert response2.json()["error"] == "Usuario ya existe"

@pytest.mark.unit_test
def test_logout_view():
    request = {"refresh": "test_refresh_token"}
    response = logout_view(request)
    assert response.status_code == 205

@pytest.mark.unit_test
def test_profile_view():
    request = {}
    response = profile_view(request)
    assert response.status_code == 200
    assert "id" in response.json()
    assert "username" in response.json()
    assert "email" in response.json()
    assert "role" in response.json()
    assert "company" in response.json()

# Gherkin feature file
Feature: Authentication views
  As a user, I want to test the authentication views

Scenario: Register a new user
  Given I send a POST request to "/register" with username "test_user", password "test_password", and email "test_email"
  Then the response status code should be 201
  And the response body should contain "message": "Usuario creado correctamente"

Scenario: Try to register an existing user
  Given I send a POST request to "/register" with username "test_user", password "test_password", and email "test_email"
  When I try to send another POST request to "/register" with the same username, password, and email
  Then the response status code should be 400
  And the response body should contain "error": "Usuario ya existe"

Scenario: Log out using a valid token
  Given I send a POST request to "/logout" with refresh token "test_refresh_token"
  Then the response status code should be 205

Scenario: View profile information
  Given I send a GET request to "/profile"
  Then the response status code should be 200
  And the response body should contain "id", "username", "email", "role", and "company" keys
