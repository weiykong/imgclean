"""Image quality feature extraction: blur, exposure."""

from __future__ import annotations

import cv2
import numpy as np
from PIL import Image


def laplacian_variance(image: Image.Image) -> float:
    """
    Compute variance of the Laplacian — higher values mean sharper image.
    Low values indicate blur.
    """
    gray = _to_gray_np(image)
    lap = cv2.Laplacian(gray, cv2.CV_64F)
    return float(lap.var())


def mean_brightness(image: Image.Image) -> float:
    """
    Compute mean pixel brightness in the range [0, 255].
    Works on both grayscale and colour images.
    """
    gray = _to_gray_np(image)
    return float(gray.mean())


def saturation_ratio(image: Image.Image, low_thresh: int = 5, high_thresh: int = 250) -> tuple[float, float]:
    """
    Return (dark_ratio, bright_ratio): fraction of pixels that are nearly
    black or nearly white respectively.
    """
    gray = _to_gray_np(image)
    total = gray.size
    dark = float(np.sum(gray < low_thresh)) / total
    bright = float(np.sum(gray > high_thresh)) / total
    return dark, bright


def _to_gray_np(image: Image.Image) -> np.ndarray:
    """Convert a PIL image to a uint8 grayscale numpy array."""
    if image.mode != "L":
        image = image.convert("L")
    return np.array(image, dtype=np.uint8)
