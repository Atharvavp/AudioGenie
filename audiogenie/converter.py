import subprocess
from pathlib import Path

class Converter:
    def __init__(self, config):
        self.enabled = config.get("enabled", False)
        self.save_converted = config.get("save_converted", False)
        self.output_directory = Path(config.get("output_directory", "converted"))
        self.output_format = config.get("output_format", "wav")
        self.codec = config.get("codec", "pcm_s32le")
        self.settings = config.get("settings", {})
        self.settings_enabled = self.settings.get("enable", False)
        self.sample_rate = self.settings.get("sample_rate", 16000) # check via ffprobe
        self.channels = self.settings.get("channels", 1) # check via ffprobe

        if self.save_converted:
            self.output_directory.mkdir(parents=True, exist_ok=True)

    def convert_file(self, input_path):
        input_path = Path(input_path)
        if not self.enabled:
            return input_path  # return original if conversion disabled

        output_path = self.output_directory / (input_path.stem + "." + self.output_format)
        if self.settings_enabled:
            cmd = [
                "ffmpeg",
                "-y",  # overwrite
                "-i", str(input_path),
                "-ar", str(self.sample_rate),
                "-ac", str(self.channels),
                "-c:a", self.codec,
                str(output_path)
            ]
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        else: 
            cmd = [
                "ffmpeg",
                "-y",  # overwrite
                "-i", str(input_path),
                "-c:a", self.codec,
                str(output_path)
            ]
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

        if self.save_converted:
            return output_path
        else:
            return output_path  # maybe return path anyway? or input_path if no save

    def convert_all(self, files):
        converted_files = []
        for f in files:
            converted = self.convert_file(f)
            converted_files.append(converted)
        return converted_files
