# import subprocess, uuid
# from pathlib import Path

# def run_ffmpeg(args):
#     try:
#         proc = subprocess.run(
#             ["ffmpeg", *args],
#             stdout=subprocess.PIPE, stderr=subprocess.PIPE,
#             text=True, check=True
#         )
#         return proc
#     except FileNotFoundError:
#         raise RuntimeError("ffmpeg not found.")
#     except subprocess.CalledProcessError as e:
#         raise RuntimeError(f"ffmpeg failed: {e.stderr.strip()[:2000]}")

# def extract_audio_from_video(video_path: Path, sr=48000, temp_dir: Path = Path(".")) -> Path:
#     out_wav = temp_dir / f"{uuid.uuid4().hex}.wav"
#     args = ["-y", "-i", str(video_path),
#             "-map", "a:0?", "-vn",
#             "-acodec", "pcm_s16le",
#             "-ar", str(sr), str(out_wav)]
#     run_ffmpeg(args)
#     if not out_wav.exists() or out_wav.stat().st_size == 0:
#         raise RuntimeError("No audio stream found in video.")
#     return out_wav

# def mux_clean_audio_back(video_src_path: Path, clean_audio_path: Path, dest_video_path: Path):
#     dest_video_path.parent.mkdir(parents=True, exist_ok=True)
#     args = ["-y", "-i", str(video_src_path),
#             "-i", str(clean_audio_path),
#             "-map", "0:v:0?", "-map", "1:a:0?",
#             "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
#             "-shortest", str(dest_video_path)]
#     run_ffmpeg(args)
#     if not dest_video_path.exists():
#         raise RuntimeError("Failed to mux cleaned audio back into video.")

"""
ffmpeg_utils.py — Utility functions for audio/video processing via FFmpeg.

This module provides:
- A safe wrapper to run ffmpeg commands.
- Audio extraction from video files.
- Muxing (replacing) audio back into a video.
"""

import subprocess
import uuid
from pathlib import Path


def run_ffmpeg(args):
    """
    Run an ffmpeg command with given arguments.

    :param args: List of ffmpeg command arguments (without "ffmpeg").
    :return: CompletedProcess object from subprocess.run.
    :raises RuntimeError: If ffmpeg is not installed or the command fails.
    """
    try:
        proc = subprocess.run(
            ["ffmpeg", *args],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        return proc
    except FileNotFoundError:
        raise RuntimeError("ffmpeg not found. Please ensure it is installed and in PATH.")
    except subprocess.CalledProcessError as e:
        # Limit error output to avoid overly long logs
        raise RuntimeError(f"ffmpeg failed: {e.stderr.strip()[:2000]}")


def extract_audio_from_video(video_path: Path, sr: int = 48000, temp_dir: Path = Path(".")) -> Path:
    """
    Extract the first audio stream from a video file into a temporary WAV.

    :param video_path: Path to the source video file.
    :param sr: Output sample rate (default: 48 kHz).
    :param temp_dir: Directory for temporary output file.
    :return: Path to the extracted WAV file.
    :raises RuntimeError: If no audio stream is found.
    """
    out_wav = temp_dir / f"{uuid.uuid4().hex}.wav"

    args = [
        "-y", "-i", str(video_path),     # Input file
        "-map", "a:0?", "-vn",           # Select first audio stream, drop video
        "-acodec", "pcm_s16le",          # Raw PCM audio
        "-ar", str(sr),                  # Set sample rate
        str(out_wav)
    ]
    run_ffmpeg(args)

    if not out_wav.exists() or out_wav.stat().st_size == 0:
        raise RuntimeError("No audio stream found in video.")

    return out_wav


def mux_clean_audio_back(video_src_path: Path, clean_audio_path: Path, dest_video_path: Path):
    """
    Replace the audio of a video file with a cleaned audio track.

    :param video_src_path: Path to the original video.
    :param clean_audio_path: Path to the cleaned audio file (e.g., denoised).
    :param dest_video_path: Path for the output video with replaced audio.
    :raises RuntimeError: If muxing fails.
    """
    # Ensure output directory exists
    dest_video_path.parent.mkdir(parents=True, exist_ok=True)

    args = [
        "-y", "-i", str(video_src_path),     # Input video
        "-i", str(clean_audio_path),         # Input audio
        "-map", "0:v:0?", "-map", "1:a:0?", # Use video from first input, audio from second
        "-c:v", "copy",                      # Copy video without re-encoding
        "-c:a", "aac", "-b:a", "192k",       # Encode audio as AAC
        "-shortest",                         # Match shortest stream length
        str(dest_video_path)
    ]
    run_ffmpeg(args)

    if not dest_video_path.exists():
        raise RuntimeError("Failed to mux cleaned audio back into video.")
