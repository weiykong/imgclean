from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from imgclean.models.image_record import ImageRecord


@dataclass
class Dataset:
    """Collection of ImageRecords representing a scanned folder or set of splits."""

    records: list[ImageRecord] = field(default_factory=list)
    root: Path | None = None           # common root directory
    splits: dict[str, list[Path]] = field(default_factory=dict)  # split -> file paths

    # ---- convenience accessors ----

    def __len__(self) -> int:
        return len(self.records)

    def by_split(self, split: str) -> list[ImageRecord]:
        return [r for r in self.records if r.split == split]

    def corrupted(self) -> list[ImageRecord]:
        return [r for r in self.records if r.is_corrupted]

    def valid(self) -> list[ImageRecord]:
        return [r for r in self.records if not r.is_corrupted]

    def split_names(self) -> list[str]:
        return sorted({r.split for r in self.records if r.split is not None})
