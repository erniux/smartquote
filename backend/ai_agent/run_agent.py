import sys
import os
sys.path.append("/ai_agent")
from ai_agent.test_generator import ApiTestGenerator

if __name__ == "__main__":
    # Desactivar conexión con LangSmith (modo local)
    os.environ["LANGCHAIN_TRACING_V2"] = "false"
    os.environ["LANGCHAIN_PROJECT"] = "local-agent"
    os.environ["LANGCHAIN_API_KEY"] = ""
    os.environ["LANGCHAIN_ENDPOINT"] = ""
    os.environ["LANGCHAIN_DEBUG"] = "true"
    os.environ["LANGCHAIN_VERBOSE"] = "true"


    print("🧠 Iniciando el agente con modo debug...\n")
    generator = ApiTestGenerator()
    generator.generate_tests()

    print("\n✅ Proceso completado.")