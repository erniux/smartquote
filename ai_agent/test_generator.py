# ai_agent/test_generator.py
# para ejecución:
# docker compose exec ai_agent python ai_agent/run_agent.py --app=quotations [--source backend|frontend] [--full]

import os
import re
import time
import httpx
import ollama
from pathlib import Path
from datetime import datetime
from collections import defaultdict

from ai_agent.reader import CodeReader
from ai_agent.config import Config
from ai_agent.frontend_reader import FrontendReader


class TestGenerator:
    """
    Genera archivos .feature (Gherkin) para API (backend) o UI (frontend) usando Ollama,
    con límites de contexto y priorización para acelerar la inferencia.
    """

    # ---------- Límites para acelerar ----------
    # Prioriza pocos archivos clave + truncado por archivo + truncado total
    MAX_FILES_PER_MODULE = 6          # ej. models/serializers/views + 3 extras
    MAX_CHARS_PER_FILE   = 30_000     # ~30KB por archivo
    MAX_COMBINED_CHARS   = 80_000     # ~80KB total al prompt

    def __init__(self, fast_mode=False, app_name=None, export=False, fallback=False, source=None):
        self.config = Config()

        # Normaliza el parámetro: None / "", espacios, mayúsculas, etc.
        src = (source or "").strip().lower()
        if src not in ("backend", "frontend", ""):
            raise ValueError(f"source inválido: {source!r}. Usa 'backend', 'frontend' o None.")
        # Si no pasan source, esta instancia usa backend (run_agent crea otra para frontend)
        self.source = src or "backend"

        # Elegir reader según la fuente
        if self.source == "frontend":
            self.reader = FrontendReader(app_name=app_name)
        else:
            self.reader = CodeReader(app_name=app_name)

        print(f"📚 Source seleccionado: {self.source} | Reader: {self.reader.__class__.__name__}")

        self.fast_mode = bool(fast_mode)
        self.app_name = app_name
        self.export = export
        self.fallback = fallback
        self.start_time = datetime.now()

        # Salida de features y logs
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
    def wait_for_ollama(self, url, timeout=180):
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

            time.sleep(4)

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
        print(f"📂 Se leerán {total_files} archivos para análisis (antes de priorizar/truncar)...")

        # Agrupar archivos por carpeta (app)
        grouped_files = defaultdict(list)
        for path, content in files.items():
            folder = os.path.basename(os.path.dirname(path))  # quotations, sales, etc.
            grouped_files[folder].append((path, content))

        print(f"📦 Se agruparán {len(grouped_files)} módulos para análisis...")

        for i, (folder, file_list) in enumerate(grouped_files.items(), start=1):
            print(f"\n🧩 Procesando módulo {i}/{len(grouped_files)}: {folder}")

            # 1) priorizar archivos clave
            prioritized = self._prioritize_files(file_list, self.source)
            if len(prioritized) > self.MAX_FILES_PER_MODULE:
                print(f"⚖️  Limite de archivos por módulo: {self.MAX_FILES_PER_MODULE} (de {len(prioritized)})")
                prioritized = prioritized[: self.MAX_FILES_PER_MODULE]

            # 2) truncar contenido por archivo
            truncated_files = []
            for (p, c) in prioritized:
                tc = self._truncate_text(c, self.MAX_CHARS_PER_FILE)
                truncated_files.append((p, tc))

            # 3) unificar con etiqueta de ruta y truncado total
            combined = self._combine_with_labels(truncated_files, self.MAX_COMBINED_CHARS)
            print(f"🧾 Tamaño final del prompt: {len(combined):,} chars")

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

{combined}
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

{combined}
"""

            # Llamada al modelo (1ª)
            response = self.client.chat(
                model=self.config.OLLAMA_MODEL,
                messages=[{"role": "system", "content": system_prompt},
                          {"role": "user", "content": prompt}],
                options=self._ollama_options()
            )
            answer = response["message"]["content"]

            # 2ª vuelta pidiendo SOLO Gherkin (refuerzo)
            response = self.client.chat(
                model=self.config.OLLAMA_MODEL,
                messages=[{"role": "user", "content": f"Return ONLY valid Gherkin for the previous analysis.\n{answer}"}],
                options=self._ollama_options()
            )
            answer = response["message"]["content"]

            # Validar + sanitizar Gherkin
            if not self._is_valid_gherkin(answer):
                print("⚠️ Respuesta no válida como Gherkin. Reintentando con prompt estricto…")
                strict_msgs = self._second_chance_prompt(folder, self.source, combined)
                response = self.client.chat(model=self.config.OLLAMA_MODEL, messages=strict_msgs, options=self._ollama_options())
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

    # ----------------------------
    # 🛠️ Utilidades de recorte/priorización
    # ----------------------------
    def _prioritize_files(self, file_list, source):
        """
        Ordena primero por peso semántico:
          backend: models -> serializers -> views -> forms -> tasks -> otros
          frontend: pages -> components -> hooks -> utils -> otros
        """
        weights = []
        if source == "backend":
            order = ["models.py", "serializers.py", "views.py", "forms.py", "tasks.py"]
        else:
            # frontend
            order = ["pages", "components", "hooks", "utils"]

        def score(path: str) -> int:
            p = path.lower()
            for idx, key in enumerate(order):
                if key in p:
                    return idx
            return len(order) + 1

        # sort by score then shorter paths
        weights = sorted(file_list, key=lambda pc: (score(pc[0]), len(pc[0])))
        print("🧮 Prioridad de archivos:")
        for p, _ in weights:
            print(f"   • {p}")
        return weights

    def _truncate_text(self, text: str, max_chars: int) -> str:
        if len(text) <= max_chars:
            return text
        head = text[: max_chars // 2]
        tail = text[-(max_chars // 2) :]
        return head + "\n\n# ... [TRUNCATED] ...\n\n" + tail

    def _combine_with_labels(self, files, max_total_chars: int) -> str:
        """
        Une archivos con etiqueta de ruta y corta si supera max_total_chars.
        """
        chunks = []
        total = 0
        for path, content in files:
            label = f"# Archivo: {os.path.basename(path)}\n"
            block = label + content.strip() + "\n\n"
            if total + len(block) > max_total_chars:
                remaining = max_total_chars - total
                if remaining > 0:
                    block = block[:remaining] + "\n# [TRUNCATED PROMPT]\n"
                    chunks.append(block)
                print(f"✂️  Prompt alcanzó límite total {max_total_chars:,} chars.")
                break
            chunks.append(block)
            total += len(block)
        return "".join(chunks)

    def _ollama_options(self) -> dict:
        """
        Parámetros para acelerar Ollama. Ajusta num_thread según tu host.
        """
        if self.fast_mode:
            return {
                "num_predict": 256,
                "num_ctx": 1536,
                "num_thread": 6,
                "temperature": 0.2,
            }
        return {
            "num_predict": 512,
            "num_ctx": 2048,
            "num_thread": 6,
            "temperature": 0.2,
        }

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
