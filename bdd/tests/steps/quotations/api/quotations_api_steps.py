import os
import pytest
from pytest_bdd import given, when, then, scenarios

scenarios(r"../../../features/quotations/api/quotations_api.feature")

from urllib.parse import urljoin
import pytest
A continuación se muestra el archivo de steps para las pruebas de API en Python usando la librería 'requests' y pytest-bdd basado en el archivo .feature proporcionado.


import requests
from pytest import mark, fixture
from pytest_bdd import given, when, then, scenario

@fixture(autouse=True)
def api(ctx):
    session = requests.Session()
    yield session
    session.close()

@fixture
def api_base_url(ctx):
    return "http://localhost:8000/api"

@scenario("quotations_api.feature", "A user with proper permissions can list quotations")
def test_list_quotations(api, api_base_url, ctx):
    url = f"{api_base_url}/quotations/"
    session = api
    given(u"I am authenticated as an authorized user or admin user")


    when(u"I send a GET request to the '/quotations/' endpoint")
    response = session.get(url)

    then(u"I should receive a response containing a JSON array of quotation objects")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    assert isinstance(response.json(), list), "Response is not a JSON array"
    for item in response.json():
        assert all([key in item for key in ["id", "customer_name", "email", "currency", "notes", "subtotal", "tax", "total", "status"]]), f"Missing required fields: {[key for key in item if key not in ['id', 'customer_name', 'email', 'currency', 'notes', 'subtotal', 'tax', 'total', 'status']]}"

@scenario("quotations_api.feature", "An unauthenticated user cannot list quotations")
def test_unauthorized_user_cannot_list_quotations(api, api_base_url, ctx):
    url = f"{api_base_url}/quotations/"
    session = api
    given(u"I am not authenticated")

    when(u"I send a GET request to the '/quotations/' endpoint")
    response = session.get(url)

    then(u"I should receive a response with an error message and a status code of 401 Unauthorized")
    assert response.status_code == 401, f"Expected status code 401, got {response.status_code}"



A continuación se proporcionan los pasos de pruebas adicionales para completar las funcionalidades CRUD de endpoints tipo '/api/quotations/'. Se requiere agregar más fixtures y código de autenticación.


@scenario("quotations_api.feature", "A user can create a new quotation")
def test_create_new_quotation(api, api_base_url, ctx):
    url = f"{api_base_url}/quotations/"
    session = api

    given(u"I am authenticated as an authorized user or admin user")


    and_(u"And I have a valid Quotation creation payload in JSON format")


    when(u"I send a POST request to the '/quotations/' endpoint with the JSON payload")
    response = session.post(url, json=payload)

    then(u"I should receive a response containing a newly created quotation object")
    assert response.status_code == 201, f"Expected status code 201, got {response.status_code}"
    quotation = response.json()
    assert all([key in quotation for key in ["id", "customer_name", "email", "currency", "notes", "subtotal", "tax", "total", "status"]]), f"Missing required fields: {[key for key in quotation if key not in ['id', 'customer_name', 'email', 'currency', 'notes', 'subtotal', 'tax', 'total', 'status']]}"

@scenario("quotations_api.feature", "A user cannot create a new quotation without proper permissions")
def test_unauthorized_user_cannot_create_new_quotation(api, api_base_url, ctx):
    url = f"{api_base_url}/quotations/"
    session = api

    given(u"I am authenticated as an unauthorized user")


    and_(u"And I have a valid Quotation creation payload in JSON format")


    when(u"I send a POST request to the '/quotations/' endpoint with the JSON payload")
    response = session.post(url, json=payload)

    then(u"I should receive a response with an error message and a status code of 403 Forbidden")
    assert response.status_code == 403, f"Expected status code 403, got {response.status_code}"