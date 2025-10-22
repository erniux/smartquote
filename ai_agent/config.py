import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    ENVIRONMENT = os.getenv("ENVIRONMENT", "local")
    BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000/api/")
    USE_OLLAMA = os.getenv("USE_OLLAMA", "true").lower() == "true"
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3:latest")
    # En Docker el host es "ollama"; en local puedes exportar OLLAMA_BASE_URL distinto
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
