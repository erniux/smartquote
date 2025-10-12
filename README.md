# 🚀 SmartQuote – Sistema de Cotizaciones Inteligente para PYMEs

![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python)
![Django](https://img.shields.io/badge/Django-5.0-success?logo=django)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue?logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-ready-blue?logo=docker)
![Status](https://img.shields.io/badge/build-passing-brightgreen)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

---

## 🧩 Descripción

**SmartQuote** es una aplicación moderna desarrollada con **Django + DRF + Docker + PostgreSQL**, diseñada para que pequeñas y medianas empresas puedan crear, gestionar y enviar **cotizaciones inteligentes** de forma rápida y profesional.

📦 Permite registrar productos, calcular precios con márgenes personalizados, generar cotizaciones en PDF y subir imágenes de productos.  
🧠 Ideal para carpinterías, herrerías, imprentas, talleres y todo negocio que cotice proyectos o servicios a clientes.

---

## 🏗️ Arquitectura del Proyecto

```
smartquote/
├── backend/
│   ├── core/                # App principal (productos, cotizaciones)
│   ├── smartquote/          # Configuración del proyecto Django
│   ├── requirements.txt     # Dependencias del backend
│   ├── Dockerfile           # Imagen base de Django
│   ├── docker-compose.yml   # Servicios: web + db
│   └── .env.example         # Variables de entorno (modo ejemplo)
└── .github/
    └── workflows/           # CI/CD con GitHub Actions
```

---

## ⚙️ Tecnologías

| Componente | Tecnología |
|-------------|-------------|
| **Backend** | Django 5 + Django REST Framework |
| **Base de Datos** | PostgreSQL 16 |
| **Infraestructura** | Docker + Docker Compose |
| **Autenticación** | JWT (SimpleJWT) |
| **Storage** | Local (media/) con opción futura a AWS o Google Cloud |
| **CI/CD** | GitHub Actions |

---

## 🧰 Instalación y configuración

### 1️⃣ Clonar el repositorio
```bash
git clone https://github.com/erniux/smartquote.git
cd smartquote/backend
```

### 2️⃣ Crear archivo `.env`
Copia el de ejemplo:
```bash
cp .env.example .env
```

Y modifica tus credenciales si lo deseas.

### 3️⃣ Construir los contenedores
```bash
docker compose up -d --build
```

### 4️⃣ Crear proyecto Django (solo si es la primera vez)
```bash
docker compose exec web django-admin startproject smartquote .
docker compose exec web python manage.py startapp core
```

### 5️⃣ Migraciones y superusuario
```bash
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

### 6️⃣ Acceder al panel de administración
👉 [http://localhost:8000/admin/](http://localhost:8000/admin/)

---

## 🌐 Endpoints principales

| Endpoint | Método | Descripción |
|-----------|--------|--------------|
| `/api/products/` | GET, POST | Gestión de productos con imágenes |
| `/api/token/` | POST | Obtener token JWT |
| `/api/token/refresh/` | POST | Refrescar token JWT |

Ejemplo de respuesta de producto:
```json
{
  "id": 1,
  "name": "Herrería en Ventanas",
  "description": "Crear marcos de herrería a base de hierro inoxidable",
  "price": "10.00",
  "margin": "5.00",
  "unit": "mts",
  "image_url": "http://localhost:8000/media/uploads/products/ventana.jpg"
}
```

---

## 🖼️ Captura de ejemplo

![SmartQuote Admin Panel](docs/screenshots/admin-products.png)

---

## 📦 Próximas fases

- [x] Base del backend con Django y Docker  
- [x] Endpoint de productos con imagen  
- [ ] Módulo de cotizaciones (Quotation)  
- [ ] Generación de PDFs  
- [ ] Frontend con React + Vite  
- [ ] Despliegue en producción (Render / Railway / AWS)

---

## 💬 Créditos

Desarrollado con ❤️ por **Erna Tercero Rodríguez**  
📍 Querétaro, México  
🔗 [github.com/erniux](https://github.com/erniux)

---

## ⚖️ Licencia

Este proyecto está bajo la licencia **MIT**, lo que permite su uso, modificación y distribución libre.

---

🪄 *“Cotiza en minutos, sin hojas de cálculo.” – SmartQuote*
