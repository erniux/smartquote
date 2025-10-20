import os

class CodeReader:
    """
    Lee automáticamente las apps Django dentro de /app y
    extrae solo los archivos models.py, serializers.py y views.py.
    Ignora migraciones, tests y otros archivos no relevantes.
    """

    def __init__(self, base_dir="/app"):
        self.base_dir = base_dir
        self.allowed_files = {"models.py", "serializers.py", "views.py"}

    def _is_django_app(self, path):
        """Verifica si una carpeta parece una app Django (contiene models.py o apps.py)."""
        return any(os.path.exists(os.path.join(path, f)) for f in ["models.py", "apps.py"])

    def read_files(self):
        context = {}

        for root, dirs, files in os.walk(self.base_dir):
            # Evitar subcarpetas de migraciones y tests
            if "migrations" in root or "tests" in root:
                continue

            # Detectar si el directorio actual pertenece a una app Django
            if not self._is_django_app(root):
                continue

            for f in files:
                if f in self.allowed_files:
                    path = os.path.join(root, f)
                    try:
                        with open(path, "r", encoding="utf-8") as file:
                            context[path] = file.read()
                    except Exception as e:
                        print(f"⚠️ No se pudo leer {path}: {e}")

        return context
