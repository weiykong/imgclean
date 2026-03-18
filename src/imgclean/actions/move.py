"""Move files from one location to another, preserving relative structure."""

from __future__ import annotations

import shutil
from pathlib import Path

from imgclean.utils.logging import log


def move_files(
    paths: list[Path],
    destination: Path,
    root: Path | None = None,
    dry_run: bool = True,
) -> list[Path]:
    """
    Move each path to ``destination``, optionally preserving the directory
    structure relative to ``root``.

    Returns the list of destination paths that were (or would be) created.
    """
    moved: list[Path] = []

    for src in paths:
        dest = _resolve_dest(src, destination, root)

        if dry_run:
            log.info(f"[DRY-RUN] move: {src} → {dest}")
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), dest)
            log.info(f"Moved: {src} → {dest}")

        moved.append(dest)

    return moved


def _resolve_dest(src: Path, destination: Path, root: Path | None) -> Path:
    if root is not None:
        try:
            rel = src.relative_to(root)
            return destination / rel
        except ValueError:
            pass
    return destination / src.name
