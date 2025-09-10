# from pathlib import Path
# import shutil, uuid, re

# def resolve_path_from_gradio_file(file_obj):
#     if file_obj is None:
#         return None
#     if isinstance(file_obj, (str, Path)):
#         return Path(file_obj)
#     path = getattr(file_obj, "name", None)
#     if path is None and isinstance(file_obj, dict):
#         path = file_obj.get("name") or file_obj.get("path") or file_obj.get("value")
#     if not path:
#         raise ValueError("Could not resolve uploaded file path.")
#     return Path(path)

# def copy_to_temp(file_obj, temp_dir: Path):
#     src_path = resolve_path_from_gradio_file(file_obj)
#     ext = src_path.suffix.lower()
#     unique_name = f"{uuid.uuid4().hex}{ext}"
#     temp_path = temp_dir / unique_name
#     shutil.copy(src_path, temp_path)
#     return temp_path, src_path.name

# def sanitize_stem(name: str) -> str:
#     stem = Path(name).stem
#     stem = re.sub(r'[^A-Za-z0-9_\-\. ]+', '_', stem).strip()
#     return stem or "file"

# def build_deduped_path(dest_dir: Path, base_stem: str, suffix: str) -> Path:
#     candidate = dest_dir / f"{base_stem}{suffix}"
#     i = 2
#     while candidate.exists():
#         candidate = dest_dir / f"{base_stem}_{i}{suffix}"
#         i += 1
#     return candidate

from pathlib import Path
import shutil, uuid, re


def resolve_path_from_gradio_file(file_obj):
    """
    Resolve and return the file path from a Gradio file object.

    Supports inputs that may be:
    - str or pathlib.Path (already a path)
    - Gradio-like objects with a `name` attribute
    - dict with keys like 'name', 'path', or 'value'

    Args:
        file_obj: File object from Gradio or direct path.

    Returns:
        Path: Resolved file path.

    Raises:
        ValueError: If path cannot be resolved.
    """
    if file_obj is None:
        return None

    if isinstance(file_obj, (str, Path)):
        return Path(file_obj)

    path = getattr(file_obj, "name", None)

    if path is None and isinstance(file_obj, dict):
        path = file_obj.get("name") or file_obj.get("path") or file_obj.get("value")

    if not path:
        raise ValueError("Could not resolve uploaded file path.")

    return Path(path)


def copy_to_temp(file_obj, temp_dir: Path):
    """
    Copy the uploaded file to a temporary directory with a unique name.

    Args:
        file_obj: File object from Gradio or a resolved path.
        temp_dir (Path): Temporary directory to copy into.

    Returns:
        (Path, str): (temp file path, original file name)
    """
    src_path = resolve_path_from_gradio_file(file_obj)
    ext = src_path.suffix.lower()

    unique_name = f"{uuid.uuid4().hex}{ext}"
    temp_path = temp_dir / unique_name

    shutil.copy(src_path, temp_path)

    print(f"[INFO] Copied file '{src_path.name}' → Temp: {temp_path}")
    return temp_path, src_path.name


def sanitize_stem(name: str) -> str:
    """
    Sanitize a file name stem by replacing invalid characters.

    Keeps only letters, digits, underscores, hyphens, dots, and spaces.

    Args:
        name (str): Original file name.

    Returns:
        str: Safe, sanitized file stem.
    """
    stem = Path(name).stem
    stem = re.sub(r'[^A-Za-z0-9_\-\. ]+', '_', stem).strip()
    return stem or "file"


def build_deduped_path(dest_dir: Path, base_stem: str, suffix: str) -> Path:
    """
    Build a unique file path by appending a counter if needed.

    Example:
        - file.txt
        - file_2.txt
        - file_3.txt

    Args:
        dest_dir (Path): Destination directory.
        base_stem (str): Base file name without extension.
        suffix (str): File extension (e.g., '.wav').

    Returns:
        Path: A non-conflicting path inside dest_dir.
    """
    candidate = dest_dir / f"{base_stem}{suffix}"
    i = 2
    while candidate.exists():
        candidate = dest_dir / f"{base_stem}_{i}{suffix}"
        i += 1

    if candidate != dest_dir / f"{base_stem}{suffix}":
        print(f"[WARN] File exists. Using deduped name: {candidate.name}")

    return candidate
