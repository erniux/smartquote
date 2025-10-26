# 🚀 SmartQuote – Sistema de Cotizaciones Inteligente para PYMEs

![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python)
![Django](https://img.shields.io/badge/Django-5.0-success?logo=django)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue?logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-ready-blue?logo=docker)
![Status](https://img.shields.io/badge/build-passing-brightgreen)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

---
# 🧠 SmartQuote — Sistema Inteligente de Cotizaciones con Precios de Mercado

SmartQuote es una aplicación moderna construida con **Django + Docker + DRF + yFinance**, diseñada para crear y administrar **cotizaciones dinámicas** que se actualizan automáticamente según los **precios reales de metales, madera, PVC y divisas**.

---

## 🚀 Características principales

✅ **API REST completa** para crear, editar y consultar cotizaciones.  
✅ **Integración con Yahoo Finance (`yfinance`)** para obtener precios actualizados.  
✅ **Conversión automática de divisas (USD → MXN, EUR, JPY)**.  
✅ **Cálculo inteligente** de subtotal, IVA y total según commodities.  
✅ **Botón mágico en el panel Admin** para recalcular precios en tiempo real.  
✅ **Soporte de múltiples materiales:** aluminio, hierro, cobre, oro, plata, madera y PVC.  
✅ **Estructura modular** con apps separadas (`core`, `services`, `quotations`).  
✅ **Docker-ready**, totalmente aislado para desarrollo o despliegue en producción.

---

## 🧱 Arquitectura del Proyecto

```
smartquote/
│
├── core/                # App principal (productos y materiales)
│   ├── models.py
│   ├── admin.py
│   └── serializers.py
│
├── quotations/          # App de cotizaciones dinámicas
│   ├── models.py        # Quotation y QuotationItem
│   ├── serializers.py   # Cálculo automático de precios
│   ├── views.py
│   ├── urls.py
│   └── admin.py         # Botón “Recalcular precios”
│
├── services/            # API de datos externos (yFinance)
│   ├── api_clients.py   # Obtiene precios de metales y divisas
│   └── management/
│       └── commands/
│           └── update_prices.py
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## ⚙️ Instalación con Docker

```bash
# Clonar el repositorio
git clone https://github.com/erniux/smartquote.git
cd smartquote/backend

# Construir y ejecutar contenedores
docker compose up -d --build

# Crear las apps iniciales y migraciones
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate

# Crear superusuario
docker compose exec web python manage.py createsuperuser
```

---

## 📦 Actualizar precios del mercado

SmartQuote usa **Yahoo Finance (`yfinance`)** para obtener precios reales de commodities y divisas.

Ejecuta el comando:

```bash
docker compose exec web python manage.py update_prices
```

Ejemplo de salida:

```
⏳ Obteniendo precios de metales y commodities desde Yahoo Finance...
✅ ALUMINUM (ALI=F) → 2640.75 USD
✅ IRON (TIO=F) → 105.74 USD
✅ COPPER (HG=F) → 4.8940 USD
✅ GOLD (GC=F) → 4000.40 USD
✅ SILVER (SI=F) → 47.24 USD
✅ LUMBER (LBR=F) → 610.50 USD
✅ PVC (PVC-USD) → 0.0109 USD
⏳ Obteniendo tasas de cambio...
✅ USD/MXN → 18.54
✅ USD/EUR → 0.85
✅ USD/JPY → 151.11
✅ Actualización completada
```

---

## 💰 Cálculo automático de cotizaciones

Cada cotización (`Quotation`) se calcula automáticamente al momento de crearse o editarse:

- Toma el **precio actual del commodity** asociado a cada producto.  
- Aplica la **tasa de cambio** USD → moneda local.  
- Calcula **subtotal + IVA + total** de forma automática.

### Ejemplo `POST /api/quotations/`

```json
{
  "customer_name": "Escuela Técnica #21",
  "customer_email": "contacto@escuela21.mx",
  "currency": "MXN",
  "tax": 16,
  "items": [
    { "product": 1, "quantity": 2 }
  ]
}
```

📤 **Respuesta automática:**

```json
{
  "id": 3,
  "customer_name": "Escuela Técnica #21",
  "currency": "MXN",
  "subtotal": "370.85",
  "tax": "16.00",
  "total": "430.19",
  "items": [
    {
      "product": 1,
      "product_name": "Herrería en Ventanas",
      "quantity": 2,
      "unit_price": "185.43"
    }
  ]
}
```

---

## 🧠 Botón mágico “Recalcular precios con valores del mercado”

En el panel de administración de Django:
1. Selecciona una o varias cotizaciones.  
2. En el menú “Acción”, elige  
   **🔁 Recalcular precios con valores del mercado**  
3. Presiona “Ejecutar”.  

✨ El sistema recalculará precios, subtotal y total según los valores más recientes de los commodities y divisas.

---

## 🧩 Apps incluidas

| App | Descripción |
|-----|--------------|
| `core` | Gestión de productos base |
| `services` | Obtención de precios desde Yahoo Finance |
| `quotations` | Creación de cotizaciones dinámicas y cálculo de totales |

---

## Flujo CI / CD
                ┌───────────────────────────┐
                │        Developer          │
                │     (VSCode + Docker)     │
                └────────────┬──────────────┘
                             │
                             ▼
                 ┌───────────────────────────┐
                 │     GitHub Repository      │
                 │  (push, pull_request, etc) │
                 └────────────┬──────────────┘
                             │
     ┌────────────────────────────────────────────────────┐
     │                     GitHub Actions                 │
     │────────────────────────────────────────────────────│
     │  1️⃣ ai-agent-ci.yml   → Build + Lint AI Agent      │
     │  2️⃣ django-ci.yml     → Build + Check Django       │
     │  3️⃣ bdd-tests.yml     → Run BDD / Playwright tests │
     └────────────────────────────────────────────────────┘
                             │
                             ▼
                ┌───────────────────────────┐
                │    Docker Compose Stack   │
                │ ai_agent / backend / bdd  │
                └────────────┬──────────────┘
                             │
                             ▼
             ┌───────────────────────────────┐
             │        Deployment (CD)        │
             │  • Heroku / Render / Fly.io   │
             │  • Docker VPS (optional)      │
             └────────────┬──────────────────┘
                             │
                             ▼
                🌐 SMARTQUOTE en Producción
                (Backend + Frontend + AI Agent)


## 🧰 Tecnologías

- **Python 3.13**
- **Django 5 + DRF**
- **yFinance**
- **PostgreSQL**
- **Docker / Compose**
- **Pillow**
- **REST API JSON**

---

## 📈 Próximas fases (en progreso)

- 📄 Generación automática de PDF con logo y cotización profesional.  
- 🌐 Frontend con React + Vite para gestionar cotizaciones.  
- 🔐 Autenticación JWT para API segura.  
- ⏰ Tareas programadas para actualizar precios automáticamente.  

---

## 💚 Autor

**Erna Tercero Rodríguez**  
🧑‍💻 *Software Quality Analyst & Data Science Student*  
📍 Querétaro, México  
🔗 [GitHub – erniux](https://github.com/erniux)

---

> “SmartQuote convierte la información del mercado en decisiones de negocio en tiempo real.” 🚀

---

🪄 *“Cotiza en minutos, sin hojas de cálculo.” – SmartQuote*
