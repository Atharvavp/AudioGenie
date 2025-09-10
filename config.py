from pathlib import Path

# -----------------------------------------------------------------------------
# Global configuration values for the Noise Cleaner app
# -----------------------------------------------------------------------------

# Temporary directory for intermediate files
TEMP_DIR = Path("static/temp")
TEMP_DIR.mkdir(parents=True, exist_ok=True)

# File handling
MAX_FILE_SIZE_MB = 2048  # Maximum upload size (MB)
AUDIO_EXTS = [".wav", ".mp3"]  # Supported audio formats
VIDEO_EXTS = [".mp4", ".mov", ".mkv", ".m4v"]  # Supported video formats
ALLOWED_EXTENSIONS = AUDIO_EXTS + VIDEO_EXTS  # All accepted extensions

# Audio processing defaults
DEFAULT_SAMPLE_RATE = 48000  # Default audio sample rate for processing
MODEL_NAME = "MossFormer2_SE_48K"  # Default ClearVoice model to load
