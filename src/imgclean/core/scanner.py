"""
Scan directories to produce a Dataset of ImageRecords.

This is intentionally the only place that calls the filesystem and image
loader — checks receive fully-populated records and never touch disk directly.
"""

from __future__ import annotations

from pathlib import Path

from rich.progress import BarColumn, Progress, SpinnerColumn, TaskProgressColumn, TextColumn

from imgclean.config.schema import Config
from imgclean.features.metadata import file_metadata
from imgclean.io.cache import FeatureCache
from imgclean.io.filesystem import discover_images, discover_splits
from imgclean.io.hashing import phash as compute_phash, sha256 as compute_sha256
from imgclean.io.image_loader import load_image
from imgclean.models.dataset import Dataset
from imgclean.models.image_record import ImageRecord
from imgclean.utils.logging import log


def scan_directory(
    root: Path,
    config: Config,
    split: str | None = None,
    cache: FeatureCache | None = None,
) -> Dataset:
    """Scan a single directory and return a Dataset of ImageRecords."""
    paths = discover_images(root, recursive=config.dataset.recursive)
    log.info(f"Found {len(paths)} image(s) in [bold]{root}[/bold]")
    records = _build_records(paths, config, split=split, cache=cache)
    return Dataset(records=records, root=root)


def scan_splits(splits: dict[str, Path], config: Config) -> Dataset:
    """Scan multiple split directories and return a merged Dataset."""
    all_records: list[ImageRecord] = []
    root_candidates: list[Path] = []

    cache: FeatureCache | None = None
    if config.cache.enabled:
        # Use the first split's parent as the cache root
        first_root = next(iter(splits.values()))
        cache_dir = first_root.parent / config.cache.dir_name
        cache = FeatureCache(cache_dir)

    for split_name, directory in splits.items():
        directory = directory.resolve()
        root_candidates.append(directory)
        paths = discover_images(directory, recursive=config.dataset.recursive)
        log.info(
            f"Split [bold]{split_name!r}[/bold]: {len(paths)} image(s) in {directory}"
        )
        records = _build_records(paths, config, split=split_name, cache=cache)
        all_records.extend(records)

    if cache:
        cache.flush()

    # Find common root
    root: Path | None = None
    if root_candidates:
        try:
            root = Path(*root_candidates).parent
        except TypeError:
            root = root_candidates[0].parent

    return Dataset(records=all_records, root=root)


def _build_records(
    paths: list[Path],
    config: Config,
    split: str | None,
    cache: FeatureCache | None,
) -> list[ImageRecord]:
    records: list[ImageRecord] = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
    ) as progress:
        task = progress.add_task("Scanning images…", total=len(paths))

        for path in paths:
            record = _build_record(path, split=split, config=config, cache=cache)
            records.append(record)
            progress.advance(task)

    return records


def _build_record(
    path: Path,
    split: str | None,
    config: Config,
    cache: FeatureCache | None,
) -> ImageRecord:
    cache_key = str(path)

    # Return cached features if available and file hasn't changed
    if cache:
        cached = cache.get(cache_key)
        if cached and _cache_is_valid(path, cached):
            return _record_from_cache(path, split, cached)

    fs_meta = file_metadata(path)
    load_result = load_image(path)

    record = ImageRecord(
        path=path,
        split=split,
        width=load_result.width,
        height=load_result.height,
        format=load_result.format,
        mode=load_result.mode,
        file_size=fs_meta["file_size"],
        is_corrupted=load_result.is_corrupted,
        corruption_error=load_result.error,
    )

    if not load_result.is_corrupted and load_result.image is not None:
        record.sha256 = compute_sha256(path)
        try:
            record.perceptual_hash = compute_phash(load_result.image)
        except Exception:  # noqa: BLE001
            pass

    if cache:
        cache.set(cache_key, _record_to_cache(record, fs_meta["mtime"]))

    return record


def _cache_is_valid(path: Path, cached: dict) -> bool:
    try:
        current_mtime = path.stat().st_mtime
        return abs(current_mtime - cached.get("mtime", 0)) < 1.0
    except OSError:
        return False


def _record_to_cache(record: ImageRecord, mtime: float) -> dict:
    return {
        "mtime": mtime,
        "width": record.width,
        "height": record.height,
        "format": record.format,
        "mode": record.mode,
        "file_size": record.file_size,
        "sha256": record.sha256,
        "perceptual_hash": record.perceptual_hash,
        "is_corrupted": record.is_corrupted,
        "corruption_error": record.corruption_error,
    }


def _record_from_cache(path: Path, split: str | None, data: dict) -> ImageRecord:
    return ImageRecord(
        path=path,
        split=split,
        width=data.get("width"),
        height=data.get("height"),
        format=data.get("format"),
        mode=data.get("mode"),
        file_size=data.get("file_size"),
        sha256=data.get("sha256"),
        perceptual_hash=data.get("perceptual_hash"),
        is_corrupted=data.get("is_corrupted", False),
        corruption_error=data.get("corruption_error"),
    )
