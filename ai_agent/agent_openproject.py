import requests
import json
import urllib.parse
import subprocess
import re # Para limpiar el string
import ollama
import os
from dotenv import load_dotenv

load_dotenv()

OPENPROJECT_URL = os.getenv("OPENPROJECT_URL")
API_KEY = os.getenv("OPENPROJECT_API_KEY")

PROJECT_ID = 2         # Confirmado: ID del proyecto de destino
TYPE_ID_BUG = 7        # Confirmado: ID del tipo de tarea "Bug"

# VALOR QUE DEBES ENCONTRAR Y REEMPLAZAR EN TU INSTANCIA DE OPENPROJECT:
TARGET_STATUS_ID = 4   # <<-- ID del estado "Listo para automatizar" (EJ: 4)
# -------------------------------------------------------------------

AUTH_OBJECT = requests.auth.HTTPBasicAuth('apikey', API_KEY)
HEADERS = {"Content-Type": "application/json"}

### Generar las pruebas Playwright desde OpenProject ###
# Cliente Ollama
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")
OLLAMA_URL = "http://ollama:11434"
ollama.api_base_url = OLLAMA_URL
ollama_client = ollama.Client(host=OLLAMA_URL)
TESTS_DIR = 'tests'


# --- NUEVA FUNCIÓN DE LIMPIEZA DE ASUNTO ---
def sanitize_subject_to_filename(subject: str) -> str:
    """Convierte un asunto de OpenProject en un nombre de archivo Playwright seguro."""
    # 1. Reemplaza cualquier cosa que no sea letra, número o espacio por un guion.
    name = re.sub(r'[^\w\s-]', '', subject).strip().lower()
    # 2. Reemplaza espacios y guiones múltiples por un solo guion.
    name = re.sub(r'[-\s]+', '-', name)
    # 3. Añade la extensión típica de Playwright
    return f"{name}.spec.ts"


def get_api_endpoint():
    """Construye el endpoint con todos los filtros necesarios (Proyecto, Tipo, Estado)."""
    FILTERS = [
        {"project": {"operator": "=", "values": [str(PROJECT_ID)]}},
        {"type": {"operator": "=", "values": [str(TYPE_ID_BUG)]}},
        {"status": {"operator": "=", "values": [str(TARGET_STATUS_ID)]}},
    ]
    filters_json_string = urllib.parse.quote(json.dumps(FILTERS))
    
    return (
        f"{OPENPROJECT_URL}/api/v3/work_packages"
        f"?filters={filters_json_string}"
        f"&sortBy=[[\"id\",\"asc\"]]"
    )


def fetch_work_packages_for_automation():
    """Conecta a OpenProject, aplica filtros y USA el Asunto como ID del test."""
    API_ENDPOINT = get_api_endpoint()
    print(f"Buscando Bugs en Proyecto ID {PROJECT_ID}, Tipo ID {TYPE_ID_BUG}, y Estado ID {TARGET_STATUS_ID}...")
    
    try:
        response = requests.get(API_ENDPOINT, headers=HEADERS, auth=AUTH_OBJECT) 
        response.raise_for_status()
        data = response.json()
        
        test_files_to_run = []
        for wp in data.get('_embedded', {}).get('elements', []):
            subject = wp.get('subject')
            
            if subject:
                # 1. Sanitizar el asunto para crear el nombre del archivo de prueba
                test_file_name = sanitize_subject_to_filename(subject)
                
                test_files_to_run.append({
                    "work_package_id": wp.get('id'),
                    "subject": subject,
                    "test_file_name": test_file_name # Usamos el nombre sanitizado
                })
        
        print(f"✅ Se encontraron {len(test_files_to_run)} tests listos para ejecutar.")
        return test_files_to_run

    except Exception as e:
        print(f"\n❌ Ocurrió un error en el filtro o extracción: {e}")
        return []



