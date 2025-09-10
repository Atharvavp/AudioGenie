import gradio as gr
from pathlib import Path
import traceback, shutil

from config import AUDIO_EXTS, VIDEO_EXTS, ALLOWED_EXTENSIONS, MAX_FILE_SIZE_MB, TEMP_DIR
from utils.file_utils import copy_to_temp, sanitize_stem, build_deduped_path
from utils.ffmpeg_utils import extract_audio_from_video, mux_clean_audio_back
from utils.housekeeping import cleanup_temp_files

# -------------------------------------------------------------------------
# Main file processing function for Gradio interface
# -------------------------------------------------------------------------
def process_file(file, noise_reduction_percentage, inference_model, save_output=True):
    """
    Process an uploaded audio or video file.
    Handles validation, temporary staging, and delegates to audio/video processors.
    :param file: uploaded file object (from Gradio)
    :param noise_reduction_percentage: int, 0–100
    :param inference_model: Inference object
    :param save_output: bool, whether to save processed files
    :return: tuple of Gradio component updates
    """
    try:
        # Validate upload
        if file is None:
            msg = "⚠️ No file uploaded."
            return _gradio_error(msg)

        src_path = Path(file.name if hasattr(file, "name") else file)
        ext = src_path.suffix.lower()

        if ext not in ALLOWED_EXTENSIONS:
            msg = f"❌ Unsupported format: {ext}"
            return _gradio_error(msg)

        if src_path.stat().st_size / (1024*1024) > MAX_FILE_SIZE_MB:
            msg = f"❌ File too large."
            return _gradio_error(msg)

        # Stage file in temporary directory
        staged_input_path, original_name = copy_to_temp(file, TEMP_DIR)

        # Cleanup old temp files
        cleanup_temp_files(TEMP_DIR)

        # Ensure model is loaded
        inference_model.ensure_model_loaded()
        inference_model.save_output = save_output

        # Determine type of file
        is_audio, is_video = ext in AUDIO_EXTS, ext in VIDEO_EXTS

        # Delegate to appropriate processor
        if is_audio:
            return _process_audio(staged_input_path, original_name, inference_model, noise_reduction_percentage)
        else:
            return _process_video(staged_input_path, original_name, inference_model, noise_reduction_percentage)

    except Exception as e:
        traceback.print_exc()
        msg = f"⚠️ Error: {str(e)}"
        return _gradio_error(msg)


# -------------------------------------------------------------------------
# Audio processing
# -------------------------------------------------------------------------
def _process_audio(staged_input_path, original_name, inference_model, noise_reduction_percentage):
    """
    Process audio files using the inference model.
    Returns Gradio component updates.
    """
    output_files = inference_model.run([staged_input_path], noise_reduction_percentage=noise_reduction_percentage) or []

    if not output_files:
        return _gradio_error("⚠️ Failed.", staged_input=staged_input_path)

    denoised_path = Path(output_files[0])

    # Build deduplicated final filename
    stem = sanitize_stem(original_name) + "_Denoised"
    final_audio = build_deduped_path(denoised_path.parent, stem, denoised_path.suffix)

    # Rename or move file
    try:
        denoised_path.rename(final_audio)
    except Exception:
        shutil.move(str(denoised_path), str(final_audio))

    return (
        gr.update(value=None, visible=False),          # Original video
        gr.update(value=str(staged_input_path), visible=True),  # Original audio
        gr.update(value=None, visible=False),          # Final video
        gr.update(value=str(final_audio), visible=True),        # Final audio
        gr.update(value=str(final_audio), visible=True),        # Download link
        gr.update(value="✅ Audio denoised.", visible=True),    # Status
    )


# -------------------------------------------------------------------------
# Video processing
# -------------------------------------------------------------------------
def _process_video(staged_input_path, original_name, inference_model, noise_reduction_percentage):
    """
    Process video files by extracting audio, denoising, and muxing back.
    Returns Gradio component updates.
    """
    # Extract audio from video
    extracted_wav = extract_audio_from_video(staged_input_path, sr=48000, temp_dir=TEMP_DIR)

    # Denoise extracted audio
    output_files = inference_model.run([extracted_wav], noise_reduction_percentage=noise_reduction_percentage) or []
    denoised_audio = Path(output_files[0])

    # Build final video filename
    out_stem = sanitize_stem(original_name) + "_Denoised"
    final_video = build_deduped_path(denoised_audio.parent, out_stem, Path(original_name).suffix)
    final_audio = build_deduped_path(denoised_audio.parent, out_stem, denoised_audio.suffix)
    shutil.copy2(str(denoised_audio), str(final_audio))
    
    # Mux cleaned audio back into original video
    mux_clean_audio_back(staged_input_path, denoised_audio, final_video)

    return (
        gr.update(value=str(staged_input_path), visible=True),  # Original video
        gr.update(value=None, visible=False),                  # Original audio
        gr.update(value=str(final_video), visible=True),       # Final video
        gr.update(value=None, visible=False),                  # Final audio
        gr.update(value=[str(final_video), str(final_audio)],  visible=True),       # Download link
        gr.update(value="✅ Video processed.", visible=True),  # Status
    )


# -------------------------------------------------------------------------
# Helper for Gradio error messages
# -------------------------------------------------------------------------
def _gradio_error(msg, staged_input=None):
    """Return a tuple of Gradio component updates for error messages."""
    return (
        gr.update(value=None, visible=False),                  # Original video
        gr.update(value=str(staged_input) if staged_input else None, visible=staged_input is not None),  # Original audio
        gr.update(value=None, visible=False),                  # Final video
        gr.update(value=None, visible=False),                  # Final audio
        gr.update(value=None, visible=False),                  # Download link
        gr.update(value=msg, visible=True),                   # Status
    )
