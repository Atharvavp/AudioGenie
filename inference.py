from clearvoice import ClearVoice
from pathlib import Path
import traceback
import numpy as np
import soundfile as sf
import os

# -------------------------------------------------------------------------
# Audio utility for reintroducing scaled noise
# -------------------------------------------------------------------------
def add_scaled_noise_back(input_path, denoised_path, percentage, output_path):
    """Add scaled noise back to denoised audio."""

    def calculate_db_scale(percentage, dB_min=-30.0, dB_max=0.0):
        """Convert noise percentage to linear amplitude scale."""
        if percentage == 100:
            return 0.0
        r = percentage / 100
        r_inv = 1 - r
        db = dB_min + r_inv * (dB_max - dB_min)
        scale = 10 ** (db / 20)
        return scale

    def match_length(a, b):
        """Trim two signals to the same length."""
        min_len = min(len(a), len(b))
        return a[:min_len], b[:min_len]

    # Load input and denoised audio
    input_audio, sr_input = sf.read(input_path)
    processed_audio, sr_processed = sf.read(denoised_path)

    if sr_input != sr_processed:
        raise ValueError("Sample rates do not match between input and processed audio.")

    # Ensure same length
    input_audio, processed_audio = match_length(input_audio, processed_audio)

    # Compute noise-only component
    noise_only = input_audio - processed_audio

    # Scale and add noise back
    scale = calculate_db_scale(percentage)
    scaled_noise = noise_only * scale
    output_audio = processed_audio + scaled_noise

    # Clip to valid range
    output_audio = np.clip(output_audio, -1.0, 1.0)

    # Save final output
    sf.write(output_path, output_audio, sr_input)
    return output_path


# -------------------------------------------------------------------------
# Inference class for ClearVoice speech enhancement
# -------------------------------------------------------------------------
class Inference:
    def __init__(self, config):
        """
        Initialize inference with configurable parameters.
        :param config: dict with keys like enabled, save_output, output_directory, model_name, etc.
        """
        self.enabled = config.get("enabled", False)
        self.save_output = config.get("save_output", False)
        self.output_directory = Path(config.get("output_directory", "denoised"))
        self.model_path = config.get("clearvoice_model_path", None)  # Optional custom path
        self.sample_rate = config.get("sample_rate", 16000)
        self.task = config.get("task", "speech_enhancement")
        self.model_name = config.get("model_name", "MossFormer2_SE_48K")
        self.verbose = config.get("verbose", False)

        # Ensure output directory exists if saving files
        if self.save_output:
            self.output_directory.mkdir(parents=True, exist_ok=True)
            if self.verbose:
                print(f"[Inference] Output directory ready: {self.output_directory}")

        self.cv = None
        if self.enabled:
            self._load_model()

    def _load_model(self):
        """Load ClearVoice model into memory."""
        if self.verbose:
            print(f"[Inference] Loading ClearVoice model: {self.model_name}")
        self.cv = ClearVoice(task=self.task, model_names=[self.model_name])

    def ensure_model_loaded(self):
        """Reload the model if it's missing or was unloaded due to an error."""
        if self.cv is None:
            if self.verbose:
                print("[Inference] Model was not loaded — reloading.")
            self._load_model()

    def run(self, files, save_output_override=None, noise_reduction_percentage=100):
        """
        Run noise suppression on provided files.
        Optionally reintroduce scaled noise depending on noise_reduction_percentage.
        :param files: List of file paths (Path objects or strings)
        :param save_output_override: Optional bool to override self.save_output for this run
        :param noise_reduction_percentage: 0–100 (100 = fully denoised, lower = more noise kept)
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

                # Determine where to save output
                if save_output_flag:
                    output_path = self.output_directory
                else:
                    output_path = Path("static/temp")
                    output_path.mkdir(parents=True, exist_ok=True)

                if self.verbose:
                    print(f"[Inference] Processing file: {file_path} -> {output_path}")

                # Run ClearVoice inference
                self.cv(
                    input_path=str(file_path),
                    online_write=True,
                    output_path=str(output_path)
                )

                # Locate denoised output
                possible_outputs = list(output_path.rglob(file_path.name))
                if not possible_outputs:
                    raise FileNotFoundError(f"No output file generated for {file_path}")
                denoised_file = possible_outputs[0]

                # If user wants partial denoising, add scaled noise back
                if noise_reduction_percentage < 100:
                    final_output = output_path / f"{file_path.stem}_final{file_path.suffix}"
                    add_scaled_noise_back(
                        input_path=file_path,
                        denoised_path=denoised_file,
                        percentage=noise_reduction_percentage,
                        output_path=final_output
                    )
                    output_files.append(final_output)
                else:
                    output_files.append(denoised_file)

            except Exception as e:
                print(f"[Inference] Error processing {file}: {e}")
                traceback.print_exc()
                output_files.append(None)

        return output_files
