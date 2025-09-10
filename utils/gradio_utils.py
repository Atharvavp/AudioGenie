# from pathlib import Path
# import gradio as gr

# def _ext_from_file(file_obj) -> str:
#     if file_obj is None:
#         return ""
#     if isinstance(file_obj, (str, Path)):
#         return Path(file_obj).suffix.lower()
#     name = getattr(file_obj, "name", None)
#     if name is None and isinstance(file_obj, dict):
#         name = file_obj.get("name") or file_obj.get("path") or file_obj.get("value")
#     return Path(name or "").suffix.lower()

# def toggle_visibility_on_file(file, audio_exts, video_exts, allowed_exts):
#     ext = _ext_from_file(file)
#     is_audio = ext in audio_exts
#     is_video = ext in video_exts

#     return (
#         gr.update(visible=is_video, value=None),
#         gr.update(visible=is_audio, value=None),
#         gr.update(visible=is_video, value=None),
#         gr.update(visible=is_audio, value=None),
#         gr.update(visible=False, value=None),
#         gr.update(
#             visible=True,
#             value="Ready. Click Submit." if ext in allowed_exts else "Select a valid file."
#         ),
#     )

from pathlib import Path
import gradio as gr


def _ext_from_file(file_obj) -> str:
    """
    Extract the file extension (in lowercase) from a Gradio file object.

    Supports:
    - str or Path input
    - Gradio file object with a 'name' attribute
    - dict with 'name', 'path', or 'value'

    Args:
        file_obj: File object from Gradio or direct path.

    Returns:
        str: File extension (including dot), e.g., '.wav', or "" if not resolvable.
    """
    if file_obj is None:
        return ""

    if isinstance(file_obj, (str, Path)):
        return Path(file_obj).suffix.lower()

    name = getattr(file_obj, "name", None)

    if name is None and isinstance(file_obj, dict):
        name = file_obj.get("name") or file_obj.get("path") or file_obj.get("value")

    return Path(name or "").suffix.lower()


def toggle_visibility_on_file(file, audio_exts, video_exts, allowed_exts):
    """
    Toggle the visibility of Gradio components based on uploaded file type.

    Args:
        file: Uploaded file object (from Gradio).
        audio_exts (list[str]): Allowed audio extensions.
        video_exts (list[str]): Allowed video extensions.
        allowed_exts (list[str]): All valid extensions (audio + video).

    Returns:
        tuple: Gradio update objects for UI components in order:
            (Original Video, Original Audio, Final Video, Final Audio,
             Download Button, Status Box)
    """
    ext = _ext_from_file(file)
    is_audio = ext in audio_exts
    is_video = ext in video_exts

    if ext:
        print(f"[INFO] Uploaded file detected with extension: {ext}")
    else:
        print("[WARN] No valid file extension found.")

    return (
        gr.update(visible=is_video, value=None),   # Show Original Video if video
        gr.update(visible=is_audio, value=None),   # Show Original Audio if audio
        gr.update(visible=is_video, value=None),   # Show Final Video if video
        gr.update(visible=is_audio, value=None),   # Show Final Audio if audio
        gr.update(visible=False, value=None),      # Hide Download button initially
        gr.update(                             # Status box
            visible=True,
            value="Ready. Click Submit." if ext in allowed_exts else "Select a valid file."
        ),
    )
