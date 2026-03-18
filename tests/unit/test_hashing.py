"""Tests for IO hashing utilities."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from imgclean.io.hashing import sha256, phash, dhash, hamming_distance


def _make_rgb_image(width: int = 64, height: int = 64, value: int = 128) -> Image.Image:
    arr = np.full((height, width, 3), value, dtype=np.uint8)
    return Image.fromarray(arr, "RGB")


class TestSha256:
    def test_same_file_same_hash(self, tmp_path: Path) -> None:
        p = tmp_path / "img.jpg"
        _make_rgb_image().save(p, format="JPEG")
        assert sha256(p) == sha256(p)

    def test_different_files_different_hash(self, tmp_path: Path) -> None:
        p1 = tmp_path / "a.png"
        p2 = tmp_path / "b.png"
        _make_rgb_image(value=10).save(p1, format="PNG")
        _make_rgb_image(value=200).save(p2, format="PNG")
        assert sha256(p1) != sha256(p2)

    def test_returns_hex_string(self, tmp_path: Path) -> None:
        p = tmp_path / "img.png"
        _make_rgb_image().save(p, format="PNG")
        h = sha256(p)
        assert len(h) == 64
        assert all(c in "0123456789abcdef" for c in h)


class TestPhash:
    def test_identical_images_zero_distance(self) -> None:
        img = _make_rgb_image()
        h1 = phash(img)
        h2 = phash(img)
        assert hamming_distance(h1, h2) == 0

    def test_very_different_images_large_distance(self) -> None:
        white = _make_rgb_image(value=255)
        black = _make_rgb_image(value=0)
        h1 = phash(white)
        h2 = phash(black)
        assert hamming_distance(h1, h2) > 0

    def test_hash_is_hex_string(self) -> None:
        img = _make_rgb_image()
        h = phash(img)
        assert isinstance(h, str)
        assert len(h) > 0


class TestHammingDistance:
    def test_same_hash_is_zero(self) -> None:
        img = _make_rgb_image()
        h = phash(img)
        assert hamming_distance(h, h) == 0

    def test_non_negative(self) -> None:
        h1 = phash(_make_rgb_image(value=50))
        h2 = phash(_make_rgb_image(value=200))
        assert hamming_distance(h1, h2) >= 0
