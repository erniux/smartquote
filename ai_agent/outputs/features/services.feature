Feature: Metales precios

Scenario: Obtener precio local para un metal específico
    Given dado un símbolo de un metal existente
    When se realiza una solicitud GET a la API con el símbolo proporcionado
    Then debe devolver el precio local para el metal en formato MXN

Scenario: Obtener precio local para un metal no existente
    Given dado un símbolo de un metal que no existe en la base de datos
    When se realiza una solicitud GET a la API con el símbolo proporcionado
    Then debe devolver un error especificando que el metal no existe

Scenario: Obtener precio local para un metal existente con margen
    Given dado un símbolo de un metal existente
    When se realiza una solicitud GET a la API con el símbolo proporcionado y el margen especificado
    Then debe devolver el precio local para el metal en formato MXN considerando el margen indicado

Scenario: Obtener todos los precios locales para metales existentes
    Given dado que hay metales registrados en la base de datos
    When se realiza una solicitud GET a la API sin símbolo específico
    Then debe devolver un listado de precio local para todos los metales registrados en formato MXN

Scenario: Actualizar precios y tasas desde la API de Yahoo Finance
    Given dado que no hay precios y tasas actualizados en la base de datos
    When se realiza una solicitud GET a la API de Yahoo Finance para obtener los precios más recientes de metales
    And luego se ejecuta el comando `update_prices` desde el backend
    Then debe devolver un mensaje indicando que los precios y tasas fueron actualizados correctamente
