"""File and perceptual hashing utilities."""

from __future__ import annotations

import hashlib
from pathlib import Path

import imagehash
from PIL import Image


def sha256(path: Path, chunk_size: int = 65_536) -> str:
    """Compute SHA-256 of a file's raw bytes."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(chunk_size):
            h.update(chunk)
    return h.hexdigest()


def phash(image: Image.Image, hash_size: int = 16) -> str:
    """Compute perceptual hash (pHash) of a PIL image, returned as hex string."""
    return str(imagehash.phash(image, hash_size=hash_size))


def dhash(image: Image.Image, hash_size: int = 16) -> str:
    """Compute difference hash (dHash) of a PIL image."""
    return str(imagehash.dhash(image, hash_size=hash_size))


def hamming_distance(hash_a: str, hash_b: str) -> int:
    """Compute Hamming distance between two imagehash hex strings."""
    a = imagehash.hex_to_hash(hash_a)
    b = imagehash.hex_to_hash(hash_b)
    return a - b  # type: ignore[return-value]
