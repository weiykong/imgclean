"""Extract file and EXIF metadata from images."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from PIL import Image
from PIL.ExifTags import TAGS


def file_metadata(path: Path) -> dict[str, Any]:
    """Return basic file-system metadata for a path."""
    stat = path.stat()
    return {
        "file_size": stat.st_size,
        "mtime": stat.st_mtime,
    }


def exif_metadata(image: Image.Image) -> dict[str, Any]:
    """
    Extract human-readable EXIF tags from a PIL image.
    Returns an empty dict if no EXIF data is present.
    """
    try:
        raw = image._getexif()  # type: ignore[attr-defined]
    except (AttributeError, Exception):
        return {}

    if raw is None:
        return {}

    result: dict[str, Any] = {}
    for tag_id, value in raw.items():
        tag = TAGS.get(tag_id, tag_id)
        # Skip binary blobs like MakerNote
        if isinstance(value, bytes) and len(value) > 64:
            continue
        result[str(tag)] = value

    return result
