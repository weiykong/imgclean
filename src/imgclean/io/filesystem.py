"""Walk directories and collect image file paths."""

from __future__ import annotations

from pathlib import Path

from imgclean.config.defaults import SUPPORTED_EXTENSIONS


def discover_images(root: Path, recursive: bool = True) -> list[Path]:
    """Return all image files under ``root`` with supported extensions."""
    root = root.resolve()
    if not root.exists():
        raise FileNotFoundError(f"Directory not found: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {root}")

    pattern = "**/*" if recursive else "*"
    paths: list[Path] = []

    for p in root.glob(pattern):
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS:
            paths.append(p)

    return sorted(paths)


def discover_splits(split_dirs: dict[str, str | Path]) -> dict[str, list[Path]]:
    """
    Given a mapping of split_name -> directory, return a mapping of
    split_name -> list of image paths.
    """
    result: dict[str, list[Path]] = {}
    for name, directory in split_dirs.items():
        result[name] = discover_images(Path(directory))
    return result
