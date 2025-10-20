import os

class CodeReader:
    def __init__(self, base_dir="/app"):
        self.base_dir = base_dir

    def read_files(self):
        context = {}
        for root, _, files in os.walk(self.base_dir):
            if "quotations" not in root:
                continue
            for f in files:
                if f.endswith(".py") and any(k in f for k in ["serializer", "view", "model"]):
                    path = os.path.join(root, f)
                    with open(path, "r", encoding="utf-8") as file:
                        context[path] = file.read()
        return context
