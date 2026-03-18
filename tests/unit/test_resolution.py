"""Tests for the resolution check."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from imgclean.checks.resolution import ResolutionCheck
from imgclean.config.schema import Config, ThresholdsConfig
from imgclean.models.dataset import Dataset
from imgclean.models.image_record import ImageRecord


def _config(min_w: int = 256, min_h: int = 256) -> Config:
    cfg = Config()
    cfg.thresholds = ThresholdsConfig(min_width=min_w, min_height=min_h)
    return cfg


def _record(path: Path, width: int, height: int) -> ImageRecord:
    return ImageRecord(path=path, width=width, height=height)


class TestResolutionCheck:
    def test_no_findings_for_large_image(self, tmp_path: Path) -> None:
        record = _record(tmp_path / "big.jpg", 512, 512)
        dataset = Dataset(records=[record])
        check = ResolutionCheck(_config(min_w=256, min_h=256))
        assert check.run(dataset) == []

    def test_finding_for_tiny_image(self, tmp_path: Path) -> None:
        record = _record(tmp_path / "tiny.jpg", 32, 32)
        dataset = Dataset(records=[record])
        check = ResolutionCheck(_config(min_w=256, min_h=256))
        findings = check.run(dataset)
        assert len(findings) == 1
        assert findings[0].file_path == record.path

    def test_border_case_exactly_at_threshold_passes(self, tmp_path: Path) -> None:
        record = _record(tmp_path / "border.jpg", 256, 256)
        dataset = Dataset(records=[record])
        check = ResolutionCheck(_config(min_w=256, min_h=256))
        assert check.run(dataset) == []

    def test_corrupted_records_skipped(self, tmp_path: Path) -> None:
        record = ImageRecord(
            path=tmp_path / "corrupt.jpg",
            width=10,
            height=10,
            is_corrupted=True,
        )
        dataset = Dataset(records=[record])
        check = ResolutionCheck(_config())
        assert check.run(dataset) == []