def generate_playwright_test(wp_id: int, subject: str, test_file_name: str, target_url: str = "http://localhost:5173"):
    """
    Usa Ollama y Mistral para generar un test de Playwright basado en el Asunto.
    """
    
    # Asegurarse de que la carpeta 'tests' existe
    if not os.path.exists(TESTS_DIR):
        os.makedirs(TESTS_DIR)
        print(f"Directorio '{TESTS_DIR}' creado.")

    file_path = os.path.join(TESTS_DIR, test_file_name)
    
    # Si el archivo ya existe, lo saltamos para evitar sobreescribir el trabajo manual.
    if os.path.exists(file_path):
        print(f"⚠️ El archivo de prueba ya existe: {file_path}. Saltando la generación.")
        return True # Asumimos éxito para la ejecución
    
    # 1. Ingeniería del Prompt para Mistral
    # El prompt debe ser muy específico en el formato de salida que esperamos (solo código).
    system_prompt = (
        "Eres un experto en Playwright y python. Tu única tarea es generar un código de prueba "
        "completo y ejecutable de Playwright. La salida debe ser **SOLO EL CÓDIGO** y no debe contener "
        "ninguna explicación, introducción o texto de formato Markdown (```python). "
        "Asegúrate de usar la función `test()` y la página de navegación `page`."
    )
    user_prompt = (
        f"Genera un test de Playwright en python para verificar el siguiente BUG de OpenProject. "
        f"El bug es: **{subject}**. "
        f"El test debe asumir que la aplicación se ejecuta en la URL: **{target_url}**. "
        "El test debe simular los pasos para intentar reproducir el bug y, finalmente, incluir una aserción "
        "que confirme si el bug ocurre o se ha solucionado."
    )

    print(f"🤖 Llamando a Mistral para generar el test para el WP {wp_id}...")

    try:
        # 2. Llamada a la API de Ollama (asumiendo que Ollama está corriendo localmente)
        response = ollama_client.chat(
            model=OLLAMA_MODEL,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt},
            ]
        )
        
        generated_code = response['message']['content'].strip()
        
        # 3. Limpieza y Guardado del Código
        # Algunos modelos aún incluyen bloques de código, así que los limpiamos.
        if generated_code.startswith('```'):
            generated_code = generated_code.split('\n', 1)[-1]
        if generated_code.endswith('```'):
            generated_code = generated_code.rsplit('\n', 1)[0]
            
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(generated_code)
        
        print(f"✅ Código de prueba generado y guardado en: {file_path}")
        return True

    except Exception as e:
        print(f"❌ Error al conectar o generar código con Ollama: {e}")
        # Retorna False para que el bucle principal sepa que no puede ejecutar la prueba
        return False
    

# La función run_playwright_test NO necesita cambios, ya que usa el 'test_file_name'
def run_playwright_test(test_file_name):
    """Ejecuta un archivo de prueba Playwright."""
    print(f"\n▶️ Ejecutando Playwright para: {test_file_name}")
    # Comando de Playwright
    command = ["npx", "playwright", "test", f"tests/{test_file_name}", "--reporter=list"]
    
    try:
        result = subprocess.run(
            command, 
            capture_output=True, 
            text=True, 
            check=True
        )
        print(f"✅ Ejecución exitosa de {test_file_name}.")
        return {"status": "success", "output": result.stdout}

    except subprocess.CalledProcessError as e:
        print(f"❌ La prueba {test_file_name} falló.")
        return {"status": "failure", "output": e.stdout + e.stderr}
        
    except FileNotFoundError:
        print(f"⚠️ Error: Playwright o npx no se encuentran en el PATH.")
        return {"status": "error", "output": "Playwright/npx not found."}


# ... (Funciones fetch_work_packages_for_automation y run_playwright_test se mantienen) ...

def main_agent_loop():
    """Bucle principal que coordina la lectura, generación, ejecución y reporte."""
    
    # 1. OBTENER TAREAS FILTRADAS
    tests_to_run = fetch_work_packages_for_automation()
    
    # 2. EJECUTAR PRUEBAS Y CAPTURAR RESULTADOS
    execution_results = []
    
    for test in tests_to_run:
        wp_id = test['work_package_id']
        subject = test['subject']
        test_file_name = test['test_file_name']
        
        print(f"\n--- Procesando Tarea {wp_id} | Asunto: {subject} ---")

        # PASO 3.5: GENERAR EL CÓDIGO DEL TEST
        if not generate_playwright_test(wp_id, subject, test_file_name):
             # Si falla la generación (Ollama caído, etc.), registramos el error y saltamos.
             execution_results.append({
                 "work_package_id": wp_id,
                 "test_file_name": test_file_name,
                 "status": "generation_failed",
                 "output": "Error al generar código con Mistral."
             })
             continue
        
        # PASO 3.9: EJECUTAR LA PRUEBA GENERADA
        result = run_playwright_test(test_file_name)
        
        result['work_package_id'] = wp_id
        result['test_file_name'] = test_file_name
        execution_results.append(result)

    print("\n--- RESUMEN DE EJECUCIÓN ---")
    # ... (El resumen de ejecución se mantiene) ...
        
    return execution_results


if __name__ == "__main__":
    # Asegúrate de que Ollama esté corriendo y el modelo 'mistral' esté descargado
    # Puedes usar: 'ollama run mistral' para descargarlo
    main_agent_loop()
