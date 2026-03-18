from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class ImageRecord:
    """Represents a single image file discovered during a scan."""

    path: Path
    split: str | None = None          # e.g. "train", "val", "test"
    width: int | None = None
    height: int | None = None
    format: str | None = None          # "JPEG", "PNG", etc.
    mode: str | None = None            # "RGB", "L", etc.
    file_size: int | None = None       # bytes
    sha256: str | None = None
    perceptual_hash: str | None = None # pHash hex string
    embedding_id: str | None = None    # key into embedding store
    is_corrupted: bool = False
    corruption_error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    # ---- derived helpers ----

    @property
    def megapixels(self) -> float | None:
        if self.width is not None and self.height is not None:
            return (self.width * self.height) / 1_000_000
        return None

    @property
    def aspect_ratio(self) -> float | None:
        if self.width and self.height:
            return self.width / self.height
        return None

    @property
    def filename(self) -> str:
        return self.path.name

    def __repr__(self) -> str:
        return f"ImageRecord(path={self.path!r}, size={self.width}x{self.height})"
