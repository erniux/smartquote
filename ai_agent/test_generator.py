# ai_agent/test_generator.py
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
        self.output_dir = "/app/outputs/features"
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
        """Genera los tests automáticamente a partir del código fuente."""
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.logs_dir, exist_ok=True)

        files = self.reader.read_files()
        total_files = len(files)
        print(f"📂 Se leerán {total_files} archivos para análisis...")

        output_path = os.path.join(self.output_dir, "generated_test.py")

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

            # Guardar .feature base (en outputs)
            feature_output_path = os.path.join(self.output_dir, f"{folder}.feature")
            with open(feature_output_path, "w", encoding="utf-8") as f:
                f.write(answer)

            print(f"✅ Archivo .feature generado: {feature_output_path}")
            self.export_results(feature_output_path, f"{folder}.feature")

            # -------------------------------
            # 🧩 Crear estructura E2E paralela (condicional por source)
            # -------------------------------
            bdd_base_dir = f"/app/bdd/tests/features/{folder}"
            if self.source == "backend":
                bdd_api_dir = os.path.join(bdd_base_dir, "api")
                os.makedirs(bdd_api_dir, exist_ok=True)
                api_feature_path = os.path.join(bdd_api_dir, f"{folder}_api.feature")
                api_content = answer.strip()
                if not api_content.startswith("Feature:"):
                    api_content = f"Feature: {folder.title()} API\n\n{api_content}"
                with open(api_feature_path, "w", encoding="utf-8") as api_f:
                    api_f.write(api_content)
                print(f"📄 Feature API duplicado en {api_feature_path}")
                ui_feature_path = None
            else:
                bdd_ui_dir = os.path.join(bdd_base_dir, "ui")
                os.makedirs(bdd_ui_dir, exist_ok=True)
                ui_feature_path = os.path.join(bdd_ui_dir, f"{folder}_ui.feature")
                ui_content = answer.strip()
                if not ui_content.startswith("Feature:"):
                    ui_content = f"Feature: {folder.title()} UI\n\n{ui_content}"
                with open(ui_feature_path, "w", encoding="utf-8") as ui_f:
                    ui_f.write(ui_content)
                print(f"📄 Feature UI duplicado en {ui_feature_path}")
                api_feature_path = None

            # 🔗 Marcador de sincronización
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
        Incluye detalles E2E (features + steps) si se ejecutó con --full/--both.
        """
        end_time = datetime.now()
        duration = end_time - self.start_time
        log_name = f"ai_agent_report_{end_time.strftime('%Y%m%d_%H%M%S')}.txt"
        log_path = os.path.join(self.logs_dir, log_name)

        # Detectar carpetas E2E
        features_base = f"/app/bdd/tests/features/{self.app_name or 'unknown'}"
        steps_base = f"/app/bdd/tests/features/steps/{self.app_name or 'unknown'}"

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

    # ----------------------------
    # 🔁 Conversión .feature → steps (API y UI)
    # ----------------------------
    def convert_to_steps(self, prefix="quotations"):
        """
        Conversión SIMPLE de .feature -> steps (pytest-bdd).
        - Prompt corto para Ollama (API y UI).
        - Sin 'ctx' ni 'context' en firmas.
        - Siempre incluye 'scenarios(<ruta_relativa>)'.
        - Si no hay implementación, deja 'pass'.
        """

        # Ajusta a 'bdd/tests' si ése es tu árbol real
        FEATURES_ROOT = "/app/bdd/tests/features"
        STEPS_ROOT    = f"/app/bdd/tests/features/steps/{prefix}"

        UI_STEPS_DIR  = os.path.join(STEPS_ROOT, "ui")
        API_STEPS_DIR = os.path.join(STEPS_ROOT, "api")
        os.makedirs(UI_STEPS_DIR, exist_ok=True)
        os.makedirs(API_STEPS_DIR, exist_ok=True)

        def _strip_fences(txt: str) -> str:
            txt = re.sub(r"```[a-zA-Z]*", "", txt)
            txt = re.sub(r"^\s*(Here is|A continuación|Below is|This file).*?$", "", txt,
                        flags=re.IGNORECASE | re.MULTILINE)
            return txt.strip()

        def _drop_context_params(code: str) -> str:
            """
            Elimina 'context' y 'ctx' de las firmas de funciones step.
            Ej.: def foo(context, page): -> def foo(page):
            Mantiene los dos puntos y respeta el resto de parámetros.
            """
            import re

            pattern = re.compile(r"(def\s+)(?P<name>[A-Za-z_]\w*)\s*\((?P<params>[^)]*)\)\s*:")

            def repl(m: re.Match) -> str:
                name = m.group("name")
                params = m.group("params")
                parts = [p.strip() for p in params.split(",") if p.strip()]
                parts = [p for p in parts if p not in ("context", "ctx")]
                new_params = ", ".join(parts)
                return f"def {name}({new_params}):"

            return pattern.sub(repl, code)


        def _ensure_header_and_scenarios(code: str, rel_feature: str, is_ui: bool) -> str:
            header_lines = [
                "import os",
                "from playwright.sync_api import sync_playwright,Page"
                "from behave import given, when, then"
                f"from pages import {rel_feature}_page"
            ]
            header = "\n".join(header_lines) + "\n\n"

            if "scenarios(" not in code:
                code = header + f'scenarios(r"{rel_feature}")\n\n' + code
            else:
                # si ya trae scenarios, aseguramos imports al principio
                if not code.lstrip().startswith("import") and "from pytest_bdd" not in code.splitlines()[0]:
                    code = header + code
            return code

        def _ensure_bodies(code: str) -> str:
            # si el cuerpo de una función está vacío, agrega 'pass'
            return re.sub(
                r"(def [\w_]+\([^\)]*\):)(\s*\n(?!\s+[^#\s]))",
                r"\1\n    pass\n",
                code
            )

        print(f"🔍 Buscando .feature de '{prefix}' en {FEATURES_ROOT}…")
        for root, _, files in os.walk(FEATURES_ROOT):
            for fname in files:
                if not fname.endswith(".feature"):
                    continue
                # filtra por prefijo (en nombre o ruta)
                if prefix not in fname and prefix not in root:
                    continue

                feature_path = os.path.join(root, fname)
                rel_from_api = os.path.relpath(feature_path, API_STEPS_DIR)
                rel_from_ui  = os.path.relpath(feature_path, UI_STEPS_DIR)

                with open(feature_path, "r", encoding="utf-8") as f:
                    feature_gherkin = f.read()

                is_api = "/api/" in feature_path.replace("\\","/")
                is_ui  = "/ui/"  in feature_path.replace("\\","/")

                if is_api:
                    prompt = f"""
                    Based on the attached file, that is a feature file, design a steps file using python-bdd. Not necesary to know the analysis you did to generate the file, just attach the final steps file
                    Feature file:
                    {feature_gherkin}
                    """
                    resp = self.client.chat(
                        model=self.config.OLLAMA_MODEL,
                        messages=[{"role":"user","content":prompt}],
                    )
                    code = _strip_fences(resp["message"]["content"])
                    code = _drop_context_params(code)
                    # header + scenarios(relpath)
                    code = _ensure_header_and_scenarios(code, rel_from_api, is_ui=False)
                    code = _ensure_bodies(code)

                    step_name = os.path.splitext(fname)[0] + "_steps.py"
                    out_path = os.path.join(API_STEPS_DIR, step_name)
                    with open(out_path, "w", encoding="utf-8") as w:
                        w.write(code)
                    print(f"✅ API steps -> {out_path}")

                if is_ui:
                    prompt = f"""
                    Based on the attached file, that is a feature file, design a steps file using python-bdd.
                    Feature file:
                    {feature_gherkin}
                    """
                    resp = self.client.chat(
                        model=self.config.OLLAMA_MODEL,
                        messages=[{"role":"user","content":prompt}],
                    )
                    code = _strip_fences(resp["message"]["content"])
                    code = _drop_context_params(code)
                    code = _ensure_header_and_scenarios(code, rel_from_ui, is_ui=True)
                    code = _ensure_bodies(code)

                    step_name = os.path.splitext(fname)[0] + "_steps.py"
                    out_path = os.path.join(UI_STEPS_DIR, step_name)
                    with open(out_path, "w", encoding="utf-8") as w:
                        w.write(code)
                    print(f"✅ UI steps  -> {out_path}")

        print("🎉 Conversión SIMPLE completada.")


    # ----------------------------
    # 🧰 Utilidades de Gherkin / Steps
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


    def _cleanup_python_code(self, code: str) -> str:

        # 1) quitar fences/markdown
        code = re.sub(r"```[a-zA-Z]*", "", code)
        # quitar encabezados tipo "Here is..." o prólogos narrativos frecuentes
        code = re.sub(r"^\s*(Here is|A continuación|Below is|This file).*?$", "",
                    code, flags=re.IGNORECASE | re.MULTILINE)

        # 2) conservar SOLO líneas "de código" (imports, decorators, defs, escenarios)
        kept = []
        allowed_starts = (
            "import ", "from ", "@", "def ", "class ", "scenarios(", "pytest.", "requests.", "os.", ""
        )
        for raw in code.replace("\r\n", "\n").split("\n"):
            line = raw.rstrip()
            # líneas en blanco pasan
            if not line.strip():
                kept.append("")
                continue
            # líneas válidas de código
            if line.lstrip().startswith(allowed_starts):
                kept.append(line)
            # ignora todo lo demás (prosa, comentarios no útiles)
        code = "\n".join(kept)

        # 3) eliminar 'self' de firmas
        code = re.sub(r"\bdef\s+([a-zA-Z_]\w*)\s*\(\s*self\s*(,)?", r"def \1(", code)

        # 4) asegurar 'ctx' en firmas de steps
        code = re.sub(
            r"(def\s+[a-zA-Z_]\w*\s*\()([^\)]*)\)",
            lambda m: f"{m.group(1)}{self._ensure_ctx_in_params(m.group(2))})",
            code
        )

        # 5) encabezados/imports mínimos y deduplicación simple
        blocks = []

        def ensure_once(src: str, snippet: str) -> None:
            if snippet not in src:
                blocks.append(snippet)

        ensure_once(code, "from pytest_bdd import given, when, then, scenarios")
        ensure_once(code, "import pytest")
        if "requests." in code:
            ensure_once(code, "import requests")
        ensure_once(code, "from urllib.parse import urljoin")

        header = "\n".join(blocks)
        if header:
            code = header + "\n\n" + code

        # 6) normalize: requests.*(...) -> ctx["response"] = ...
        code = re.sub(
            r"(\s*)(response\s*=\s*)?requests\.(get|post|put|delete)\(([^)]+)\)",
            lambda m: f'{m.group(1)}ctx["response"] = requests.{m.group(3)}({m.group(4)})',
            code
        )

        # 7) URLs relativas -> urljoin(api_base_url(), "/path")
        code = re.sub(
            r'ctx\["response"\]\s*=\s*requests\.(get|post|put|delete)\(\s*["\'](/[^"\']*)["\']\s*(,|\))',
            r'ctx["response"] = requests.\1(urljoin(api_base_url(), r"\2")\3',
            code
        )

        # 8) asegurar 'pass' si el cuerpo quedó vacío
        code = re.sub(
            r"(def [\w_]+\([^\)]*\):)(\s*\n(?!\s+[^#\s]))",
            r"\1\n    pass\n",
            code
        )

        # 9) agregar scenarios(...) si no está (ruta relativa genérica; la preciso en convert_to_steps)
        if "scenarios(" not in code:
            code = 'from pytest_bdd import scenarios\n' + code

        return code


    def _ensure_ctx_in_params(self, params: str) -> str:
        # normaliza lista de params y agrega ctx si no existe
        parts = [x.strip() for x in params.split(",") if x.strip()]
        if "ctx" not in parts:
            parts.append("ctx")
        seen, out = set(), []
        for x in parts:
            if x not in seen:
                out.append(x); seen.add(x)
        return ", ".join(out)
