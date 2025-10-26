# para ejecución: 
# python ai_agent/test_generator.py --app_name=companies


import os
import json
import time
import httpx
import ollama
from datetime import datetime
from collections import defaultdict
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
        self.output_dir = "/app/outputs/features"
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
    def wait_for_ollama(self, url, timeout=300):
        """Verifica que Ollama esté corriendo y que el modelo requerido esté disponible."""
        model_name = self.config.OLLAMA_MODEL
        print(f"🕓 Esperando a Ollama y al modelo '{model_name}' ...")

        start = time.time()
        while time.time() - start < timeout:
            try:
                # Verificar que el servicio Ollama esté en línea
                response = httpx.get(f"{url}/api/tags", timeout=10)
                if response.status_code == 200:
                    # Verificar si el modelo ya está disponible
                    tags = response.json().get("models", [])
                    model_names = [t.get("name", "") for t in tags]
                    if any(model_name in name for name in model_names):
                        print(f"✅ Ollama y el modelo '{model_name}' están listos.")
                        return True
                    else:
                        print(f"🔁 Modelo '{model_name}' aún no descargado, esperando...")
                else:
                    print(f"⚠️ Ollama responde con código {response.status_code}, reintentando...")
            except Exception as e:
                print(f"⏳ Aún no responde ({str(e)}), reintentando...")

            time.sleep(5)

        raise ConnectionError(
            f"❌ Tiempo agotado esperando a que Ollama y el modelo '{model_name}' estén listos."
        )

        

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


        # Agrupar archivos por carpeta (app Django)
        grouped_files = defaultdict(list)
        for path, content in files.items():
            folder = os.path.basename(os.path.dirname(path))  # ejemplo: quotations, sales
            grouped_files[folder].append((path, content))

        print(f"📦 Se agruparán {len(grouped_files)} módulos para análisis...")

        for i, (folder, file_list) in enumerate(grouped_files.items(), start=1):
            print(f"🧩 Procesando módulo {i}/{len(grouped_files)}: {folder}")
            
            # Unir el contenido de los archivos de esa app
            combined_content = "\n\n".join(
                [f"# Archivo: {os.path.basename(p)}\n{c}" for p, c in file_list]
            )

            prompt = f"""
        Analiza el siguiente conjunto de archivos pertenecientes al módulo **{folder}**
        (models, serializers y views) y genera un *un archivo .feature por cada Feature identificado** en formato Gherkin e idioma ingles.

        Reglas:
        - No incluyas texto explicativo ni análisis, solo contenido Gherkin válido.
        - Cada funcionalidad principal debe representarse como un `Feature`.
        - Usa `Scenario` claros con pasos Given/When/Then.
        - Enfócate en los flujos funcionales reales (creación, edición, validaciones, errores, etc.).
        - No uses ``` ni Markdown utiliza comentarios con # al principios
        - Responde en Inglés.
        -No anotes el lenguaje del archivo y retira los markdowns, debe ser un archivo .feature puro en Gherkin o cucucmber
        

        {combined_content}
        """

            # Resto del bloque idéntico: envías el prompt y guardas un .feature
            response = self.client.chat(
                model=self.config.OLLAMA_MODEL,
                messages=[{"role": "user", "content": prompt}],
            )
            answer = response["message"]["content"]

            feature_output_path = os.path.join(self.output_dir, f"{folder}.feature")
            with open(feature_output_path, "w", encoding="utf-8") as f:
                f.write(answer.strip())

            print(f"✅ Archivo .feature generado: {feature_output_path}")
            self.export_results(feature_output_path, f"{folder}.feature")


        #with open(output_path, "w", encoding="utf-8") as f:
        #    f.write("\n".join(all_tests))

        print(f"✅ Tests generados en: {output_path}")
        self.save_log(output_path)

        #if self.export:
        #    self.export_results(output_path)

    # ----------------------------
    # 💾 Exportación y logs
    # ----------------------------
    def export_results(self, output_path, file):
        """Copia el archivo generado a la carpeta compartida."""
        export_dir = os.path.join(
            os.getenv("PROJECT_BASE_PATH", "/workspace"), "ai_agent", "outputs", "features"
        )
        os.makedirs(export_dir, exist_ok=True)

        dest_path = os.path.join(export_dir, file)
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
            log.write(f"📄 Features generados en: {self.output_dir}\n")
        
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


    def _convert_to_feature(self, name, body):
        """
        Convierte código de test en formato Gherkin básico.
        Si el cuerpo ya contiene un bloque 'Feature:', lo conserva tal cual.
        """
        # Si ya tiene un bloque Gherkin generado por Ollama, lo reutilizamos
        if "Feature:" in body:
            feature_match = re.search(r"(Feature:.*)", body, re.DOTALL)
            if feature_match:
                return feature_match.group(1)

        # Caso contrario: generar automáticamente los escenarios desde las funciones test_
        scenarios = re.findall(r"def test_(\w+)", body)
        feature = [f"Feature: {name.replace('_', ' ').title()}"]

        for scenario in scenarios:
            feature.append(f"\n  Scenario: {scenario.replace('_', ' ').title()}")
            feature.append(f"    Given el sistema está listo")
            feature.append(f"    When se ejecuta el test {scenario}")
            feature.append(f"    Then el resultado es exitoso")

        return "\n".join(feature)

