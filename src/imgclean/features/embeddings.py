"""
Optional CLIP-based image embeddings for near-duplicate and outlier detection.

This module is only functional when the ``embeddings`` optional dependency
group is installed:

    pip install imgclean[embeddings]
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from PIL import Image as PILImage

_model = None
_preprocess = None
_device = None


def _load_model() -> None:
    global _model, _preprocess, _device
    if _model is not None:
        return

    try:
        import torch
        import open_clip
    except ImportError as exc:
        raise ImportError(
            "Embedding features require optional dependencies. "
            "Install them with: pip install imgclean[embeddings]"
        ) from exc

    _device = "cuda" if torch.cuda.is_available() else "cpu"
    _model, _, _preprocess = open_clip.create_model_and_transforms(
        "ViT-B-32", pretrained="openai", device=_device
    )
    _model.eval()


def embed_image(image: "PILImage.Image") -> np.ndarray:
    """Return a unit-normalised embedding vector for a PIL image."""
    import torch

    _load_model()

    tensor = _preprocess(image).unsqueeze(0).to(_device)  # type: ignore[operator]
    with torch.no_grad():
        features = _model.encode_image(tensor)  # type: ignore[union-attr]
        features /= features.norm(dim=-1, keepdim=True)

    return features.cpu().numpy().squeeze(0)


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine similarity between two normalised vectors."""
    return float(np.dot(a, b))
