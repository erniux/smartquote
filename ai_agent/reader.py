import os


class CodeReader:
    """
    Clase para leer y filtrar archivos relevantes de una o varias apps Django.
    Permite limitar por nombre de app y seleccionar solo los archivos necesarios
    (models, views, serializers, utils, etc.).
    """

    def __init__(self, app_name=None):
        self.app_name = app_name
        self.base_path = os.getenv("PROJECT_BASE_PATH", os.getcwd())
        self.extensions = [".py"]
        self.key_files = ["models.py", "views.py", "serializers.py", "utils.py"]

    def read_files(self):
        """
        Recorre el proyecto y lee solo los archivos relevantes.
        Retorna un diccionario con {ruta: contenido}.
        """
        print("📘 Leyendo estructura de código...")

        if self.app_name:
            app_path = os.path.join(self.base_path, self.app_name)
            if not os.path.exists(app_path):
                print(f"⚠️ La app '{self.app_name}' no existe en {self.base_path}. Se usará fallback.")
                return self._fallback_all_apps()
            return self._read_app(app_path)
        else:
            return self._fallback_all_apps()

    def _read_app(self, app_path):
        """Lee solo los archivos relevantes dentro de una app específica."""
        files = {}
        for root, _, filenames in os.walk(app_path):
            for filename in filenames:
                if filename in self.key_files and any(filename.endswith(ext) for ext in self.extensions):
                    full_path = os.path.join(root, filename)
                    try:
                        with open(full_path, "r", encoding="utf-8") as f:
                            content = f.read()
                            files[full_path] = content
                            print(f"📄 Archivo leído: {full_path}")
                    except Exception as e:
                        print(f"⚠️ Error leyendo {full_path}: {e}")
        if not files:
            print(f"⚠️ No se encontraron archivos relevantes en '{self.app_name}', usando fallback global.")
            return self._fallback_all_apps()
        return files

    def _fallback_all_apps(self):
        """Lee los archivos relevantes de todas las apps del proyecto."""
        files = {}
        for root, _, filenames in os.walk(self.base_path):
            for filename in filenames:
                if filename in self.key_files and any(filename.endswith(ext) for ext in self.extensions):
                    full_path = os.path.join(root, filename)
                    try:
                        with open(full_path, "r", encoding="utf-8") as f:
                            content = f.read()
                            files[full_path] = content
                            print(f"📄 Archivo leído (fallback): {full_path}")
                    except Exception as e:
                        print(f"⚠️ Error leyendo {full_path}: {e}")
        print(f"✅ Total de archivos relevantes encontrados: {len(files)}")
        return files
