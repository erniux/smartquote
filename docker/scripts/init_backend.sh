#!/bin/bash
set -e

echo "🚀 Iniciando script de inicialización de Django..."

# Asegurarse de que las variables estén definidas
if [ -z "$DJANGO_SUPERUSER_USERNAME" ] || [ -z "$DJANGO_SUPERUSER_EMAIL" ] || [ -z "$DJANGO_SUPERUSER_PASSWORD" ] || [ -z "$DJANGO_SUPERUSER_ROLE" ]; then
  echo "❌ ERROR: Faltan variables de entorno requeridas para crear el superusuario."
  echo "   Debes definir en tu archivo .env:"
  echo "   DJANGO_SUPERUSER_USERNAME"
  echo "   DJANGO_SUPERUSER_EMAIL"
  echo "   DJANGO_SUPERUSER_PASSWORD"
  echo "   DJANGO_SUPERUSER_ROLE"
  exit 1
fi

echo "🧱 Aplicando migraciones..."
python manage.py migrate --noinput

echo "⚙️ Creando superusuario principal si no existe..."
python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()

username = "${DJANGO_SUPERUSER_USERNAME}"
email = "${DJANGO_SUPERUSER_EMAIL}"
password = "${DJANGO_SUPERUSER_PASSWORD}"
role = "${DJANGO_SUPERUSER_ROLE}"

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password, role=role)
    print(f"✅ Superusuario creado: {username} (rol={role})")
else:
    print(f"ℹ️ El superusuario '{username}' ya existe, omitiendo creación.")

# Crear otros roles base si tu modelo los admite
roles = ["support", "auditor", "developer"]
for r in roles:
    if not User.objects.filter(role=r).exists():
        u = User.objects.create_user(
            username=f"{r}_user",
            email=f"{r}@example.com",
            password="password123",
            role=r,
        )
        print(f"👤 Usuario de rol '{r}' creado: {u.username}")
    else:
        print(f"ℹ️ Ya existe al menos un usuario con rol '{r}'.")
EOF

echo "✅ Usuarios base verificados/creados."
echo "🚀 Iniciando servidor Django..."
python manage.py runserver 0.0.0.0:8000
