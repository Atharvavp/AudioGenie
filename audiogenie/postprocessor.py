import subprocess
from pathlib import Path

class PostProcessor:
    def __init__(self, config):
        self.enabled = config.get("enabled", False)
        self.save_output = config.get("save_output", False)
        self.output_directory = Path(config.get("output_directory", "postprocessed"))
        self.fire_eq = config.get("fire_eq", {})
        self.codec = config.get("codec", "pcm_s16le")

        if self.save_output:
            self.output_directory.mkdir(parents=True, exist_ok=True)

    def apply_fire_eq(self, input_path):

        output_path = self.output_directory / input_path.name

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        freq = self.fire_eq.get("frequency", 1000)
        gain = self.fire_eq.get("gain", -10)

        afilter = f"firequalizer=gain='if(gte(f, {freq}), {gain},0)'"

        cmd = [
            "ffmpeg",
            "-i", str(input_path),
            "-af",
            afilter,
            "-c:a", self.codec, 
            str(output_path)
        ]

        try:
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, text=True)
        except subprocess.CalledProcessError as e:
            print(f"FFmpeg failed for {input_path.name}:\n{e.stderr}")
            raise

        return output_path

    def process_all(self, files):
        if not self.enabled:
            return files

        processed_files = []
        for f in files:
            processed = self.apply_fire_eq(f)
            processed_files.append(processed)
        return processed_files
