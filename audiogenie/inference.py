from clearvoice import ClearVoice
from pathlib import Path

class Inference:
    def __init__(self, config):
        self.enabled = config.get("enabled", False)
        self.save_output = config.get("save_output", False)
        self.output_directory = Path(config.get("output_directory", "denoised"))
        self.model_path = config.get("clearvoice_model_path", None)
        self.sample_rate = config.get("sample_rate", 16000)

        if self.save_output:
            self.output_directory.mkdir(parents=True, exist_ok=True)
            print(f"Inside Inference class: {self.output_directory}")

        self.cv = None
        if self.enabled:
            # Using model_names list with model_path if needed
            # For simplicity, let's assume model_path is not needed here (default to MossFormer2_SE_48K)
            # You can expand this to load onnx if required.
            self.cv = ClearVoice(task='speech_enhancement', model_names=['MossFormer2_SE_48K'])

    def run(self, files):
        if not self.enabled:
            return files  # no inference, pass files unchanged

        output_files = []
        for file in files:
            if self.save_output:
                # online_write=True saves directly to file
                self.cv(input_path=str(file), online_write=True, output_path=str(self.output_directory))
                # The output filename is same as input but in output_directory
                output_files.append(self.output_directory / "MossFormer2_SE_48K" / file.name)
            else:
                # If not saving output, just process and ignore
                self.cv(input_path=str(file))
                output_files.append(file)  # or None?
            print(f"Inside Inference class output: {output_files}")
        return output_files
