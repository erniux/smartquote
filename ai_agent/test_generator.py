# ai_agent/test_generator.py
# para ejecución:
# python ai_agent/test_generator.py --app_name=companies

import os
import re
import json
import time
import httpx
import ollama
import subprocess
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from ai_agent.reader import CodeReader
from ai_agent.config import Config
from ai_agent.frontend_reader import FrontendReader


class TestGenerator:
    """Agente para generar pruebas automatizadas basadas en código fuente y modelos Ollama."""

    def __init__(self, fast_mode=False, app_name=None, export=False, fallback=False, source="backend"):
        self.config = Config()
        self.source = source
        # Elegir reader según la fuente
        if source == "frontend":
            self.reader = FrontendReader(app_name=app_name)
        else:
            self.reader = CodeReader(app_name=app_name)

        print(f"📚 Source seleccionado: {self.source} | Reader: {self.reader.__class__.__name__}")

        self.fast_mode = fast_mode
        self.app_name = app_name
        self.export = export
        self.fallback = fallback
        self.start_time = datetime.now()

        # 👇 ahora los .feature van directo a la misma carpeta de features de BDD
        self.features_dir = "/app/bdd/tests/features"
        self.logs_dir = "/app/outputs/logs"

        print(f"🚀 Inicializando TestGenerator con modelo={self.config.OLLAMA_MODEL}")
        print(f"🧩 Conectando cliente Ollama en {self.config.OLLAMA_BASE_URL} ...")

        # Cliente Ollama
        self.client = ollama.Client(host=self.config.OLLAMA_BASE_URL.strip())

        # Verificar disponibilidad
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
                response = httpx.get(f"{url}/api/tags", timeout=10)
                if response.status_code == 200:
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
        """Genera los tests features automáticamente a partir del código fuente."""
        os.makedirs(self.features_dir, exist_ok=True)
        os.makedirs(self.logs_dir, exist_ok=True)

        files = self.reader.read_files()
        total_files = len(files)
        print(f"📂 Se leerán {total_files} archivos para análisis...")

        # Agrupar archivos por carpeta (app)
        grouped_files = defaultdict(list)
        for path, content in files.items():
            folder = os.path.basename(os.path.dirname(path))  # quotations, sales, etc.
            grouped_files[folder].append((path, content))

        print(f"📦 Se agruparán {len(grouped_files)} módulos para análisis...")

        for i, (folder, file_list) in enumerate(grouped_files.items(), start=1):
            print(f"🧩 Procesando módulo {i}/{len(grouped_files)}: {folder}")

            # Unir contenido
            combined_content = "\n\n".join(
                [f"# Archivo: {os.path.basename(p)}\n{c}" for p, c in file_list]
            )

            # Prompts estrictos por fuente
            if self.source == "backend":
                system_prompt = (
                    "You are a Senior QA Automation Engineer (SDET). "
                    "You output ONLY strict and valid Gherkin: no markdown, no comments, no prose."
                )
                prompt = f"""
Analyze Django module **{folder}** (models/serializers/views) and generate a SINGLE valid Gherkin .feature
for API behaviors (auth, CRUD, validation, permissions, HTTP errors).
STRICT RULES:
- Return ONLY Gherkin content.
- Start with 'Feature: {folder.title()} API'
- Include multiple 'Scenario:' blocks with Given/When/Then (and And/But).
- Include edge cases as possible.
- No natural-language paragraphs, no explanations, no code fences.

{combined_content}
"""
            else:
                system_prompt = (
                    "You are a Senior QA Engineer specialized in Web E2E with Playwright. "
                    "You output ONLY strict and valid Gherkin: no markdown, no comments, no prose."
                )
                prompt = f"""
Analyze React module **{folder}** (pages/components) and generate a SINGLE valid Gherkin .feature
for UI flows (navigation, login, forms, clicks, success/error messages, route guards).
STRICT RULES:
- Return ONLY Gherkin content.
- Start with 'Feature: {folder.title()} UI'
- Include multiple 'Scenario:' blocks with Given/When/Then (and And/But).
- Include edge cases as possible.
- No natural-language paragraphs, no explanations, no code fences.

{combined_content}
"""

            # Llamada al modelo (1ª)
            response = self.client.chat(
                model=self.config.OLLAMA_MODEL,
                messages=[{"role": "system", "content": system_prompt},
                          {"role": "user", "content": prompt}],
            )
            answer = response["message"]["content"]

            # 2ª vuelta pidiendo SOLO Gherkin (refuerzo)
            response = self.client.chat(
                model=self.config.OLLAMA_MODEL,
                messages=[{"role": "user", "content": f"Return ONLY valid Gherkin for the previous analysis.\n{answer}"}],
            )
            answer = response["message"]["content"]

            # Validar + sanitizar Gherkin
            if not self._is_valid_gherkin(answer):
                print("⚠️ Respuesta no válida como Gherkin. Reintentando con prompt estricto…")
                strict_msgs = self._second_chance_prompt(folder, self.source, combined_content)
                response = self.client.chat(model=self.config.OLLAMA_MODEL, messages=strict_msgs)
                answer = response["message"]["content"]

            answer = self._sanitize_to_gherkin(
                answer,
                title_fallback=f"{folder.title()} {'API' if self.source=='backend' else 'UI'}"
            )

            # ✅ Guardar .feature en la misma carpeta /features/
            suffix = "api" if self.source == "backend" else "ui"
            feature_filename = f"{folder}_{suffix}.feature"
            feature_output_path = os.path.join(self.features_dir, feature_filename)
            with open(feature_output_path, "w", encoding="utf-8") as f:
                f.write(answer)

            print(f"✅ Archivo .feature generado: {feature_output_path}")

        # Log final
        self.save_log(self.features_dir)

    # ----------------------------
    # 💾 Logs
    # ----------------------------
    def save_log(self, _unused_output_path, mode="features"):
        """
        Guarda un log con resumen de ejecución y actualiza README.md automáticamente.
        """
        end_time = datetime.now()
        duration = end_time - self.start_time
        log_name = f"ai_agent_report_{end_time.strftime('%Y%m%d_%H%M%S')}.txt"
        os.makedirs(self.logs_dir, exist_ok=True)
        log_path = os.path.join(self.logs_dir, log_name)

        features_base = "/app/bdd/tests/features"
        steps_base = "/app/bdd/tests/steps"  # 👈 corregido

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
                log.write("\n🐍 Steps presentes:\n")
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
        """Actualiza el README.md con resumen de la última ejecución."""
        readme_path = os.path.join(
            os.getenv("PROJECT_BASE_PATH", "/workspace"), "ai_agent", "README.md"
        )

        info = f"""
### 🧩 Última ejecución
- 📅 Fecha: `{end_time.strftime("%Y-%m-%d %H:%M:%S")}`
- 🤖 Modelo usado: `{self.config.OLLAMA_MODEL}`
- 🧩 App procesada: `{self.app_name or 'Todas las apps'}`
- ⚙️ Modo de ejecución: `{mode}`
- ⏱️ Duración: `{duration}`

#### 📄 Features en `bdd/tests/features`
{chr(10).join(f"- {os.path.relpath(f, '/app')}" for f in features) if features else "No se encontraron features."}

#### 🐍 Steps en `bdd/tests/steps`
{chr(10).join(f"- {os.path.relpath(s, '/app')}" for s in steps) if steps else "No se encontraron steps."}
"""

        os.makedirs(os.path.dirname(readme_path), exist_ok=True)
        if os.path.exists(readme_path):
            with open(readme_path, "r+", encoding="utf-8") as f:
                content = f.read()
                if "### 🧩 Última ejecución" in content:
                    start = content.find("### 🧩 Última ejecución")
                    content = content[:start] + info
                else:
                    content += "\n" + info
                f.seek(0)
                f.write(content)
                f.truncate()
        else:
            with open(readme_path, "w", encoding="utf-8") as f:
                f.write("# 🤖 AI Agent Execution Log\n" + info)

        print("📘 README.md actualizado con resumen ✅")

    # ----------------------------
    # 🧰 Utilidades de Gherkin
    # ----------------------------
    def _is_valid_gherkin(self, text: str) -> bool:
        if not text:
            return False
        t = text.strip()
        if "Feature:" not in t or "Scenario" not in t:
            return False
        # Debe tener al menos un Given/When/Then (o And/But después)
        has_step = any(k in t for k in [" Given ", "\nGiven ", " When ", "\nWhen ", " Then ", "\nThen "])
        return has_step

    def _sanitize_to_gherkin(self, text: str, title_fallback: str = "Feature") -> str:
        """
        Conserva SOLO líneas Gherkin: Feature/Background/Scenario/Scenario Outline/Examples y pasos Given/When/Then/And/But.
        Borra cualquier explicación, markdown, etc.
        """
        allowed = ("Feature:", "Background:", "Scenario:", "Scenario Outline:", "Examples:",
                   "Given ", "When ", "Then ", "And ", "But ")
        lines = []
        for raw in text.replace("\r\n", "\n").split("\n"):
            line = raw.strip()
            if not line:
                lines.append("")
                continue
            if any(line.startswith(tok) for tok in allowed):
                lines.append(line)
            elif line.startswith("|") and line.endswith("|"):
                lines.append(line)
        cleaned = "\n".join([l for l in lines if l is not None]).strip()
        if not cleaned.startswith("Feature:"):
            cleaned = f"Feature: {title_fallback}\n\n" + cleaned
        return cleaned.strip()

    def _second_chance_prompt(self, folder: str, source: str, combined_content: str) -> list:
        """Mensajes de re-intento hiper-estrictos cuando el modelo narró en vez de Gherkin."""
        sys = ("You output ONLY strict, valid Gherkin. No explanations, no markdown, no comments. "
               "If information is missing, invent reasonable steps, but still return ONLY Gherkin.")
        if source == "backend":
            usr = f"""Generate a single valid Gherkin .feature for API behaviors of module "{folder}".
Focus on realistic flows and edge cases (auth, 4xx/5xx, permissions, validation).
STRICT RULES:
- Return ONLY Gherkin content.
- Start with 'Feature: {folder.title()} API'
- Include multiple 'Scenario:' blocks with Given/When/Then (and And/But).
- No natural-language paragraphs, no code fences.

{combined_content}
"""
        else:
            usr = f"""Generate a single valid Gherkin .feature for UI behaviors of module "{folder}".
Focus on real user flows (navigation, forms, clicks, messages, guards).
STRICT RULES:
- Return ONLY Gherkin content.
- Start with 'Feature: {folder.title()} UI'
- Include multiple 'Scenario:' blocks with Given/When/Then (and And/But).
- No natural-language paragraphs, no code fences.

{combined_content}
"""
        return [{"role": "system", "content": sys}, {"role": "user", "content": usr}]
