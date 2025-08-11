import gradio as gr
from pathlib import Path
from inference import Inference
import traceback
import time
import shutil
import uuid

# ================================
# Configurations
# ================================
TEMP_DIR = Path("static/temp")
TEMP_DIR.mkdir(parents=True, exist_ok=True)

MAX_FILE_SIZE_MB = 50  # Prevent extremely large files from blocking processing
ALLOWED_EXTENSIONS = [".wav", ".mp3"]

# ================================
# Initialize Inference Model
# ================================
inference_model = Inference({
    "enabled": True,
    "save_output": True,
    "output_directory": "denoised",
    "sample_rate": 48000  # Fixed sample rate
})

# ================================
# Helper Functions
# ================================
def cleanup_temp_files(older_than_seconds=86400):  # 1 day default
    """Delete temp files older than given time."""
    now = time.time()
    for f in TEMP_DIR.glob("*"):
        if f.is_file() and (now - f.stat().st_mtime > older_than_seconds):
            try:
                f.unlink(missing_ok=True)
            except Exception:
                pass  # Ignore if file already removed

def copy_to_temp(file_obj):
    """Copy uploaded file to a safe temp directory with a unique name."""
    ext = Path(file_obj.name).suffix.lower()
    unique_name = f"{uuid.uuid4().hex}{ext}"
    temp_path = TEMP_DIR / unique_name
    shutil.copy(file_obj.name, temp_path)
    return temp_path

def process_file(file, save_output=True):
    """Process uploaded file through ClearVoice."""
    try:
        if file is None:
            return None, None, None, "⚠️ No file uploaded."

        ext = Path(file.name).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            return None, None, None, f"❌ Unsupported file format: {ext}"

        # Check file size limit
        file_size_mb = Path(file.name).stat().st_size / (1024 * 1024)
        if file_size_mb > MAX_FILE_SIZE_MB:
            return None, None, None, f"❌ File too large: {file_size_mb:.1f} MB (max {MAX_FILE_SIZE_MB} MB)."

        # Copy file to safe temp location
        input_audio_path = copy_to_temp(file)

        # Prevent accidental deletion of active file
        cleanup_temp_files()

        # Run inference with model auto-reload check
        inference_model.ensure_model_loaded()
        inference_model.save_output = save_output
        output_files = inference_model.run([input_audio_path])

        denoised_path = output_files[0]

        if denoised_path and Path(denoised_path).exists():
            return str(input_audio_path), str(denoised_path), str(denoised_path), "✅ Processing complete!"
        else:
            # Graceful fallback
            return str(input_audio_path), str(input_audio_path), str(input_audio_path), "⚠️ Processing failed — original file returned."

    except Exception as e:
        traceback.print_exc()
        return None, None, None, f"⚠️ Error: {str(e)}"

# ================================
# Gradio Interface
# ================================
demo = gr.Interface(
    fn=process_file,
    inputs=[
        gr.File(label="Upload WAV/MP3", file_types=ALLOWED_EXTENSIONS),
        # gr.Checkbox(label="Save Output Permanently", value=True)
    ],
    outputs=[
        gr.Audio(label="Original Audio", type="filepath"),
        gr.Audio(label="Denoised Audio", type="filepath"),
        gr.File(label="Download Processed Audio"),
        gr.Textbox(label="Status")
    ],
    title="Noise Cancellation App",
    description="Upload a WAV or MP3 file and get background noise removed using ClearVoice MossFormer2_SE_48K.",
    allow_flagging="never"
)

# Enable queue for multi-user
demo.queue()

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, share=True)
