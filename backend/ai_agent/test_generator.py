from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from ai_agent.config import Config
from ai_agent.reader import CodeReader
import logging

logging.basicConfig(level=logging.DEBUG)

class ApiTestGenerator:
    def __init__(self):
        self.config = Config()
        self.reader = CodeReader(base_dir="/app")
        self.model = ChatOllama(
            model=self.config.OLLAMA_MODEL,
            base_url=self.config.OLLAMA_BASE_URL
            )

    def generate_tests(self, output_path="/ai_agent/generated_test.py"):
        files = self.reader.read_files()
        context = "\n\n".join([f"# --- {path} ---\n{content}" for path, content in files.items()])

        prompt = ChatPromptTemplate.from_template("""
Eres un experto en pruebas automatizadas con pytest y Django REST.
A partir del siguiente código (serializers, views y models),
genera pruebas para endpoints CRUD principales.

{context}

Responde con un archivo pytest funcional.
        """)

        result = self.model.invoke(prompt.format(context=context))
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(result.content)

        print(f"✅ Tests generados en: {output_path}")
