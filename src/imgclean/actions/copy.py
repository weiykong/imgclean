"""Copy files to a destination directory."""

from __future__ import annotations

import shutil
from pathlib import Path

from imgclean.utils.logging import log


def copy_files(
    paths: list[Path],
    destination: Path,
    root: Path | None = None,
    dry_run: bool = True,
) -> list[Path]:
    """
    Copy each path to ``destination``, preserving relative structure when
    ``root`` is provided.

    Returns the list of destination paths.
    """
    copied: list[Path] = []

    for src in paths:
        dest = _resolve_dest(src, destination, root)

        if dry_run:
            log.info(f"[DRY-RUN] copy: {src} → {dest}")
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(str(src), dest)
            log.info(f"Copied: {src} → {dest}")

        copied.append(dest)

    return copied


def _resolve_dest(src: Path, destination: Path, root: Path | None) -> Path:
    if root is not None:
        try:
            rel = src.relative_to(root)
            return destination / rel
        except ValueError:
            pass
    return destination / src.name
