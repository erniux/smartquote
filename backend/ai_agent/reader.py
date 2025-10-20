import os
from textwrap import wrap

class CodeReader:
    """
    Lee automáticamente las apps Django dentro de /app y
    extrae solo los archivos models.py, serializers.py y views.py.
    Ignora migraciones, tests y otros archivos no relevantes.
    Divide el texto en "chunks" manejables para evitar errores de memoria o truncado.
    """

    def __init__(self, base_dir="/app", max_chunk_size=2000):
        self.base_dir = base_dir
        self.allowed_files = {"models.py", "serializers.py", "views.py"}
        self.max_chunk_size = max_chunk_size  # número de caracteres por bloque

    def _is_django_app(self, path):
        """Verifica si una carpeta parece una app Django (contiene models.py o apps.py)."""
        return any(os.path.exists(os.path.join(path, f)) for f in ["models.py", "apps.py"])

    def _chunk_text(self, text):
        """Divide texto largo en fragmentos manejables."""
        # wrap divide en trozos sin cortar palabras
        return wrap(text, self.max_chunk_size)

    def read_files(self):
        context_chunks = []

        files = dict(list(files.items())[:5])
        for root, _, files in os.walk(self.base_dir):
            # Evitar migraciones y tests
            if "migrations" in root or "tests" in root:
                continue

            if not self._is_django_app(root):
                continue

            for f in files:
                if f in self.allowed_files:
                    path = os.path.join(root, f)
                    try:
                        with open(path, "r", encoding="utf-8") as file:
                            content = file.read()
                            for chunk in self._chunk_text(content):
                                context_chunks.append(f"# --- {path} ---\n{chunk}")
                    except Exception as e:
                        print(f"⚠️ No se pudo leer {path}: {e}")

        return context_chunks
