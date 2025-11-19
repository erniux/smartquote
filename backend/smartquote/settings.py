import os
from pathlib import Path
from decouple import config
from datetime import timedelta
from django.conf import settings
from datetime import timedelta



# -----------------------------
# BASE DIR
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# -----------------------------
# CONFIGURACIÓN GENERAL
# -----------------------------
SECRET_KEY = config("SECRET_KEY", default="django-insecure-placeholder")
DEBUG = config("DEBUG", default=True, cast=bool)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="*").split(",")
AUTH_USER_MODEL = "users.User"


# -----------------------------
# APLICACIONES INSTALADAS
# -----------------------------
INSTALLED_APPS = [
    "users",
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Terceros
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
     "django_filters",

    # Apps locales
    "core",
    "services",
    "quotations",
    "companies",
    "sales",
    "invoices",      
]

# -----------------------------
# MIDDLEWARE
# -----------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "smartquote.urls"

# -----------------------------
# TEMPLATES
# -----------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "smartquote.wsgi.application"

# -----------------------------
# BASE DE DATOS
# -----------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DATABASE_NAME"),
        "USER": config("DATABASE_USER"),
        "PASSWORD": config("DATABASE_PASSWORD"),
        "HOST": config("DATABASE_HOST"),
        "PORT": config("DATABASE_PORT"),
    }
}

# -----------------------------
# REST FRAMEWORK + JWT
# -----------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# -----------------------------
# INTERNACIONALIZACIÓN
# -----------------------------
LANGUAGE_CODE = "es-mx"
TIME_ZONE = "America/Mexico_City"
USE_I18N = True
USE_TZ = True

# -----------------------------
# STATIC & MEDIA FILES
# -----------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# -----------------------------
# X-FRAME-OPTIONS (seguridad según entorno)
# -----------------------------
if DEBUG:
    # Permitir iframes en desarrollo (React / Vite y Django en distintos puertos)
    X_FRAME_OPTIONS = "ALLOWALL"
else:
    # En producción solo permitir iframes del mismo dominio
    X_FRAME_OPTIONS = "SAMEORIGIN"



# Ejemplo: si quieres tener una carpeta `uploads/` dentro de media
UPLOAD_DIR = MEDIA_ROOT / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# -----------------------------
# CORS
# -----------------------------
if settings.DEBUG:
    # Permitir solicitudes desde tu entorno de desarrollo (Vite, React)
    CORS_ALLOWED_ORIGINS = [
        "http://localhost:5173",  # Vite dev server
        "http://127.0.0.1:5173",
    ]

    CSRF_TRUSTED_ORIGINS = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    CORS_ALLOW_CREDENTIALS = True
else:
    # En producción, especifica el dominio real
    CORS_ALLOWED_ORIGINS = [
        "https://metalquotes.mx",  # ejemplo dominio
    ]
    CSRF_TRUSTED_ORIGINS = [
        "https://metalquotes.mx",
    ]


# -----------------------------
# PRIMARY KEY DEFAULT
# -----------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# FORGOT PASSWORD EMAIL SETTINGS

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "no-reply@smartquote.local"

# URL del frontend donde el usuario va a cambiar su contraseña
FRONTEND_URL = "http://localhost:5173"  
