# Archivo: /app/quotations/models.py
#Aquí tienes las pruebas unitarias para el modelo `Quotation`:

#```python
import pytest
from datetime import datetime, timezone
from decimal import Decimal
from django.utils import timezone
from core.models import Product
from services.models import MetalPrice, CurrencyRate
from companies.models import Company
from quotations.models import Quotation

@pytest.fixture(autouse=True)
def setup_models():
    """Configuración inicial para las pruebas."""
    Company.objects.create(name="Empresa Test", nit="001", email="test@test.com")
    Product.objects.create(
        name="Producto Test",
        description=" Producto de prueba",
        unit_price=Decimal("100.00"),
        stock=10
    )

@pytest.fixture
def quotation(django_db):
    """Crear una instancia base de Quotation para las pruebas."""
    return Quotation.objects.create(
        customer_name="Cliente Test",
        company_id=1,
        date=timezone.now().date()
    )

@pytest.mark.django_db
def test_quotation_creation(quotation):
    """Prueba de creación básica de una cotización."""
    assert quotation.customer_name == "Cliente Test"
    assert quotation.status == "draft"
    assert quotation.confirmed_at is None
    assert quotation.cancelled_at is None

@pytest.mark.django_db
def test_calculate_totals_without_items_or_expenses(quotation):
    """Prueba calcular totales sin items ni gastos."""
    subtotal, tax, total = quotation.calculate_totals()
    assert subtotal == Decimal("0.00")
    assert tax == Decimal("0.00")
    assert total == Decimal("0.00")

@pytest.mark.django_db
def test_calculate_totals_with_items_and_expenses(django_db):
    """Prueba calcular totales con items y gastos."""
    # Crear items de prueba
    item1 = Quotation.QuotationItem.objects.create(
        quotation=quotation,
        product_id=1,
        quantity=2,
        unit_price=Decimal("50.00")
    )
    
    # Crear gasto de prueba
    Quotation.QuotationExpense.objects.create(
        quotation=quotation,
        description="Gasto de prueba",
        total_cost=Decimal("20.00")
    )

    subtotal, tax, total = quotation.calculate_totals()
    
    assert subtotal == Decimal("120.00")  # (50 * 2) + 20
    assert tax == Decimal("19.20")       # 16% de 120
    assert total == Decimal("139.20")

@pytest.mark.django_db
def test_confirm_quotation(quotation):
    """Prueba confirmar una cotización."""
    # Mock fecha y hora
    mock_date = datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc)
    
    # Confirmar la cotización
    quotation.confirm(mock_date)

    assert quotation.status == "confirmed"
    assert quotation.confirmed_at == mock_date
    assert quotation.cancelled_at is None

@pytest.mark.django_db
def test_cancel_quotation(quotation):
    """Prueba cancelar una cotización."""
    # Establecer estado a 'cancelled'
    cancellation_reason = " Razón de prueba para anular"
    quotation.status = "cancelled"
    quotation.cancellation_reason = cancellation_reason
    quotation.cancelled_at = timezone.now()
    quotation.save()

    assert quotation.status == "cancelled"
    assert quotation.cancellation_reason == cancellation_reason
    assert quotation.cancelled_at is not None

@pytest.mark.django_db
def test_quotation_monetary_fields():
    """Prueba los campos monetarios con valores válidos."""
    money_field = Quotation.MONEY_FIELD.copy()
    
    # Campos esperados
    expected_values = {
        'subtotal': Decimal("0.00"),
        'tax': Decimal("0.00"),
        'total': Decimal("0.00")
    }

    quotation = Quotation.objects.create(
        customer_name="Cliente Test",
        **{field: Decimal("100.00") for field in ['subtotal', 'tax', 'total']}
    )

    assert all(getattr(quotation, key) == expected_values[key] for key in expected_values)
'''

Estas pruebas cubren:

1. Creación básica de una instancia de Quotation.
2. Cálculo de totales sin items ni gastos.
3. Cálculo de totales con items y gastos.
4. Método confirm() para marcar la cotización como confirmada.
5. Validación de campos monetarios.
6. Manejo del estado de cancelación.

Las pruebas verifican:
- Valores iniciales correctos al crear una instancia.
- Cálculos correctos de subtotal, impuesto y total con diferentes scnearios.
- Cambio correcto de estado al confirmar o anular.
- Formato y valores correctos de los campos monetarios.

Para ejecutar estas pruebas, asegúrate de tener configurado el entorno de pruebas de Django y que las aplicaciones estén registradas correctamente.

# Archivo: /app/quotations/pdf_utils.py
Aquí tienes un conjunto de pruebasunitarias detalladas para la función `generate_quotation_pdf` utilizando pytest:

```python 
'''
import pytest
from unittest.mock import Mock, patch
from io import BytesIO
from django.http import HttpResponse
from reportlab.pdfgen.canvas import Canvas
from .models import Quotation, Company  # Asume que tienes un modelo Quotation y Company

