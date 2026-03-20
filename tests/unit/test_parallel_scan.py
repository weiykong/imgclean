"""Tests for scanner parallel execution plumbing."""

from __future__ import annotations

from pathlib import Path

from imgclean.config.schema import Config
from imgclean.core import scanner
from imgclean.models.image_record import ImageRecord


def test_scan_directory_uses_configured_worker_count(
    monkeypatch,
    tmp_path: Path,
) -> None:
    paths = [tmp_path / "a.jpg", tmp_path / "b.jpg", tmp_path / "c.jpg"]
    captured: dict[str, object] = {}

    def fake_parallel_map(
        fn,
        items,
        *,
        max_workers: int | None = None,
        description: str = "Processing",
        show_progress: bool = True,
    ) -> list[ImageRecord]:
        items_list = list(items)
        captured["items"] = items_list
        captured["max_workers"] = max_workers
        captured["description"] = description
        return [fn(item) for item in items_list]

    monkeypatch.setattr(scanner, "discover_images", lambda root, recursive: paths)
    monkeypatch.setattr(scanner, "parallel_map", fake_parallel_map)
    monkeypatch.setattr(
        scanner,
        "_build_record",
        lambda path, *, split, cache: ImageRecord(path=path, split=split),
    )

    config = Config()
    config.parallel.max_workers = 3

    dataset = scanner.scan_directory(tmp_path, config, split="train")

    assert captured["max_workers"] == 3
    assert captured["description"] == "Scanning images…"
    assert captured["items"] == paths
    assert [record.path for record in dataset.records] == paths
    assert all(record.split == "train" for record in dataset.records)
