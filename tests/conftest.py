"""Shared test fixtures."""

from __future__ import annotations

import io
from pathlib import Path

import numpy as np
import pytest
from PIL import Image


# ---- Image factories ----

def _make_image(width: int, height: int, mode: str = "RGB", value: int = 128) -> Image.Image:
    data = np.full((height, width, 3 if mode == "RGB" else 1), value, dtype=np.uint8)
    if mode == "L":
        data = data.squeeze(-1)
    return Image.fromarray(data, mode=mode)


def _save_image(img: Image.Image, path: Path, fmt: str = "JPEG") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, format=fmt)
    return path


@pytest.fixture()
def tmp_image_dir(tmp_path: Path) -> Path:
    """A temporary directory pre-populated with a few valid images."""
    for i in range(5):
        img = _make_image(256, 256, value=100 + i * 10)
        _save_image(img, tmp_path / f"img_{i:02d}.jpg")
    return tmp_path


@pytest.fixture()
def sharp_image() -> Image.Image:
    """A sharp image with high Laplacian variance."""
    # Checkerboard pattern → high frequency content → high variance
    arr = np.zeros((128, 128), dtype=np.uint8)
    arr[::2, ::2] = 255
    arr[1::2, 1::2] = 255
    return Image.fromarray(arr, mode="L").convert("RGB")


@pytest.fixture()
def blurry_image() -> Image.Image:
    """A uniformly grey image → near-zero Laplacian variance."""
    return _make_image(128, 128, value=128)


@pytest.fixture()
def dark_image() -> Image.Image:
    """A very dark image."""
    return _make_image(128, 128, value=5)


@pytest.fixture()
def bright_image() -> Image.Image:
    """A very bright (overexposed) image."""
    return _make_image(128, 128, value=250)


@pytest.fixture()
def corrupted_file(tmp_path: Path) -> Path:
    """A file with a .jpg extension but garbage contents."""
    p = tmp_path / "corrupt.jpg"
    p.write_bytes(b"\x00" * 100)
    return p


@pytest.fixture()
def valid_image_file(tmp_path: Path) -> Path:
    img = _make_image(256, 256)
    return _save_image(img, tmp_path / "valid.jpg")
