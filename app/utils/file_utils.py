# app/utils/file_utils.py — File Saving Utility
#
# BUG FIX: The original code used file.file.read() inside a sync function
# called from an async route. This caused the SpooledTemporaryFile to be
# read at the wrong position OR to trigger a browser download of the file
# bytes instead of saving them server-side.
#
# FIX: Accept raw bytes (already awaited in the route) instead of UploadFile.
# The route does: content = await file.read()  →  save_uploaded_file(name, content, dir)

import os
import uuid


def save_uploaded_file(filename: str, content: bytes, upload_dir: str) -> str:
    """
    Saves raw file bytes to disk with a sanitized, collision-safe filename.

    Args:
        filename: Original filename from the upload
        content:  Raw bytes (already read with await file.read())
        upload_dir: Directory to save into

    Returns:
        The final saved filename (with UUID prefix)
    """
    safe_name = os.path.basename(filename).replace(" ", "_")
    prefix = uuid.uuid4().hex[:8]
    final_name = f"{prefix}_{safe_name}"
    file_path = os.path.join(upload_dir, final_name)

    with open(file_path, "wb") as f:
        f.write(content)

    return final_name