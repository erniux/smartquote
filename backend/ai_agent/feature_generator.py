# feature_generator.py
import os
from datetime import datetime
from reader import CodeReader
from test_generator import TestGenerator

class FeatureGenerator:
    def __init__(self, source_path="src", output_dir="features"):
        self.source_path = source_path
        self.output_dir = output_dir
        self.reader = CodeReader(source_path)
        self.generator = TestGenerator()

        os.makedirs(output_dir, exist_ok=True)

    def generate_feature_files(self):
        """Lee el código y genera archivos .feature automáticamente"""
        code_summary = self.reader.read_codebase()
        test_cases = self.generator.generate_tests(code_summary)

        for i, case in enumerate(test_cases, start=1):
            title = case.get("title", f"Scenario {i}")
            description = case.get("description", "")
            steps = case.get("steps", [])

            content = self._to_gherkin(title, description, steps)
            filename = os.path.join(self.output_dir, f"test_{i:03}.feature")

            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)

        print(f"✅ {len(test_cases)} archivos .feature generados en {self.output_dir}")

    def _to_gherkin(self, title, description, steps):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        lines = [
            f"# Auto-generado por AI Agent ({now})",
            f"Feature: {title}",
            "",
            f"  {description}",
            "",
            f"  Scenario: {title}",
        ]

        for s in steps:
            if s.lower().startswith("given"):
                lines.append(f"    Given {s[6:].strip()}")
            elif s.lower().startswith("when"):
                lines.append(f"    When {s[5:].strip()}")
            elif s.lower().startswith("then"):
                lines.append(f"    Then {s[5:].strip()}")
            else:
                lines.append(f"    And {s}")

        return "\n".join(lines)
