import os
import re
from datetime import datetime
from ai_agent.config import Config
from ai_agent.reader import CodeReader


class FeatureGenerator:
    """Convierte pruebas Python en archivos .feature (BDD / Gherkin)."""

    def __init__(self, app_name=None):
        self.config = Config()
        self.reader = CodeReader(app_name=app_name)
        self.app_name = app_name
        self.tests_dir = "/app/outputs/tests"
        self.features_dir = "/app/outputs/features"
        os.makedirs(self.features_dir, exist_ok=True)

    # ----------------------------
    # 📘 Método principal
    # ----------------------------
    def generate_feature_files(self):
        """Convierte los tests generados en features BDD."""
        test_file_path = os.path.join(self.tests_dir, "generated_test.py")

        if not os.path.exists(test_file_path):
            print(f"⚠️ No se encontró {test_file_path}. Ejecuta el generador de tests primero.")
            return

        print(f"📘 Leyendo archivo de tests: {test_file_path}")
        with open(test_file_path, "r", encoding="utf-8") as f:
            test_content = f.read()

        # Buscar todas las funciones test_*
        test_functions = re.findall(r"def (test_[\w_]+)\((.*?)\):([\s\S]*?)(?=\ndef|\Z)", test_content)

        if not test_functions:
            print("⚠️ No se encontraron funciones de prueba en el archivo.")
            return

        feature_output_path = os.path.join(self.features_dir, "generated_feature.feature")
        print(f"🧩 Generando archivo .feature en: {feature_output_path}")

        feature_content = self._convert_to_gherkin(test_functions)

        with open(feature_output_path, "w", encoding="utf-8") as f:
            f.write(feature_content)

        print(f"✅ Archivo .feature generado correctamente en {feature_output_path}")
        self.update_readme(feature_output_path)

    # ----------------------------
    # 🧠 Conversión a Gherkin
    # ----------------------------
    def _convert_to_gherkin(self, test_functions):
        """Convierte funciones de prueba en texto BDD Gherkin."""
        lines = [
            "Feature: Automated tests generated from AI Agent",
            "",
            "  # Archivo generado automáticamente a partir de tests Python",
        ]

        for func_name, params, body in test_functions:
            scenario_name = func_name.replace("_", " ").capitalize()
            lines.append(f"\n  Scenario: {scenario_name}")

            # Detectar pasos básicos
            if "get(" in body:
                lines.append("    Given the API endpoint is available")
                lines.append("    When I send a GET request")
                lines.append("    Then I should receive a 200 OK response")

            elif "post(" in body:
                lines.append("    Given a valid payload")
                lines.append("    When I send a POST request")
                if "201" in body:
                    lines.append("    Then I should receive a 201 Created response")
                else:
                    lines.append("    Then I should receive a successful response")

            elif "put(" in body or "patch(" in body:
                lines.append("    Given an existing resource")
                lines.append("    When I send an update request")
                lines.append("    Then the resource should be updated")

            elif "delete(" in body:
                lines.append("    Given an existing resource")
                lines.append("    When I send a DELETE request")
                lines.append("    Then the resource should be removed")

            else:
                lines.append("    Given the system is ready")
                lines.append("    When I execute the test logic")
                lines.append("    Then I should get the expected result")

        return "\n".join(lines)

    # ----------------------------
    # 🪶 Actualiza el README del agente
    # ----------------------------
    def update_readme(self, feature_path):
        """Actualiza el README.md con información sobre la última generación."""
        readme_path = os.path.join(
            os.getenv("PROJECT_BASE_PATH", "/workspace"), "ai_agent", "README.md"
        )
        os.makedirs(os.path.dirname(readme_path), exist_ok=True)

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        info = f"""
### 🧾 Última generación de features
- 📅 Fecha: `{timestamp}`
- 📄 Archivo generado: `{feature_path}`
- 🧩 Fuente: `/app/outputs/tests/generated_test.py`
"""

        if os.path.exists(readme_path):
            with open(readme_path, "a", encoding="utf-8") as f:
                f.write("\n" + info)
        else:
            with open(readme_path, "w", encoding="utf-8") as f:
                f.write("# 🤖 AI Agent Feature Generator\n" + info)

        print(f"🪶 README.md actualizado con la información de la última generación de features.")
