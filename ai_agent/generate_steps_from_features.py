import os
import argparse
import requests
from pathlib import Path

# Configuración
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
MODEL = os.getenv("OLLAMA_MODEL", "llama3")
FEATURE_DIR = Path("/bdd/tests/features")
STEPS_DIR = Path("/bdd/tests/steps")

PROMPT_TEMPLATE = """
You are an assistant that converts Gherkin .feature files into pytest-bdd step definitions.
Each scenario should be mapped to Python functions using @given, @when, @then.
Use reusable, clear function names and only valid Python code.

Feature content:
----------------
{feature_content}
----------------
Generate the step definitions below:
"""

def generate_steps(feature_path: Path):
    with feature_path.open("r", encoding="utf-8") as f:
        feature_content = f.read()

    payload = {
        "model": MODEL,
        "prompt": PROMPT_TEMPLATE.format(feature_content=feature_content),
        "stream": False,
    }

    response = requests.post(OLLAMA_URL, json=payload)
    if response.status_code != 200:
        print(f"❌ Error procesando {feature_path.name}: {response.text}")
        return

    result = response.json().get("response", "")
    output_file = STEPS_DIR / f"{feature_path.stem}_steps.py"

    with output_file.open("w", encoding="utf-8") as f:
        f.write(result.strip())

    print(f"✅ Steps generados para {feature_path.name} → {output_file.name}")


def main():
    parser = argparse.ArgumentParser(description="Generar steps de pytest-bdd desde features.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--all", action="store_true", help="Procesar todos los archivos .feature")
    group.add_argument("--app", type=str, help="Procesar solo el archivo que contenga el nombre de la app")
    args = parser.parse_args()

    STEPS_DIR.mkdir(parents=True, exist_ok=True)

    feature_files = list(FEATURE_DIR.glob("*.feature"))
    if not feature_files:
        print(f"⚠️ No se encontraron archivos .feature en {FEATURE_DIR}")
        return

    if args.all:
        print("🚀 Generando steps para TODOS los features...")
        for f in feature_files:
            generate_steps(f)

    elif args.app:
        matches = [f for f in feature_files if args.app.lower() in f.stem.lower()]
        if not matches:
            print(f"⚠️ No se encontró ningún feature con el nombre '{args.app}'")
            return
        for f in matches:
            generate_steps(f)


if __name__ == "__main__":
    main()
