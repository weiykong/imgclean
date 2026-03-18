"""Disk-based cache for expensive features (hashes, embeddings)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class FeatureCache:
    """
    Key-value cache backed by a single JSON file.

    Keys are file paths (relative or absolute strings).
    Values are arbitrary JSON-serialisable dicts.

    This is intentionally simple: the cache is loaded entirely into memory
    and flushed after all processing. For very large datasets a proper
    database-backed cache (e.g. SQLite) should be used instead.
    """

    def __init__(self, cache_dir: Path, name: str = "features") -> None:
        self._path = cache_dir / f"{name}.json"
        self._data: dict[str, Any] = {}

        if self._path.exists():
            try:
                self._data = json.loads(self._path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                self._data = {}

    def get(self, key: str) -> dict[str, Any] | None:
        return self._data.get(key)

    def set(self, key: str, value: dict[str, Any]) -> None:
        self._data[key] = value

    def flush(self) -> None:
        """Write the cache to disk."""
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(
            json.dumps(self._data, indent=2), encoding="utf-8"
        )

    def invalidate(self, key: str) -> None:
        self._data.pop(key, None)

    def clear(self) -> None:
        self._data = {}

    def __len__(self) -> int:
        return len(self._data)
