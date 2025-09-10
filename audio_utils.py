import numpy as np
import soundfile as sf
from pathlib import Path


def calculate_db_scale(percentage: int, dB_min: float = -30.0, dB_max: float = 0.0) -> float:
    """
    Convert a noise reintroduction percentage into a linear scale factor.

    Args:
        percentage (int): How much noise to add back (0–100).
        dB_min (float, optional): Minimum dB scaling at 100% noise removal.
        dB_max (float, optional): Maximum dB scaling at 0% noise removal.

    Returns:
        float: Linear amplitude scaling factor for the noise.
    """
    if percentage >= 100:
        return 0.0  # 100% reduction → no noise added back
    r = percentage / 100
    db = dB_min + (1 - r) * (dB_max - dB_min)
    return 10 ** (db / 20)


def match_length(a: np.ndarray, b: np.ndarray):
    """
    Ensure two audio signals are the same length by trimming to the shorter one.

    Args:
        a (np.ndarray): First audio array.
        b (np.ndarray): Second audio array.

    Returns:
        tuple[np.ndarray, np.ndarray]: Trimmed arrays of equal length.
    """
    min_len = min(len(a), len(b))
    return a[:min_len], b[:min_len]


def add_scaled_noise_back(input_path: Path, denoised_path: Path, percentage: int, output_path: Path) -> Path:
    """
    Reintroduce scaled noise into denoised audio.

    Args:
        input_path (Path): Path to original (noisy) audio file.
        denoised_path (Path): Path to denoised audio file.
        percentage (int): Percentage of noise to add back (0–100).
        output_path (Path): Path where the mixed audio will be saved.

    Returns:
        Path: Path to the final audio file with reintroduced noise.
    """
    # Load original and denoised audio
    input_audio, sr_input = sf.read(input_path)
    processed_audio, sr_processed = sf.read(denoised_path)

    if sr_input != sr_processed:
        raise ValueError("Sample rates do not match between input and denoised audio.")

    # Align lengths before subtraction
    input_audio, processed_audio = match_length(input_audio, processed_audio)

    # Isolate noise and scale it
    noise_only = input_audio - processed_audio
    scale = calculate_db_scale(percentage)

    # Mix noise back in, ensuring values stay in [-1, 1]
    output_audio = np.clip(processed_audio + noise_only * scale, -1.0, 1.0)

    # Save result
    sf.write(output_path, output_audio, sr_input)
    print(f"[INFO] Added back {percentage}% noise → Saved at {output_path}")

    return output_path
