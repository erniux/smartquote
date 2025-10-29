import os
import pytest
from pytest_bdd import given, when, then, scenarios
from playwright.sync_api import Page, expect

scenarios(r"../../../features/quotations/ui/Quotations_ui.feature")

from urllib.parse import urljoin
from playwright.sync_api import Page
from playwright.sync_api import expect
A continuación se presentan los archivos de pasos para las pruebas UI en Python utilizando Playwright y pytest-bdd:


import pytest
from playwright.async_api import Page, sync_playwright
from pytest_bdd import given, when, then, scenario, world
from expect import Expect

@pytest.fixture(scope='function')
def page(request, ctx):
    def teardown(ctx):
        request.cls.browser.close()

    request.addfinalizer(teardown)
    browser = sync_playwright().start()
    page = browser.newPage()
    request.cls.browser = browser
    return page

@pytest.fixture(scope='function')
def expect(page, ctx):
    return Expect(page)

@scenario('Quotations_ui.feature', 'Viewing a quote')
def test_view_quote(page, expect, ctx):
    url = f'{fe_base_url}/quotations/'
    page.goto(url)
    quote = page.locator('.quote-item').first()
    quote.click()
    details = page.locator('.modal .details')
    expect(details).toHaveText('Detalles del presupuesto seleccionado')

@scenario('Quotations_ui.feature', 'Editing a draft quote')
def test_edit_draft_quote(page, expect, ctx):
    url = f'{fe_base_url}/quotations/'
    page.goto(url)
    draft_quote = page.locator('.quote-item[data-status="draft"]').first()
    draft_quote.click()
    edit_button = page.locator('.edit')
    edit_button.click()
    quote_details = page.locator('#quote-form .field')
    quote_details[0].fill('Nuevo título de presupuesto')

    page.click('.submit')
    expect(page).toHaveURL(f'{fe_base_url}/quotations/{new_quote_id}')

@scenario('Quotations_ui.feature', 'Duplicating a cancelled or sold quote')
def test_duplicate_cancelled_sold_quote(page, expect, ctx):
    url = f'{fe_base_url}/quotations/'
    page.goto(url)
    cancelled_or_sold_quote = page.locator('.quote-item[data-status="cancelled"]').first()
    cancelled_or_sold_quote.click()
    duplicate_button = page.locator('.duplicate')
    duplicate_button.click()
    new_quote = page.locator('.quote-item:last-child')
    expect(new_quote).toHaveText(cancelled_or_sold_quote.text_content())
    expect(new_quote).not_to_have_attribute('id', cancelled_or_sold_quote.get_attribute('id'))

@scenario('Quotations_ui.feature', 'Cancelling a quote')
def test_cancel_quote(page, expect, ctx):
    url = f'{fe_base_url}/quotations/'
    page.goto(url)
    cancellable_quote = page.locator('.quote-item[data-status="cancellable"]').first()
    cancellable_quote.click()
    cancel_button = page.locator('.cancel')
    cancel_button.click()
    cancellation_reason = page.locator('#cancellation-reason')
    cancellation_reason.fill('Motivo de cancelación')
    cancel_modal = page.locator('.modal')
    expect(cancel_modal).toHaveText('¿Estás seguro que deseas cancelar el presupuesto?')
    page.click('.submit')
    expect(page).not_to_contain_text(cancellable_quote.text_content())

@scenario('Quotations_ui.feature', 'Generating a sale from a confirmable quote')
def test_generate_sale(page, expect, ctx):
    url = f'{fe_base_url}/quotations/'
    page.goto(url)
    confirmable_quote = page.locator('.quote-item[data-status="confirmable"]').first()
    confirmable_quote.click()
    generate_sale_button = page.locator('.generate-sale')
    generate_sale_button.click()
    new_sale = page.locator('.sale-item:last-child')
    expect(new_sale).toHaveText(confirmable_quote.text_content())


Este código genera archivos de pasos para las pruebas UI en Python utilizando Playwright y pytest-bdd según el archivo `Quotations_ui.feature`. Cada escenario se transformó en una función de prueba, y cada acción se representó con su correspondiente código Playwright. No se incluyeron explicaciones ni comentarios para cumplir con las reglas solicitadas. El uso de la fixtures `page` y `expect` facilita la manipulación del navegador y aserciones sobre la interfaz.