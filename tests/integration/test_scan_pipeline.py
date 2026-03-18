"""Integration test: full scan pipeline on a synthetic dataset."""

from __future__ import annotations

import shutil
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from imgclean.config.schema import Config
from imgclean.core.orchestrator import run_scan


def _create_dataset(root: Path) -> None:
    """Create a minimal synthetic dataset."""
    root.mkdir(parents=True, exist_ok=True)

    # Normal images
    for i in range(4):
        arr = np.full((256, 256, 3), 100 + i * 20, dtype=np.uint8)
        Image.fromarray(arr, "RGB").save(root / f"normal_{i}.jpg")

    # Tiny (low-res) image
    arr = np.full((16, 16, 3), 128, dtype=np.uint8)
    Image.fromarray(arr, "RGB").save(root / "tiny.jpg")

    # Duplicate pair — copy bytes to guarantee identical SHA-256
    arr = np.full((256, 256, 3), 200, dtype=np.uint8)
    Image.fromarray(arr, "RGB").save(root / "dup_a.png")
    shutil.copy2(root / "dup_a.png", root / "dup_b.png")

    # Corrupted file
    (root / "corrupt.jpg").write_bytes(b"\x00\x01\x02\x03")


class TestFullScanPipeline:
    def test_scan_runs_without_error(self, tmp_path: Path) -> None:
        _create_dataset(tmp_path / "dataset")
        cfg = Config()
        cfg.cache.enabled = False  # no cache in tests
        report = run_scan(paths=[tmp_path / "dataset"], config=cfg)
        assert report is not None
        assert report.summary.total_files > 0

    def test_corruption_detected(self, tmp_path: Path) -> None:
        _create_dataset(tmp_path / "dataset")
        cfg = Config()
        cfg.cache.enabled = False
        report = run_scan(paths=[tmp_path / "dataset"], config=cfg)
        corrupted = report.summary.issue_counts.get("corrupted", 0)
        assert corrupted >= 1

    def test_low_resolution_detected(self, tmp_path: Path) -> None:
        _create_dataset(tmp_path / "dataset")
        cfg = Config()
        cfg.cache.enabled = False
        report = run_scan(paths=[tmp_path / "dataset"], config=cfg)
        low_res = report.summary.issue_counts.get("low_resolution", 0)
        assert low_res >= 1

    def test_exact_duplicates_detected(self, tmp_path: Path) -> None:
        _create_dataset(tmp_path / "dataset")
        cfg = Config()
        cfg.cache.enabled = False
        report = run_scan(paths=[tmp_path / "dataset"], config=cfg)
        dupes = report.summary.issue_counts.get("exact_duplicate", 0)
        assert dupes >= 2

    def test_report_summary_counts_consistent(self, tmp_path: Path) -> None:
        _create_dataset(tmp_path / "dataset")
        cfg = Config()
        cfg.cache.enabled = False
        report = run_scan(paths=[tmp_path / "dataset"], config=cfg)
        total_in_counts = sum(report.summary.issue_counts.values())
        assert total_in_counts == report.summary.findings_count
