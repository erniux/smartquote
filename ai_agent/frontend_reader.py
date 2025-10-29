# ai_agent/frontend_reader.py
import os

class FrontendReader:
    """
    Lee archivos del frontend (React) para generar features de UI.
    Escanea /app/frontend/src/pages y /app/frontend/src/components.
    """
    def __init__(self, base_path="/app/frontend", app_name=None):
        self.base_path = base_path
        self.app_name = app_name  # 👈 nuevo
        self.src = os.path.join(base_path, "src")
        self.include_dirs = ["pages", "components"]
        self.extensions = (".jsx", ".tsx", ".js", ".ts")

        # normalizamos el nombre de la app para machear carpetas (Quotations, Sales…)
        self.app_hint = None
        if app_name:
            # "quotations" -> "Quotations"
            self.app_hint = app_name[0].upper() + app_name[1:]

    def _match_app(self, path: str) -> bool:
        """Si hay app_name, filtra rutas que contengan esa carpeta (p.ej. /pages/Quotations/...)."""
        if not self.app_hint:
            return True
        return (f"/{self.app_hint}/" in path) or (path.endswith(f"/{self.app_hint}.jsx") or path.endswith(f"/{self.app_hint}.tsx"))

    def read_files(self):
        files = {}
        if not os.path.exists(self.src):
            print(f"⚠️ No existe {self.src} dentro del contenedor.")
            return files

        for d in self.include_dirs:
            root_dir = os.path.join(self.src, d)
            for root, _, names in os.walk(root_dir):
                for name in names:
                    if name.endswith(self.extensions):
                        full = os.path.join(root, name)
                        if not self._match_app(full):
                            continue
                        try:
                            with open(full, "r", encoding="utf-8", errors="ignore") as f:
                                files[full] = f.read()
                                print(f"📄 (FE) Archivo leído: {full}")
                        except Exception as e:
                            print(f"⚠️ Error leyendo {full}: {e}")

        print(f"✅ Total FE archivos leídos: {len(files)}")
        return files
