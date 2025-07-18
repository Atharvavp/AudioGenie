from pathlib import Path

class InputResolver:
    def __init__(self, input_config):
        self.mode = input_config["mode"]
        self.paths = input_config["paths"]

    def resolve(self):
        files = []
        if self.mode == "file":
            files = [Path(p) for p in self.paths]
        elif self.mode == "directory":
            for directory in self.paths:
                p = Path(directory)
                files.extend(list(p.rglob("*.wav")))
                files.extend(list(p.rglob("*.mp3")))
        return files