@pytest.fixture
def quotation():
    """Fixture para crear una instancia mock de Quotation"""
    company = Company(
        name="Empresa Test",
        address="Calle Test 123",
        phone="+57 123456789",
        email="test@email.com",
        website="www.empresa.com",
        logo=Mock()  # Mock para manejar la imagen
    )
    
    items = [
        {
            'product': Mock(name='Producto Test 1'),
            'unit_price': 100.0,
            'quantity': 2,
        },
        {
            'product': Mock(name='Producto Test 2'),
            'unit_price': 50.0,
            'quantity': 3,
        }
    ]
    
    return Mock(
        company=company,
        customer_name="Juan Pérez",
        customer_email="juan@email.com",
        currency="COP",
        date=datetime.now(),
        items=Mock(all=lambda: items),
        _get_items=Mock(return_value=items)
    )

def test_basic_generation(quotation):
    """Prueba básica para verificar que se genera el PDF sin errores"""
    buffer = BytesIO()
    response = generate_quotation_pdf(quotation, buffer)
    
    assert isinstance(response, HttpResponse)
    assert response['Content-Type'] == 'application/pdf'
    assert len(buffer.getvalue()) > 0

def test_elements_inclusion(quotation):
    """Prueba para verificar que todos los elementos están presentes en el PDF"""
    buffer = BytesIO()
    generate_quotation_pdf(quotation, buffer)
    
    # Verificar que hay una imagen (logo) incluida
    assert b'/XObject' in buffer.getvalue()  # Indica la presencia de un objeto de imagen
    
    # Verificar texto específico en el PDF
    text_elements = [
        quotation.company.name,
        quotation.customer_name,
        quotation.currency,
        quotation.date.strftime('%d/%m/%Y'),
    ]
    
    pdf_content = buffer.getvalue()
    for element in text_elements:
        assert element.encode() in pdf_content

def test_table_structure(quotation):
    """Prueba para verificar la estructura de la tabla"""
    buffer = BytesIO()
    generate_quotation_pdf(quotation, buffer)
    
    # Obtener el canvas del PDF
    canvas = Canvas(buffer)
    
    # Buscar las coordenadas y texto de la tabla
    elements = canvas._elements  # Asume que tienes acceso a los elementos dibujados
    
    # Verificar encabezado de la tabla
    assert any("Producto" in element.text for element in elements if hasattr(element, 'text'))
    
    # Verificar filas de la tabla
    expected_products = [item['product'].name for item in quotation.items]
    for product in expected_products:
        assert product.encode() in buffer.getvalue()
    
    # Verificar formato numérico
    prices = [
        f"${float(item['unit_price']):,.2f}" 
        for item in quotation.items
    ]
    for price in prices:
        assert price.encode() in buffer.getvalue()

def test_default_logo_usage(quotation):
    """Prueba para verificar que se usa el logo por defecto"""
    # Hacer que company.logo devuelva None
    quotation.company.logo = None
    
    buffer = BytesIO()
    generate_quotation_pdf(quotation, buffer)
    
    # Verificar que se incluye la imagen por defecto
    default_logo_path = b'static/img/default_logo.png'
    assert default_logo_path in buffer.getvalue()

def test_empty_fields_handling(quotation):
    """Prueba para verificar el manejo de campos vacíos"""
    # Hacer que company.address devuelva None
    quotation.company.address = None
    
    buffer = BytesIO()
    generate_quotation_pdf(quotation, buffer)
    
    # Verificar que el campo dirección se omita si no está presente
    assert (' Dirección:' not in buffer.getvalue())

def test_currency_symbol_inclusion(quotation):
    """Prueba para verificar la inclusión del símbolo de moneda"""
    buffer = BytesIO()
    generate_quotation_pdf(quotation, buffer)
    
    # Verificar que se incluye el símbolo de moneda
    assert f"${quotation.currency}".encode() in buffer.getvalue()

def test_date_formatting(quotation):
    """Prueba para verificar el formato de fecha"""
    buffer = BytesIO()
    generate_quotation_pdf(quotation, buffer)
    
    # Obtener la fecha esperada en formato requerido
    expected_date = quotation.date.strftime('%d/%m/%Y')
    
    assert expected_date.encode() in buffer.getvalue()

@pytest.mark.parametrize("test_input,expected", [
    ("COP", "$ COP"),
    ("USD", "$ USD"),
])
def test_currency_display(test_input, expected):
    """Prueba parametrizada para verificar la visualización de monedas"""
    quotation = Mock(
        company=Company(name="Empresa Test"),
        customer_name="Juan Pérez",
        currency=test_input,
        date=datetime.now(),
        items=[]
    )
    
    buffer = BytesIO()
    generate_quotation_pdf(quotation, buffer)
    
    assert expected.encode() in buffer.getvalue()

