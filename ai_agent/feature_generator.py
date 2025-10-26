import os
import re
import json
import time
import httpx
import ollama
from datetime import datetime
from ai_agent.reader import CodeReader
from ai_agent.config import Config


class ApiTestGenerator:
    """Agente para generar pruebas automatizadas basadas en código fuente y modelos Ollama."""

    def __init__(self, fast_mode=False, app_name=None, export=False, fallback=False):
        self.config = Config()
        self.reader = CodeReader(app_name=app_name)
        self.fast_mode = fast_mode
        self.app_name = app_name
        self.export = export
        self.fallback = fallback
        self.start_time = datetime.now()
        self.output_dir = "/app/outputs/tests"
        self.logs_dir = "/app/outputs/logs"

        print(f"🚀 Inicializando ApiTestGenerator con modelo={self.config.OLLAMA_MODEL}")
        print(f"🧩 Conectando cliente Ollama en {self.config.OLLAMA_BASE_URL} ...")

        # Crear cliente oficial de Ollama
        self.client = ollama.Client(host=self.config.OLLAMA_BASE_URL.strip())

        # Verificar que Ollama esté disponible
        self.wait_for_ollama(self.config.OLLAMA_BASE_URL)
        print(f"✅ Cliente Ollama inicializado correctamente en {self.config.OLLAMA_BASE_URL}")

    # ----------------------------
    # 🔍 Verificación de disponibilidad
    # ----------------------------
    def wait_for_ollama(self, url, timeout=60):
        """Verifica que Ollama esté corriendo antes de iniciar."""
        print(f"🕓 Verificando conexión con Ollama en {url} ...")
        start = time.time()
        while time.time() - start < timeout:
            try:
                response = httpx.get(f"{url}/api/tags", timeout=5)
                if response.status_code == 200:
                    print("✅ Ollama está disponible y responde correctamente.")
                    return True
            except Exception:
                time.sleep(3)
        raise ConnectionError("❌ Ollama no respondió en el tiempo esperado.")

    # ----------------------------
    # ⚙️  Generador principal de pruebas
    # ----------------------------
    def generate_tests(self):
        """Genera los tests automáticamente a partir del código fuente."""
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.logs_dir, exist_ok=True)

        files = self.reader.read_files()
        total_files = len(files)
        print(f"📂 Se leerán {total_files} archivos para análisis...")

        output_path = os.path.join(self.output_dir, "generated_test.py")
        all_tests = []

        for i, (path, content) in enumerate(files.items(), start=1):
            print(f"🧩 Procesando bloque {i}/{total_files} ({len(content)} chars)")
            try:
                prompt = f"""
Analiza el siguiente archivo y genera pruebas unitarias o de integración usando pytest.
No incluyas bloques de código Markdown (no uses ```python ni ```).
Usa comentarios normales de Python (con #) para explicar brevemente cada prueba o sección.
No agregues explicaciones fuera del código, solo comentarios dentro del mismo.
Mantén un formato limpio, profesional y compatible con pytest.

Archivo analizado: {os.path.basename(path)}

{content}
"""

                print(f"🔄 Enviando prompt a Ollama ({self.config.OLLAMA_BASE_URL})...")
                response = self.client.chat(
                    model=self.config.OLLAMA_MODEL,
                    messages=[{"role": "user", "content": prompt}],
                )

                answer = response["message"]["content"]
                print(f"💬 Respuesta de Ollama: {answer[:120]}...")

                all_tests.append(f"# ==== Tests para {os.path.basename(path)} ====\n{answer}\n")
                print(f"✅ Bloque {i} procesado correctamente.")
            except Exception as e:
                print(f"⚠️ Error procesando bloque {i}: {e}")

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(all_tests))

        print(f"✅ Tests generados en: {output_path}")
        self.save_log(output_path)

        if self.export:
            self.export_results(output_path)

    # ----------------------------
    # 💾 Exportación y logs
    # ----------------------------
    def export_results(self, output_path):
        """Copia el archivo generado a la carpeta compartida."""
        export_dir = os.path.join(
            os.getenv("PROJECT_BASE_PATH", "/workspace"), "ai_agent", "outputs", "tests"
        )
        os.makedirs(export_dir, exist_ok=True)

        dest_path = os.path.join(export_dir, "generated_test.py")
        if os.path.abspath(output_path) != os.path.abspath(dest_path):
            os.system(f"cp {output_path} {dest_path}")
            print(f"📦 Archivo exportado a {dest_path}")
        else:
            print("⚙️  Archivo ya está en la ruta destino, no se copia.")

    def save_log(self, output_path):
        """Guarda log con resumen y actualiza README.md automáticamente."""
        end_time = datetime.now()
        duration = end_time - self.start_time
        log_name = f"ai_agent_report_{end_time.strftime('%Y%m%d_%H%M%S')}.txt"
        log_path = os.path.join(self.logs_dir, log_name)

        with open(log_path, "w", encoding="utf-8") as log:
            log.write("🧠 AI AGENT EXECUTION REPORT\n")
            log.write("=" * 40 + "\n")
            log.write(f"📅 Inicio: {self.start_time}\n")
            log.write(f"📅 Fin: {end_time}\n")
            log.write(f"🧩 App: {self.app_name or 'Todas las apps'}\n")
            log.write(f"🤖 Modelo: {self.config.OLLAMA_MODEL}\n")
            log.write(
                f"⚙️ Parámetros: {'--fast ' if self.fast_mode else ''}{'--export ' if self.export else ''}{'--fallback' if self.fallback else ''}\n"
            )
            log.write(f"📂 Archivos analizados: {len(self.reader.read_files())}\n")
            log.write(f"📄 Tests generados: {output_path}\n")
            log.write(f"⏱️ Duración total: {duration}\n")
            log.write("=" * 40 + "\n")

        print(f"🪶 Log guardado en {log_path}")
        self.update_readme(end_time, duration)

    def update_readme(self, end_time, duration):
        """Actualiza el README.md con la información de la última ejecución."""
        readme_path = os.path.join(
            os.getenv("PROJECT_BASE_PATH", "/workspace"), "ai_agent", "README.md"
        )
        info = f"""
### 🧾 Última ejecución registrada
- 📅 Fecha: `{end_time.strftime("%Y-%m-%d %H:%M:%S")}`
- 🤖 Modelo usado: `{self.config.OLLAMA_MODEL}`
- 🧩 App procesada: `{self.app_name or 'Todas las apps'}`
- ⚙️ Parámetros: {'--fast' if self.fast_mode else ''} {'--export' if self.export else ''} {'--fallback' if self.fallback else ''}
- ⏱️ Duración: `{duration}`
"""
        os.makedirs(os.path.dirname(readme_path), exist_ok=True)
        if os.path.exists(readme_path):
            with open(readme_path, "r+", encoding="utf-8") as f:
                content = f.read()
                if "### 🧾 Última ejecución registrada" in content:
                    start = content.find("### 🧾 Última ejecución registrada")
                    content = content[:start] + info
                else:
                    content += "\n" + info
                f.seek(0)
                f.write(content)
                f.truncate()
            print("🪶 README.md actualizado automáticamente con la última ejecución.")
        else:
            with open(readme_path, "w", encoding="utf-8") as f:
                f.write("# 🤖 AI Agent Execution Log\n" + info)
            print(f"📘 README.md creado automáticamente en {readme_path}")


