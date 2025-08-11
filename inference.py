from clearvoice import ClearVoice
from pathlib import Path
import traceback

class Inference:
    def __init__(self, config):
        # Configurable parameters
        self.enabled = config.get("enabled", False)
        self.save_output = config.get("save_output", False)
        self.output_directory = Path(config.get("output_directory", "denoised"))
        self.model_path = config.get("clearvoice_model_path", None)  # Optional custom path
        self.sample_rate = config.get("sample_rate", 16000)
        self.task = config.get("task", "speech_enhancement")
        self.model_name = config.get("model_name", "MossFormer2_SE_48K")
        self.verbose = config.get("verbose", False)

        # Ensure output directory exists if saving
        if self.save_output:
            self.output_directory.mkdir(parents=True, exist_ok=True)

        self.cv = None
        if self.enabled:
            self._load_model()

    def _load_model(self):
        """Load ClearVoice model."""
        if self.verbose:
            print(f"[Inference] Loading ClearVoice model: {self.model_name}")
        self.cv = ClearVoice(task=self.task, model_names=[self.model_name])

    def ensure_model_loaded(self):
        """Reload the model if it's missing or was unloaded due to an error."""
        if self.cv is None:
            if self.verbose:
                print("[Inference] Model was not loaded — reloading.")
            self._load_model()

    def run(self, files, save_output_override=None):
        """
        Run noise suppression on provided files.
        :param files: List of file paths (Path objects or strings)
        :param save_output_override: Optional bool to override self.save_output for this run
        :return: List of output file paths
        """
        if not self.enabled:
            if self.verbose:
                print("[Inference] Inference disabled — returning original files")
            return files

        output_files = []
        save_output_flag = self.save_output if save_output_override is None else save_output_override

        for file in files:
            try:
                file_path = Path(file)
                if not file_path.exists():
                    raise FileNotFoundError(f"Input file not found: {file_path}")

                if save_output_flag:
                    output_path = self.output_directory
                else:
                    output_path = Path("static/temp")
                    output_path.mkdir(parents=True, exist_ok=True)

                if self.verbose:
                    print(f"[Inference] Processing file: {file_path} -> {output_path}")

                # Run ClearVoice
                self.cv(
                    input_path=str(file_path),
                    online_write=True,
                    output_path=str(output_path)
                )

                # Dynamically locate the output file
                possible_outputs = list(output_path.rglob(file_path.name))
                if possible_outputs:
                    output_files.append(possible_outputs[0])
                else:
                    raise FileNotFoundError(f"No output file generated for {file_path}")

            except Exception as e:
                print(f"[Inference] Error processing {file}: {e}")
                traceback.print_exc()
                output_files.append(None)

        return output_files
