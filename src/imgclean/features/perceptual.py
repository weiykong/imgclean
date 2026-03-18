"""Perceptual hash feature extraction."""

from __future__ import annotations

from PIL import Image

from imgclean.io.hashing import phash as _phash, dhash as _dhash


def compute_phash(image: Image.Image, hash_size: int = 16) -> str:
    """Compute pHash for an image; returns hex string."""
    return _phash(image, hash_size=hash_size)


def compute_dhash(image: Image.Image, hash_size: int = 16) -> str:
    """Compute dHash for an image; returns hex string."""
    return _dhash(image, hash_size=hash_size)
