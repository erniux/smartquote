import os
import time
import requests
from ollama import Client
from ai_agent.reader import CodeReader
from ai_agent.config import Config

class ApiTestGenerator:
    def __init__(self):
        self.config = Config()
        self.reader = CodeReader()
        self.client = Client(host=self.config.OLLAMA_BASE_URL)
        print(f"🚀 Inicializando ApiTestGenerator con modelo={self.config.OLLAMA_MODEL}")
        print(f"🧩 Conectando cliente Ollama en {self.config.OLLAMA_BASE_URL} ...")

    def wait_for_ollama(self, base_url, timeout=180):
        """Espera hasta que Ollama responda al endpoint /api/tags."""
        try:
            timeout = float(timeout)
        except ValueError:
            timeout = 180.0

        start = time.time()
        print(f"🕓 Verificando conexión con Ollama en {base_url} ...")

        while time.time() - start < timeout:
            try:
                r = requests.get(f"{base_url}/api/tags", timeout=5)
                if r.status_code == 200:
                    print("✅ Ollama está disponible y responde correctamente.")
                    return True
                else:
                    print(f"⚠️ Ollama respondió con código {r.status_code}")
            except Exception as e:
                print(f"⏳ Esperando a que Ollama se inicie... ({type(e).__name__}: {e})")
            time.sleep(5)

        raise ConnectionError("❌ Ollama no respondió en el tiempo esperado.")

    def generate_tests(self, output_path="/ai_agent/generated_test.py"):
        """Lee los archivos relevantes del proyecto y genera pruebas automatizadas usando Ollama."""
        self.wait_for_ollama(self.config.OLLAMA_BASE_URL)

        print(f"🧠 Usando cliente directo de Ollama en {self.config.OLLAMA_BASE_URL}")
        files = self.reader.read_files()
        print(f"📂 Se leerán {len(files)} archivos para análisis...")

        prompt = """
Eres un ingeniero QA experto en Python. 
Genera pruebas automatizadas con pytest basadas en el siguiente contexto de código.

Contexto:
{context}

Regresa solo el código Python de las pruebas.
"""

        results = []
        # Detectar si files es lista o diccionario
        if isinstance(files, list):
            files = {f"archivo_{i+1}.py": content for i, content in enumerate(files)}

        for i, (path, content) in enumerate(files.items(), start=1):

            print(f"🧩 Procesando bloque {i}/{len(files)} ({len(content)} chars)")
            try:
                response = self.client.generate(
                    model=self.config.OLLAMA_MODEL,
                    prompt=prompt.format(context=content),
                    stream=False
                )
                result = response.get("response", "").strip()
                if result:
                    print(f"✅ Bloque {i} procesado correctamente.")
                    results.append(f"# Archivo: {path}\n{result}")
                else:
                    print(f"⚠️ Bloque {i} no devolvió contenido.")
            except Exception as e:
                print(f"⚠️ Error procesando bloque {i}: {e}")

        if not results:
            print("⚠️ No se generaron resultados. Revisa la configuración o el modelo.")
            return

        # Guardar las pruebas generadas
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n\n".join(results))

        print(f"✅ Tests generados en: {output_path}")
        print("🎉 Proceso completado correctamente.")
