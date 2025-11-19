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
STATUS_ID_SUCCESS = int(os.getenv("STATUS_ID_SUCCESS"))  # Estado para prueba exitosa
STATUS_ID_FAILURE = int(os.getenv("STATUS_ID_FAILURE"))  # Estado para prueba fallida

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
    name = re.sub(r'[^\w\s-]', '', subject).strip().lower()
    name = re.sub(r'[-\s]+', '-', name)
    # 3. Cambia la extensión a .py y añade el prefijo pytest 'test_'
    return f"test_{name}.py"


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
        "Eres un experto en Playwright y **Python (Pytest)**. Tu única tarea es generar un código de prueba "
        "completo y ejecutable. La salida debe ser **SOLO EL CÓDIGO** en Python y no debe contener "
        "ninguna explicación o formato Markdown. "
        "Asegúrate de: "
        "1. Definir una función de prueba asíncrona (`async def`) con el decorador `@pytest.mark.asyncio`."
        "2. Incluir el fixture `page` como **argumento de la función de prueba**: `async def test_my_feature(page):`."
        "3. NO usar `async with page:` dentro del cuerpo del test, ya que es incorrecto."
    )
    user_prompt = (
        f"Genera un test de Playwright en **Python (usando Pytest)** para verificar el siguiente BUG de OpenProject. "
        f"El bug es: **{subject}**. "
        f"El test debe asumir que la aplicación se ejecuta en la URL: **{target_url}**. "
        "El test debe simular los pasos para intentar reproducir el bug y, finalmente, incluir una aserción "
        "que confirme si el bug ocurre o se ha solucionado. Recuerda solo contestar con el codigo Python necesario."
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
    

# ejecutar la prueba usando Pytest
def run_playwright_test(test_file_name):
    """Ejecuta un archivo de prueba Playwright usando pytest."""
    print(f"\n▶️ Ejecutando Pytest para: {test_file_name}")
    
    # Comando de Pytest. NO necesitamos 'npx' ni la ruta completa si pytest está en el PATH
    # El archivo debe estar en la carpeta 'tests' o la que Pytest escanee.
    command = ["pytest", "-v", os.path.join("tests", test_file_name)] 
    
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
        # ... (retorno de fallo) ...
        return {"status": "failure", "output": e.stdout + e.stderr}
        
    except FileNotFoundError:
        # Esto ocurre si 'pytest' no se encuentra en el PATH
        print(f"⚠️ Error: Pytest no se encuentra en el PATH. Asegúrate de que está instalado.")
        return {"status": "error", "output": "Pytest not found."}


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
             execution_results.append({
                 "work_package_id": wp_id,
                 "test_file_name": test_file_name,
                 "status": "generation_failed",
                 "output": "Error al generar código con Mistral."
             })
             continue
        
        # PASO 3.9: EJECUTAR LA PRUEBA GENERADA
        # 🛑 NOTA: Asegúrate de que tu run_playwright_test esté usando 'pytest' y no 'npx'
        result = run_playwright_test(test_file_name)
        
        result['work_package_id'] = wp_id
        result['test_file_name'] = test_file_name
        execution_results.append(result)

        # 🏆 PASO 4: REPORTAR A OPENPROJECT DESPUÉS DE LA EJECUCIÓN
        report_to_openproject(
            wp_id=wp_id,
            status=result['status'],
            output=result['output'],
            test_file_name=test_file_name
        )


    print("\n--- RESUMEN DE EJECUCIÓN ---")
    for result in execution_results:
        print(f"WP {result['work_package_id']} ({result['test_file_name']}): {result['status'].upper()}")
        
    return execution_results

# Coloca esta función después de 'run_playwright_test'

# Asegúrate de que STATUS_ID_SUCCESS y STATUS_ID_FAILURE estén definidos en tu configuración.

def report_to_openproject(wp_id: int, status: str, output: str, test_file_name: str):
    """
    Actualiza el Work Package en OpenProject con el resultado del test,
    adjuntando el resultado completo a la Descripción y el Estatus.
    """
    report_endpoint = f"{OPENPROJECT_URL}/api/v3/work_packages/{wp_id}"
    
    # 1. Determinar el nuevo estado y el contenido del reporte
    if status == 'success':
        new_status_id = STATUS_ID_SUCCESS
        report_summary = f"✅ **TEST AUTOMATIZADO EXITOSO**\nEl test Playwright '{test_file_name}' se ejecutó correctamente."
        # Limitamos el output del éxito para no saturar la descripción
        report_detail = f"\n\n**Output Completo:**\n```\n{output[:1000]}\n```" 
        print(f"✔️ Reportando WP {wp_id} como ÉXITO (Estado ID: {new_status_id}).")
        
    else: # 'failure' o 'error'
        new_status_id = STATUS_ID_FAILURE
        report_summary = f"❌ **TEST AUTOMATIZADO FALLIDO o ERROR**\nEl test Playwright '{test_file_name}' falló. El error reportado por Pytest fue:"
        # Incluimos el output completo (hasta 2000 caracteres) que contendrá el traceback de Python
        report_detail = f"\n\n**Detalle Completo del Fallo:**\n```\n{output[:2000]}\n```" 
        print(f"✖️ Reportando WP {wp_id} como FALLO (Estado ID: {new_status_id}).")

    
    try:
        # 2. OBTENER lockVersion y Descripción Actual
        # Es necesario obtener los datos actuales para no sobrescribir la descripción y para obtener el lockVersion.
        response_get = requests.get(report_endpoint, headers=HEADERS, auth=AUTH_OBJECT)
        response_get.raise_for_status()
        data_get = response_get.json()

        current_lock_version = data_get.get('lockVersion')
        # Extraemos la descripción actual (el campo 'raw' contiene el Markdown/texto)
        current_description_raw = data_get.get('description', {}).get('raw', '')


        # 3. CONSTRUIR NUEVA DESCRIPCIÓN (Adjuntando el reporte completo)
        separator = "\n\n---\n\n" # Separador visual para diferenciar el informe
        
        # Combinar: Descripción original + Separador + Reporte completo (resumen + detalle)
        new_description_raw = current_description_raw + separator + report_summary + report_detail
        
        
        # 4. CONSTRUIR EL PAYLOAD
        payload = {
            "_links": {
                "status": {
                    "href": f"/api/v3/statuses/{new_status_id}",
                }
            },
            "lockVersion": current_lock_version, 
            # ¡ACTUALIZACIÓN! Agregamos el campo 'description'
            "description": {
                "raw": new_description_raw
            },
            # Añadimos un comentario (para el registro de actividad)
            "comment": {
                "raw": report_summary 
            }
        }
        
        # 5. Enviar la solicitud PATCH para actualizar
        response = requests.patch(report_endpoint, headers=HEADERS, auth=AUTH_OBJECT, json=payload)
        response.raise_for_status()
        
        print(f"✨ WP {wp_id} actualizado con éxito. Nuevo estado: {status.upper()}.")
        return True

    except requests.exceptions.HTTPError as e:
        print(f"❗ ERROR al reportar WP {wp_id}. Código: {e.response.status_code}.")
        print(f"Mensaje: {e.response.text}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado al actualizar OpenProject: {e}")
        return False


if __name__ == "__main__":
    main_agent_loop()
