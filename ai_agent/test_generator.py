# para ejecución: 
# python ai_agent/test_generator.py --app_name=companies


import os
import re
import json
import time
import httpx
import ollama
from datetime import datetime
from collections import defaultdict
from ai_agent.reader import CodeReader
from ai_agent.config import Config


class TestGenerator:
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

        print(f"🚀 Inicializando TestGenerator con modelo={self.config.OLLAMA_MODEL}")
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

            system_prompt = (
                "You are a Senior QA Automation Engineer (SDET) certified in ISTQB Requirements Analysis. "
                "You always output strict and valid Gherkin syntax without explanations or summaries. "
                "Your task is to analyze Django source code and generate executable .feature files suitable for pytest-bdd or Cucumber."
            )

            prompt = f"""
            Assume you are acting as a **Senior SDET Test Analyst Engineer** certified in **ISTQB Requirements Analysis**.
            Analyze the following Django module named **{folder}**, including its models, serializers, and views,
            and generate a **single valid Cucumber .feature file** that contains all functional and edge-case scenarios.

            {combined_content}
            """

            # Resto del bloque idéntico: envías el prompt y guardas un .feature
            response = self.client.chat(
                model=self.config.OLLAMA_MODEL,
                #messages=[{"role": "user", "content": prompt}],
                 messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
                    ],
                )
            answer = response["message"]["content"]

            #print(f"✅ Primer respuesta: {answer}")
            
            prompt = f""" with {answer} generate a .feature file, Follow these strict rules:
            - Your response must contain only valid Gherkin syntax.
            - Do NOT explain, summarize, or describe the code.
            - Do NOT include Markdown symbols, headers, code fences, or commentary.
            - Each source file must be represented as a `Feature`.
            - Each Scenario must include clear Given / When / Then steps written in English.
            - Focus on realistic user interactions, validation errors, and business rules.
            - Avoid restating this prompt. Only return the .feature file content.

            """

            response = self.client.chat(
                model=self.config.OLLAMA_MODEL,
                messages=[{"role": "user", "content": prompt}],
                )
            answer = response["message"]["content"]
            print(f"✅ Segunda respuesta: {answer}")

            feature_output_path = os.path.join(self.output_dir, f"{folder}.feature")
            with open(feature_output_path, "w", encoding="utf-8") as f:
                f.write(answer)
            

            print(f"✅ Archivo .feature generado: {feature_output_path}")
            self.export_results(feature_output_path, f"{folder}.feature")

            # -------------------------------
            # 🧩 Crear estructura E2E paralela (API/UI)
            # -------------------------------
            bdd_base_dir = f"/app/bdd/tests/features/{folder}"
            bdd_api_dir = os.path.join(bdd_base_dir, "api")
            bdd_ui_dir = os.path.join(bdd_base_dir, "ui")
            os.makedirs(bdd_api_dir, exist_ok=True)
            os.makedirs(bdd_ui_dir, exist_ok=True)

            # Normalizar nombres (sin extensión)
            base_name = os.path.splitext(file_name if 'file_name' in locals() else f"{folder}.feature")[0]
            api_feature_path = os.path.join(bdd_api_dir, f"{folder}_api.feature")
            ui_feature_path = os.path.join(bdd_ui_dir, f"{folder}_ui.feature")

            # Crear contenido adaptado
            api_content = f"Feature: {folder.title()} API\n\n" + answer.strip()
            ui_content = f"Feature: {folder.title()} UI\n\n" + answer.strip()

            # Guardar duplicados
            with open(api_feature_path, "w", encoding="utf-8") as api_f:
                api_f.write(api_content)
            with open(ui_feature_path, "w", encoding="utf-8") as ui_f:
                ui_f.write(ui_content)

            print(f"📄 Feature API duplicado en {api_feature_path}")
            print(f"📄 Feature UI duplicado en {ui_feature_path}")

            # 🔗 Crear marcador de sincronización
            sync_marker = os.path.join(bdd_base_dir, "_sync.json")
            with open(sync_marker, "w", encoding="utf-8") as sync_f:
                json.dump({
                    "base_feature": feature_output_path,
                    "api_feature": api_feature_path,
                    "ui_feature": ui_feature_path,
                    "timestamp": datetime.now().isoformat()
                }, sync_f, indent=4)
            print(f"🧭 Sincronización registrada en {sync_marker}")


        print(f"✅ Tests generados en: {output_path}")
        self.save_log(output_path)


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


    def save_log(self, output_path, mode="features"):
        """
        Guarda un log con resumen de ejecución y actualiza README.md automáticamente.
        Incluye detalles E2E (features + steps) si se ejecutó con --full.
        """
        end_time = datetime.now()
        duration = end_time - self.start_time
        log_name = f"ai_agent_report_{end_time.strftime('%Y%m%d_%H%M%S')}.txt"
        log_path = os.path.join(self.logs_dir, log_name)

        # Detectar carpetas E2E
        features_base = f"/app/bdd/tests/features/{self.app_name or 'unknown'}"
        steps_base = f"/app/bdd/tests/steps/{self.app_name or 'unknown'}"

        def list_files_safe(path):
            try:
                result = []
                for root, _, files in os.walk(path):
                    for f in files:
                        if f.endswith((".feature", ".py")):
                            result.append(os.path.join(root, f))
                return result
            except FileNotFoundError:
                return []

        features = list_files_safe(features_base)
        steps = list_files_safe(steps_base)

        # 🪶 Escribir log
        with open(log_path, "w", encoding="utf-8") as log:
            log.write("🧠 AI AGENT EXECUTION REPORT\n")
            log.write("=" * 60 + "\n")
            log.write(f"📅 Inicio: {self.start_time}\n")
            log.write(f"📅 Fin: {end_time}\n")
            log.write(f"🧩 App: {self.app_name or 'Todas las apps'}\n")
            log.write(f"🤖 Modelo: {self.config.OLLAMA_MODEL}\n")
            log.write(f"⚙️ Modo de ejecución: {mode}\n")
            log.write(f"⏱️ Duración total: {duration}\n")
            log.write("=" * 60 + "\n")

            if features:
                log.write("\n📄 Features generados:\n")
                for f in features:
                    log.write(f"   - {f}\n")
            else:
                log.write("\n📄 Features: No se encontraron archivos.\n")

            if steps:
                log.write("\n🐍 Steps generados:\n")
                for s in steps:
                    log.write(f"   - {s}\n")
            else:
                log.write("\n🐍 Steps: No se encontraron archivos.\n")

            log.write("\n" + "=" * 60 + "\n")
            log.write(f"🗂 Logs almacenados en: {self.logs_dir}\n")

        print(f"🪶 Log detallado guardado en {log_path}")

        # ✅ Actualizar README con resumen
        self.update_readme_e2e(end_time, duration, features, steps, mode)


    def update_readme_e2e(self, end_time, duration, features, steps, mode):
        """Actualiza el README.md con resumen E2E de la última ejecución."""
        readme_path = os.path.join(
            os.getenv("PROJECT_BASE_PATH", "/workspace"), "ai_agent", "README.md"
        )

        info = f"""
    ### 🧩 Última ejecución E2E completa
    - 📅 Fecha: `{end_time.strftime("%Y-%m-%d %H:%M:%S")}`
    - 🤖 Modelo usado: `{self.config.OLLAMA_MODEL}`
    - 🧩 App procesada: `{self.app_name or 'Todas las apps'}`
    - ⚙️ Modo de ejecución: `{mode}`
    - ⏱️ Duración: `{duration}`

    #### 📄 Features generados
    {chr(10).join(f"- {os.path.relpath(f, '/app')}" for f in features) if features else "No se encontraron features."}

    #### 🐍 Steps generados
    {chr(10).join(f"- {os.path.relpath(s, '/app')}" for s in steps) if steps else "No se encontraron steps."}
    """

        os.makedirs(os.path.dirname(readme_path), exist_ok=True)
        if os.path.exists(readme_path):
            with open(readme_path, "r+", encoding="utf-8") as f:
                content = f.read()
                if "### 🧩 Última ejecución E2E completa" in content:
                    start = content.find("### 🧩 Última ejecución E2E completa")
                    content = content[:start] + info
                else:
                    content += "\n" + info
                f.seek(0)
                f.write(content)
                f.truncate()
        else:
            with open(readme_path, "w", encoding="utf-8") as f:
                f.write("# 🤖 AI Agent Execution Log\n" + info)

        print("📘 README.md actualizado con resumen E2E ✅")


    def convert_to_steps(self, prefix="core"):
        """
        Convierte los archivos .feature en dos conjuntos de steps (API y UI) 
        dentro de bdd/tests/steps/<app_name>/api y ui.
        """
        import re

        features_dir = "/app/bdd/tests/features"
        base_steps_dir = f"/app/bdd/tests/steps/{prefix}"
        steps_ui_dir = os.path.join(base_steps_dir, "ui")
        steps_api_dir = os.path.join(base_steps_dir, "api")

        os.makedirs(steps_ui_dir, exist_ok=True)
        os.makedirs(steps_api_dir, exist_ok=True)

        print(f"🔍 Buscando archivos .feature con prefijo '{prefix}' en {features_dir}")

        for file_name in os.listdir(features_dir):
            if file_name.startswith(prefix) and file_name.endswith(".feature"):
                feature_path = os.path.join(features_dir, file_name)
                with open(feature_path, "r", encoding="utf-8") as f:
                    feature_content = f.read()

                print(f"🧩 Procesando {file_name}...")

                # 🧠 Detectar tipo de pasos según keywords
                feature_lower = feature_content.lower()
                contains_api = any(word in feature_lower for word in ["api", "endpoint", "http", "request", "json", "response"])
                contains_ui = any(word in feature_lower for word in ["click", "page", "navigate", "browser", "form", "button", "input"])

                # ⚙️ Siempre generaremos ambos (UI + API)
                print(f"🧠 Generando pasos UI y API para: {prefix}")

                # -------------------------------
                # 🧩 PROMPT PARA API
                # -------------------------------
                api_prompt = f"""
    Eres un SDET Senior especializado en pruebas de API con pytest-bdd.
    Del siguiente archivo .feature genera el archivo de steps para pruebas de API usando Python y la librería 'requests'.
    Asegúrate de:
    - Incluir import requests, pytest y pytest_bdd
    - Implementar pasos para CRUD en endpoints tipo '/api/{prefix}/'
    - Verificar status_code y campos JSON
    - No incluir texto, explicaciones ni comentarios
    - Cada función debe tener cuerpo ejecutable o al menos un pass

    Archivo: {file_name}
    Contenido:
    {feature_content}
    """

                api_response = self.client.chat(
                    model=self.config.OLLAMA_MODEL,
                    messages=[{"role": "user", "content": api_prompt}],
                )
                api_code = api_response["message"]["content"]

                # Limpieza básica
                api_code = re.sub(r"```[a-zA-Z]*", "", api_code)
                api_code = re.sub(r"#.*", "", api_code)
                api_code = api_code.strip()

                # Insertar pass si vacío
                api_code = re.sub(
                    r"(def [\w_]+\([^\)]*\):)(\s*\n(?!\s+pass\b))",
                    r"\1\n    pass\n",
                    api_code
                )

                # Guardar
                api_output = os.path.join(steps_api_dir, f"{prefix}_api_steps.py")
                with open(api_output, "w", encoding="utf-8") as f:
                    f.write(api_code)
                print(f"✅ Archivo API guardado en {api_output}")

                # -------------------------------
                # 🧩 PROMPT PARA UI
                # -------------------------------
                ui_prompt = f"""
    Eres un SDET Senior especializado en automatización UI con Playwright y pytest-bdd.
    Del siguiente archivo .feature genera el archivo de steps para pruebas UI usando Python y playwright.sync_api.
    Asegúrate de:
    - Importar pytest, pytest_bdd, playwright.sync_api y expect
    - Usar funciones page.goto(), page.fill(), page.click(), expect()
    - No incluir texto, explicaciones ni comentarios
    - Cada función debe tener cuerpo ejecutable o al menos un pass
    - Usa la ruta base del frontend correspondiente al módulo '{prefix}'

    Archivo: {file_name}
    Contenido:
    {feature_content}
    """

                ui_response = self.client.chat(
                    model=self.config.OLLAMA_MODEL,
                    messages=[{"role": "user", "content": ui_prompt}],
                )
                ui_code = ui_response["message"]["content"]

                # Limpieza
                ui_code = re.sub(r"```[a-zA-Z]*", "", ui_code)
                ui_code = re.sub(r"#.*", "", ui_code)
                ui_code = ui_code.strip()

                # Asegurar pass si vacío
                ui_code = re.sub(
                    r"(def [\w_]+\([^\)]*\):)(\s*\n(?!\s+pass\b))",
                    r"\1\n    pass\n",
                    ui_code
                )

                # Guardar
                ui_output = os.path.join(steps_ui_dir, f"{prefix}_ui_steps.py")
                with open(ui_output, "w", encoding="utf-8") as f:
                    f.write(ui_code)
                print(f"✅ Archivo UI guardado en {ui_output}")

        print("🎉 Conversión E2E completada con éxito.")
