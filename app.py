"""
app.py — Entry point for Amba Denoiser Gradio application.

This script:
- Initializes the inference pipeline (ClearVoice-based denoiser).
- Defines the Gradio UI with file upload, slider for noise reduction %, and output display.
- Handles input type detection (audio vs. video).
- Runs inference + processing when user clicks "Submit".
"""

import gradio as gr
from inference import Inference
from config import ALLOWED_EXTENSIONS, AUDIO_EXTS, VIDEO_EXTS, TEMP_DIR, DEFAULT_SAMPLE_RATE, MODEL_NAME
from utils.gradio_utils import toggle_visibility_on_file
from processing import process_file

# ------------------------------------------------------------
# Initialize inference model
# ------------------------------------------------------------
inference_model = Inference({
    "enabled": True,
    "save_output": True,
    "output_directory": "denoised",
    "sample_rate": DEFAULT_SAMPLE_RATE,
    "model_name": MODEL_NAME
})
print("[App] Inference model initialized with:", MODEL_NAME)

# ------------------------------------------------------------
# Define Gradio interface
# ------------------------------------------------------------
with gr.Blocks(title="Amba Denoiser") as demo:
    gr.Markdown("<h1 style='text-align:center'>🎧 Amba Denoiser</h1>")
    with gr.Row():
        # ------------------- Left column: Input controls -------------------
        with gr.Column(scale=1):
            inp_file = gr.File(
                label="Upload WAV/MP3 or MP4/MOV/MKV/M4V",
                file_types=ALLOWED_EXTENSIONS
            )
            slider = gr.Slider(
                0, 100, value=100, step=1,
                label="Noise Reduction %"
            )
            submit = gr.Button("Submit", variant="primary")

        # ------------------- Right column: Output preview -------------------
        with gr.Column(scale=1):
            out_orig_video = gr.Video(label="Original Video", visible=False)
            out_orig_audio = gr.Audio(label="Original Audio", type="filepath", visible=False)
            out_final_video = gr.Video(label="Final Video", visible=False)
            out_final_audio = gr.Audio(label="Final Audio", type="filepath", visible=False)
            out_download = gr.File(label="Download Final", visible=False)
            out_status = gr.Textbox(label="Status / Log", value="Waiting...")

    # ------------------------------------------------------------
    # Event: Input file uploaded → detect type (audio vs. video)
    # ------------------------------------------------------------
    inp_file.change(
        fn=lambda f: toggle_visibility_on_file(
            f, AUDIO_EXTS, VIDEO_EXTS, ALLOWED_EXTENSIONS
        ),
        inputs=[inp_file],
        outputs=[
            out_orig_video,
            out_orig_audio,
            out_final_video,
            out_final_audio,
            out_download,
            out_status,
        ]
    )

    # ------------------------------------------------------------
    # Event: Submit button → run inference pipeline
    # ------------------------------------------------------------
    submit.click(
        fn=lambda f, n: process_file(f, n, inference_model),
        inputs=[inp_file, slider],
        outputs=[
            out_orig_video,
            out_orig_audio,
            out_final_video,
            out_final_audio,
            out_download,
            out_status,
        ]
    )

# Enable queuing (safer for multiple users / async calls)
demo.queue()

# ------------------------------------------------------------
# Launch Gradio app
# ------------------------------------------------------------
if __name__ == "__main__":
    print("[App] Launching Gradio interface on http://0.0.0.0:7860 ...")
    demo.launch(server_name="0.0.0.0", server_port=7860, share=True)
