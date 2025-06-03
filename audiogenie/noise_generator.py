import numpy as np
import soundfile as sf
from pathlib import Path

class NoiseGenerator:
    def __init__(self, config):
        self.enabled = config.get("enabled", False)
        self.intermediate_directory = Path(config.get("intermediate_directory", "temp"))
        self.output_directory = Path(config.get("output_directory", "noise_only"))
        self.keep_intermediates = config.get("keep_intermediates", False)

        if self.enabled:
            self.intermediate_directory.mkdir(parents=True, exist_ok=True)
            self.output_directory.mkdir(parents=True, exist_ok=True)

    def subtract_waveforms(self, original_path, denoised_path, output_path):
        orig, sr1 = sf.read(original_path)
        den, sr2 = sf.read(denoised_path)
        assert sr1 == sr2, "Sampling rates must match"

        # Convert both to mono for subtraction (recommended)
        if orig.ndim > 1:
            orig = np.mean(orig, axis=1)
        if den.ndim > 1:
            den = np.mean(den, axis=1)

        # Pad shorter array to match length of longer
        max_len = max(len(orig), len(den))
        orig = np.pad(orig, (0, max_len - len(orig)), 'constant')
        den = np.pad(den, (0, max_len - len(den)), 'constant')

        noise = orig - den
        sf.write(output_path, noise, sr1)


    def generate_noise(self, original_files, denoised_files):
        if not self.enabled:
            return []

        noise_files = []
        for orig_path, den_path in zip(original_files, denoised_files):
            output_path = self.output_directory / orig_path.name
            self.subtract_waveforms(orig_path, den_path, output_path)
            noise_files.append(output_path)

        if not self.keep_intermediates:
            # You can add code here to remove intermediate files from intermediate_directory
            pass

        return noise_files
