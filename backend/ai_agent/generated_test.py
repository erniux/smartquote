No hay un archivo de prueba pytest funcional que responda directamente a la estructura y contenido proporcionados. Sin embargo, puedo ayudarte a crear una prueba funcional básica para cada aplicación.

**metal_prices.py**
```python
import pytest
from services.views import MetalPriceDetailView, MetalPriceListView

@pytest.mark.django_db
def test_metal_price_detail_view():
    # Crear un metal price en la base de datos
    metal = MetalPrice(symbol='Au', price_usd=1000.00)
    metal.save()

    # Verificar que el detalle del metal price sea correcto
    view = MetalPriceDetailView()
    response = view.get({'symbol': 'Au'})
    assert response.status_code == 200
    assert response.data['symbol'] == 'Au'
    assert response.data['price_usd'] == 1000.00

@pytest.mark.django_db
def test_metal_price_list_view():
    # Crear varios metal prices en la base de datos
    metals = [MetalPrice(symbol='Au', price_usd=1000.00), MetalPrice(symbol='Ag', price_usd=500.00)]
    for metal in metals:
        metal.save()

    # Verificar que la lista de metal prices sea correcta
    view = MetalPriceListView()
    response = view.get()
    assert response.status_code == 200
    assert len(response.data) == 2
    assert response.data[0]['symbol'] == 'Au'
    assert response.data[1]['symbol'] == 'Ag'
```

**users.py**
```python
import pytest
from users.views import RegisterView, logout_view

@pytest.mark.django_db
def test_register_view():
    # Crear un usuario nuevo
    request = {'username': 'john', 'password': 'hello', 'email': 'john@example.com'}
    view = RegisterView()
    response = view.post(request)
    assert response.status_code == 201
    assert response.data['message'] == 'Usuario creado correctamente'

@pytest.mark.django_db
def test_logout_view():
    # Iniciar sesión con un usuario
    user = User.objects.create_user(username='john', password='hello')
    request = {'refresh': RefreshToken.for_user(user)}
    view = logout_view()
    response = view.post(request)
    assert response.status_code == 205
    assert response.data['message'] == 'Sesión cerrada'
```

**other_views.py**
```python
import pytest
from other_views import get_price_local_view

@pytest.mark.django_db
def test_get_price_local_view():
    # Crear varios metal prices en la base de datos
    metals = [MetalPrice(symbol='Au', price_usd=1000.00), MetalPrice(symbol='Ag', price_usd=500.00)]
    for metal in metals:
        metal.save()

    # Verificar que el precio local sea correcto
    view = get_price_local_view()
    response = view.get()
    assert response.status_code == 200
    assert len(response.data) == 2
    assert response.data[0]['price_local'] == '1000.00 MXN'
    assert response.data[1]['price_local'] == '500.00 MXN'
```

Recuerda que estas pruebas son solo ejemplos y necesitarían adaptarse a tus especificaciones de prueba.