class FeatureGenerator:
    """
    Genera archivos .feature (BDD) a partir de tests generados por ApiTestGenerator.
    """

    def __init__(self, source_path=None, output_dir="outputs/features"):
        self.source_path = source_path or "outputs/tests/generated_test.py"
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)


    def generate_feature_files(self):
        """Convierte los tests de Python en archivos .feature (soporta carpeta o archivo)."""
        print(f"📘 Leyendo fuente: {self.source_path}")

        files_to_process = []

        # Si es carpeta → recorrer todo
        if os.path.isdir(self.source_path):
            for root, _, filenames in os.walk(self.source_path):
                for filename in filenames:
                    if filename.endswith(".py"):
                        files_to_process.append(os.path.join(root, filename))
            if not files_to_process:
                raise FileNotFoundError(f"No se encontraron archivos .py en {self.source_path}")
        else:
            # Si es archivo individual
            files_to_process = [self.source_path]

        feature_files = []

        for file_path in files_to_process:
            print(f"📖 Procesando archivo: {file_path}")
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
            except Exception as e:
                print(f"⚠️ No se pudo leer {file_path}: {e}")
                continue

            # Divide el contenido en secciones (solo si el archivo fue generado por ApiTestGenerator)
            if "# ==== Tests para " in content:
                sections = re.split(r"# ==== Tests para (.+?) ====", content)
                sections = [s.strip() for s in sections if s.strip()]
            else:
                # Si no tiene delimitadores, se convierte todo el archivo en un solo feature
                sections = ["tests_generales", content]

            for i in range(0, len(sections), 2):
                filename = sections[i].replace(".py", "").replace("/", "_")
                body = sections[i + 1] if i + 1 < len(sections) else ""
                feature_content = self._convert_to_feature(filename, body)
                feature_path = os.path.join(self.output_dir, f"{filename}.feature")

                with open(feature_path, "w", encoding="utf-8") as out:
                    out.write(feature_content)
                feature_files.append(feature_path)
                print(f"✅ Archivo .feature generado: {feature_path}")

        self._update_readme(feature_files)



    def _convert_to_feature(self, name, body):
        """Convierte código de test en formato Gherkin básico."""
        scenarios = re.findall(r"def test_(\w+)", body)
        feature = [f"Feature: {name.replace('_', ' ').title()}"]

        for scenario in scenarios:
            feature.append(f"\n  Scenario: {scenario.replace('_', ' ').title()}")
            feature.append(f"    Given el sistema está listo")
            feature.append(f"    When se ejecuta el test {scenario}")
            feature.append(f"    Then el resultado es exitoso")

        return "\n".join(feature)

    def _save_feature_files(self, combined_text):
        """
        Divide el archivo generado en múltiples .feature,
        uno por cada bloque que comience con 'Feature:'.
        """
        # Buscar cada bloque que empieza con 'Feature:'
        pattern = r'(Feature:[\s\S]*?)(?=\nFeature:|\Z)'
        matches = re.findall(pattern, combined_text)

        if not matches:
            print("⚠️ No se encontraron bloques Feature: en el archivo.")
            return

        os.makedirs(self.output_dir, exist_ok=True)

        for match in matches:
            # Tomar el nombre de la feature (primera línea)
            first_line = match.splitlines()[0]
            feature_name = (
                first_line.replace("Feature:", "").strip()
                .lower()
                .replace(" ", "_")
                .replace("/", "_")
            )

            # Crear archivo por feature
            file_path = os.path.join(self.output_dir, f"{feature_name}.feature")

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(match.strip() + "\n")

            print(f"✅ Archivo .feature generado: {file_path}")


    def _update_readme(self, feature_files):
        """Actualiza el README.md con la fecha de generación de features."""
        readme_path = os.path.join("/workspace/ai_agent", "README.md")
        info = f"""
### 🧩 Última generación de archivos .feature
- 📅 Fecha: `{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}`
- 📂 Archivos generados:
{os.linesep.join([f'  - {os.path.basename(f)}' for f in feature_files])}
"""
        if os.path.exists(readme_path):
            with open(readme_path, "a", encoding="utf-8") as f:
                f.write("\n" + info)
        else:
            with open(readme_path, "w", encoding="utf-8") as f:
                f.write("# 🤖 AI Agent Execution Log\n" + info)
        print("🪶 README.md actualizado con la última generación de features.")

