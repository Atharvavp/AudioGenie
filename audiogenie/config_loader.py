import json
from pathlib import Path

class ConfigLoader:
    def __init__(self, config_path):
        self.config_path = Path(config_path)
        self.config = None

    def load(self):
        with open(self.config_path) as f:
            self.config = json.load(f)
        return self.config