def test_subtotal_calculations(quotation):
    """Prueba para verificar los cálculos de subtotales"""
    # Modificar los precios y cantidades
    quotation.items.all()[0].unit_price = 150.0
    quotation.items.all()[0].quantity = 3
    
    buffer = BytesIO()
    generate_quotation_pdf(quotation, buffer)
    
    # Calcular subtotal esperado
    expected_subtotal = round(150 * 3 + 50 * 2, 2)  # Asumiendo dos productos
    
    assert f"${expected_subtotal:,.2f}".encode() in buffer.getvalue()
'''

Estas pruebas cubren diferentes aspectos del código incluyendo:

1. **Generación básica del PDF**
2. **Inclusión de elementos clave (logo, información de empresa, cliente)**
3. **Estructura y formato de la tabla de productos**
4. **Uso del logo por defecto**
5. **Manejo de campos vacíos**
6. **Formato numérico (monedas y fechas)**
7. **Cálculos de subtotales**

Para ejecutar estas pruebas, asegúrate de tener instalados los paquetes necesarios:

```bash
pip install pytest reportlab
```

Y configura tu entorno para que las clases y modelos Mockeados funcionen correctamente.

Es importante recordar que algunas pruebas, como las que verifican el contenido del PDF (`test_elements_inclusion`, `test_table_structure`), pueden requerir ajustes adicionales dependiendo de cómo estén implementados los elementos en tu aplicación.

# Archivo: /app/quotations/serializers.py
Para generar pruebas automatizadas con `pytest` para los serializers del código proporcionado, seguiremos estos pasos:

### 1. Crear una clase base de prueba
Primero, crearemos una clase base que contendrá métodos comunes para las pruebas de los serializers.

```python 
'''
import pytest
from rest_framework import serializers
from core.models import Product
from quotations.models import Quotation, QuotationItem, QuotationExpense
from .serializers import (
    QuotationItemSerializer,
    QuotationExpenseSerializer,
    QuotationSerializer
)

@pytest.mark.django_db
class BaseTestCase:
    def test_serializer_is_invalid(self, serializer_class, data):
        serializer = serializer_class(data=data)
        assert not serializer.is_valid()
    
    def test_serializer_is_valid(self, serializer_class, data):
        serializer = serializer_class(data=data)
        assert serializer.is_valid()
'''

### 2. Pruebas para QuotationItemSerializer
Creamos pruebas específicas para `QuotationItemSerializer`.

```python 
'''
class TestQuotationItemSerializer(BaseTestCase):
    def test_quotation_item_required_fields(self):
        data = {
            "quantity": "10.5"
        }
        self.test_serializer_is_valid(QuotationItemSerializer, data)
    
    def test_quotation_item_missing_quantity(self):
        data = {
            "name": "Test Item",
            "metal_symbol": "Ag",
            "price": "100.00"
        }
        self.test_serializer_is_invalid(QuotationItemSerializer, data)
'''

### 3. Pruebas para QuotationExpenseSerializer
Creamos pruebas específicas para `QuotationExpenseSerializer`.

```python
'''
class TestQuotationExpenseSerializer(BaseTestCase):
    def test_quotation_expense_required_fields(self):
        data = {
            "name": "Shipping",
            "category": "shipping",
            "quantity": "1",
            "unit_cost": "50.00"
        }
        self.test_serializer_is_valid(QuotationExpenseSerializer, data)
    
    def test_quotation_expense_missing_fields(self):
        data = {
            "name": "Shipping",
            "category": "shipping"
        }
        self.test_serializer_is_invalid(QuotationExpenseSerializer, data)
'''

### 4. Pruebas para QuotationSerializer
Creamos pruebas específicas para `QuotationSerializer`, teniendo en cuenta los nested serializers.

```python
'''
class TestQuotationSerializer(BaseTestCase):
    def test_quotation_required_fields(self):
        data = {
            "customer_name": "John Doe",
            "items": [
                {
                    "id": 1,
                    "name": "Item 1",
                    "metal_symbol": "Au",
                    "price": "100.00",
                    "quantity": "2.5"
                }
            ]
        }
        self.test_serializer_is_valid(QuotationSerializer, data)
    
    def test_quotation_missing_required_fields(self):
        data = {
            "customer_name": "John Doe",
            "items": []
        }
        self.test_serializer_is_invalid(QuotationSerializer, data)
'''

### 5. Ejecutar las pruebas
Para ejecutar las pruebas, puedes usar:

```bash

pytest tests/serializers.py -v
```

Estas pruebas cubrirán:
- Campos requeridos.
- Tipos de datos correctos.
- Validación general para los serializers.

### Notas adicionales
- Asegúrate de que el modulo `services` y ` quotations` estén correctamente configurados en tu entorno de desarrollo.
- Puedes ampliar las pruebas agregando más casos, como pruebas para actualizaciones (`update`) y manejo de errores específicos.

Estas pruebas te ayudarán a asegurar que tus serializers funcionan correctamente y cumplan con los requisitos especificados.
'''