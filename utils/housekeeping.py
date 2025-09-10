# import time

# def cleanup_temp_files(temp_dir, older_than_seconds=86400):
#     now = time.time()
#     for f in temp_dir.glob("*"):
#         if f.is_file() and (now - f.stat().st_mtime > older_than_seconds):
#             try:
#                 f.unlink(missing_ok=True)
#             except Exception:
#                 pass

import time
from pathlib import Path


def cleanup_temp_files(temp_dir: Path, older_than_seconds: int = 86400):
    """
    Remove old temporary files from the given directory.

    Args:
        temp_dir (Path): Directory containing temporary files.
        older_than_seconds (int, optional): Age threshold in seconds.
            Defaults to 86400 (1 day).

    Notes:
        - Only files are deleted (subdirectories are ignored).
        - Errors during deletion are silently ignored, but a warning is printed.
    """
    now = time.time()

    if not temp_dir.exists():
        print(f"[WARN] Temp directory {temp_dir} does not exist. Skipping cleanup.")
        return

    deleted_count = 0
    for f in temp_dir.glob("*"):
        try:
            if f.is_file() and (now - f.stat().st_mtime > older_than_seconds):
                f.unlink(missing_ok=True)
                deleted_count += 1
                print(f"[INFO] Deleted old temp file: {f}")
        except Exception as e:
            print(f"[WARN] Failed to delete {f}: {e}")

    if deleted_count:
        print(f"[INFO] Cleanup complete. Removed {deleted_count} old files from {temp_dir}.")
    else:
        print(f"[INFO] No old temp files found in {temp_dir}.")
