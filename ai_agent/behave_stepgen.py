#!/usr/bin/env python3
import os
import re
import subprocess
from pathlib import Path

FEATURES_ROOT = Path("/app/bdd/tests/features")
STEPS_ROOT    = Path("/app/bdd/tests/steps")

HEADER = """# -*- coding: utf-8 -*-
# Auto-generated from behave --dry-run snippets
from behave import given, when, then
"""

SNIPPET_START_RE = re.compile(r"^You can implement step definitions", re.I)
DECORATOR_RE = re.compile(r"^@(given|when|then)\b", re.I)

def run_behave_snippets(feature_path: Path) -> str:
    """
    Ejecuta behave en modo --dry-run sobre un .feature y devuelve la salida completa (stdout).
    Behave imprimirá al final los 'snippets' para pasos indefinidos.
    """
    # Importante: correr Behave con cwd en carpeta base para que resuelva paths bien.
    cmd = ["behave", "--dry-run", str(feature_path)]
    res = subprocess.run(cmd, cwd=str(FEATURES_ROOT.parent), capture_output=True, text=True)
    return res.stdout + "\n" + res.stderr

def extract_snippets(full_output: str) -> str:
    """
    Extrae SOLO los bloques de snippets (decoradores @given/@when/@then + funciones).
    """
    lines = full_output.splitlines()
    snippets = []
    collecting = False
    for line in lines:
        if SNIPPET_START_RE.search(line):
            collecting = True
            continue
        if collecting:
            if DECORATOR_RE.search(line) or line.strip().startswith("def "):
                snippets.append(line)
            # mantiene indentación y líneas en blanco de los bloques
            elif snippets and (line.startswith("    ") or not line.strip()):
                snippets.append(line)
            else:
                # termina al cortar con otra sección/summary
                pass
    # Limpieza final
    block = "\n".join(snippets).strip()
    return block

def ensure_header(code: str) -> str:
    code = code.strip()
    if not code:
        return HEADER + "\n# (No undefined steps. Everything already implemented.)\n"
    # Quitar fences o basura accidental
    code = re.sub(r"```[a-zA-Z]*", "", code).strip()
    # Asegurar 'pass' si alguna función vino vacía
    code = re.sub(r"(def [\w_]+\([^\)]*\):)\s*$", r"\1\n    pass", code, flags=re.M)
    return HEADER + "\n" + code + "\n"

def output_path_for(feature_path: Path) -> Path:
    """
    Devuelve la ruta destino del .py de steps para un .feature dado,
    respetando /api o /ui y reutilizando el nombre base.
    """
    rel = feature_path.relative_to(FEATURES_ROOT)
    # rel: <app>/<tipo>/<archivo>.feature
    app = rel.parts[0]
    tipo = rel.parts[1] if len(rel.parts) > 1 else "api"  # por si acaso
    base = rel.stem + "_steps.py"
    out_dir = STEPS_ROOT / app / tipo
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir / base

def main(app_prefix: str = ""):
    """
    Recorre TODOS los .feature (o filtrados por prefijo de app en la ruta) y genera
    archivos de steps basados en los snippets que imprime Behave.
    """
    features = list(FEATURES_ROOT.rglob("*.feature"))
    if app_prefix:
        features = [f for f in features if app_prefix in str(f)]
    if not features:
        print(f"⚠️ No se encontraron .feature bajo {FEATURES_ROOT} con prefijo '{app_prefix}'.")
        return

    print(f"🔍 Encontrados {len(features)} .feature. Generando snippets...")
    for fpath in features:
        print(f"🧩 {fpath}")
        out = run_behave_snippets(fpath)
        snippets = extract_snippets(out)
        code = ensure_header(snippets)
        dest = output_path_for(fpath)
        dest.write_text(code, encoding="utf-8")
        print(f"✅ Steps -> {dest}")

    print("🎉 Listo. Si vuelves a correr el script, se actualizarán los archivos.")

if __name__ == "__main__":
    import sys
    prefix = sys.argv[1] if len(sys.argv) > 1 else ""
    main(prefix)
