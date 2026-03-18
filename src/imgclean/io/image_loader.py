"""Safe image loading with corruption detection."""

from __future__ import annotations

from pathlib import Path
from typing import NamedTuple

from PIL import Image, UnidentifiedImageError


class LoadResult(NamedTuple):
    image: Image.Image | None
    width: int | None
    height: int | None
    format: str | None
    mode: str | None
    is_corrupted: bool
    error: str | None


def load_image(path: Path) -> LoadResult:
    """
    Attempt to open and fully decode an image.
    Returns a LoadResult regardless of success or failure.

    Two-pass strategy:
    1. ``verify()`` right after ``open()`` — catches corrupt headers/checksums.
    2. Re-open and ``load()`` — forces full pixel decoding (catches truncated data).
    """
    # Pass 1: header / checksum verification
    try:
        with Image.open(path) as img:
            img.verify()  # must be called before img.load()
    except (UnidentifiedImageError, OSError, SyntaxError, ValueError) as exc:
        return LoadResult(
            image=None,
            width=None,
            height=None,
            format=None,
            mode=None,
            is_corrupted=True,
            error=str(exc),
        )
    except Exception as exc:  # noqa: BLE001
        return LoadResult(
            image=None,
            width=None,
            height=None,
            format=None,
            mode=None,
            is_corrupted=True,
            error=f"Unexpected error during verify: {exc}",
        )

    # Pass 2: full pixel decoding (verify() closes the internal file handle)
    try:
        with Image.open(path) as img:
            img.load()
            return LoadResult(
                image=img.copy(),
                width=img.width,
                height=img.height,
                format=img.format,
                mode=img.mode,
                is_corrupted=False,
                error=None,
            )
    except (UnidentifiedImageError, OSError, SyntaxError, ValueError) as exc:
        return LoadResult(
            image=None,
            width=None,
            height=None,
            format=None,
            mode=None,
            is_corrupted=True,
            error=str(exc),
        )
    except Exception as exc:  # noqa: BLE001
        return LoadResult(
            image=None,
            width=None,
            height=None,
            format=None,
            mode=None,
            is_corrupted=True,
            error=f"Unexpected error during load: {exc}",
        )
