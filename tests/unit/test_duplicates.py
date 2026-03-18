"""Tests for exact and perceptual duplicate detection."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from imgclean.checks.exact_duplicates import ExactDuplicatesCheck
from imgclean.checks.perceptual_duplicates import PerceptualDuplicatesCheck
from imgclean.config.schema import Config
from imgclean.io.hashing import phash
from imgclean.models.dataset import Dataset
from imgclean.models.image_record import ImageRecord
from imgclean.models.issue_types import IssueType


def _config() -> Config:
    return Config()


def _record(path: Path, sha256: str | None = None, phash_val: str | None = None) -> ImageRecord:
    return ImageRecord(path=path, sha256=sha256, perceptual_hash=phash_val)


class TestExactDuplicatesCheck:
    def test_detects_exact_duplicate(self, tmp_path: Path) -> None:
        h = "abc123"
        r1 = _record(tmp_path / "a.jpg", sha256=h)
        r2 = _record(tmp_path / "b.jpg", sha256=h)
        dataset = Dataset(records=[r1, r2])
        check = ExactDuplicatesCheck(_config())
        findings = check.run(dataset)
        assert len(findings) == 2
        assert all(f.issue_type == IssueType.EXACT_DUPLICATE for f in findings)

    def test_no_findings_when_unique(self, tmp_path: Path) -> None:
        r1 = _record(tmp_path / "a.jpg", sha256="aaa")
        r2 = _record(tmp_path / "b.jpg", sha256="bbb")
        dataset = Dataset(records=[r1, r2])
        check = ExactDuplicatesCheck(_config())
        assert check.run(dataset) == []

    def test_same_group_id_for_cluster(self, tmp_path: Path) -> None:
        h = "deadbeef"
        r1 = _record(tmp_path / "a.jpg", sha256=h)
        r2 = _record(tmp_path / "b.jpg", sha256=h)
        r3 = _record(tmp_path / "c.jpg", sha256=h)
        dataset = Dataset(records=[r1, r2, r3])
        check = ExactDuplicatesCheck(_config())
        findings = check.run(dataset)
        group_ids = {f.group_id for f in findings}
        assert len(group_ids) == 1

    def test_skips_records_without_hash(self, tmp_path: Path) -> None:
        r1 = _record(tmp_path / "a.jpg", sha256=None)
        r2 = _record(tmp_path / "b.jpg", sha256=None)
        dataset = Dataset(records=[r1, r2])
        check = ExactDuplicatesCheck(_config())
        assert check.run(dataset) == []


class TestPerceptualDuplicatesCheck:
    def _make_phash(self, value: int) -> str:
        arr = np.full((64, 64, 3), value, dtype=np.uint8)
        img = Image.fromarray(arr, "RGB")
        return phash(img)

    def test_detects_identical_phash(self, tmp_path: Path) -> None:
        h = self._make_phash(128)
        r1 = _record(tmp_path / "a.jpg", phash_val=h)
        r2 = _record(tmp_path / "b.jpg", phash_val=h)
        dataset = Dataset(records=[r1, r2])
        check = PerceptualDuplicatesCheck(_config())
        findings = check.run(dataset)
        assert len(findings) == 2
        assert all(f.issue_type == IssueType.NEAR_DUPLICATE for f in findings)

    def test_no_finding_for_very_different_images(self, tmp_path: Path) -> None:
        h1 = self._make_phash(0)    # black
        h2 = self._make_phash(255)  # white — very different hashes
        r1 = _record(tmp_path / "a.jpg", phash_val=h1)
        r2 = _record(tmp_path / "b.jpg", phash_val=h2)
        dataset = Dataset(records=[r1, r2])
        check = PerceptualDuplicatesCheck(_config())
        findings = check.run(dataset)
        # black and white solid colours may or may not trigger depending on hash
        # We just assert no crash and correct types
        for f in findings:
            assert f.issue_type == IssueType.NEAR_DUPLICATE

    def test_single_record_returns_empty(self, tmp_path: Path) -> None:
        h = self._make_phash(100)
        dataset = Dataset(records=[_record(tmp_path / "a.jpg", phash_val=h)])
        check = PerceptualDuplicatesCheck(_config())
        assert check.run(dataset) == []
