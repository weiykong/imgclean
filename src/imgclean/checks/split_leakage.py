"""Detect train/val/test leakage via exact and perceptual hash comparison."""

from __future__ import annotations

import uuid
from itertools import combinations

from imgclean.checks.base import BaseCheck
from imgclean.io.hashing import hamming_distance
from imgclean.models.dataset import Dataset
from imgclean.models.finding import Finding
from imgclean.models.issue_types import IssueType, Severity


class SplitLeakageCheck(BaseCheck):
    name = "split_leakage"
    description = (
        "Detect images that appear in multiple dataset splits "
        "(train/val/test contamination)."
    )

    def run(self, dataset: Dataset) -> list[Finding]:
        split_names = dataset.split_names()
        if len(split_names) < 2:
            return []

        findings: list[Finding] = []
        findings.extend(self._exact_leakage(dataset, split_names))
        findings.extend(self._perceptual_leakage(dataset, split_names))
        return findings

    def _exact_leakage(
        self, dataset: Dataset, split_names: list[str]
    ) -> list[Finding]:
        findings: list[Finding] = []

        # Build hash -> (split, record) mapping
        hash_map: dict[str, list[tuple[str, object]]] = {}
        for record in dataset.valid():
            if record.sha256 and record.split:
                hash_map.setdefault(record.sha256, []).append((record.split, record))

        for file_hash, entries in hash_map.items():
            splits_present = {s for s, _ in entries}
            if len(splits_present) < 2:
                continue

            group_id = str(uuid.uuid4())[:8]
            for split, record in entries:
                other_paths = [r.path for s, r in entries if r is not record]  # type: ignore[attr-defined]
                other_splits = [s for s, r in entries if r is not record]  # type: ignore[attr-defined]
                findings.append(
                    Finding(
                        issue_type=IssueType.SPLIT_LEAKAGE,
                        severity=Severity.ERROR,
                        file_path=record.path,  # type: ignore[attr-defined]
                        message=(
                            f"Exact leakage: same file found in splits "
                            f"{sorted(splits_present)}."
                        ),
                        related_files=other_paths,
                        group_id=group_id,
                        metadata={
                            "split": split,
                            "other_splits": other_splits,
                            "sha256": file_hash,
                            "leakage_type": "exact",
                        },
                    )
                )

        return findings

    def _perceptual_leakage(
        self, dataset: Dataset, split_names: list[str]
    ) -> list[Finding]:
        findings: list[Finding] = []
        max_distance = self.thresholds.phash_hamming_max

        # Build split -> records with phash
        split_records = {
            name: [r for r in dataset.by_split(name) if r.perceptual_hash]
            for name in split_names
        }

        for split_a, split_b in combinations(split_names, 2):
            records_a = split_records[split_a]
            records_b = split_records[split_b]

            for rec_a in records_a:
                for rec_b in records_b:
                    # Skip exact duplicates already caught
                    if rec_a.sha256 and rec_a.sha256 == rec_b.sha256:
                        continue

                    dist = hamming_distance(
                        rec_a.perceptual_hash,  # type: ignore[arg-type]
                        rec_b.perceptual_hash,  # type: ignore[arg-type]
                    )
                    if dist <= max_distance:
                        group_id = str(uuid.uuid4())[:8]
                        for rec, other, own_split, other_split in [
                            (rec_a, rec_b, split_a, split_b),
                            (rec_b, rec_a, split_b, split_a),
                        ]:
                            findings.append(
                                Finding(
                                    issue_type=IssueType.SPLIT_LEAKAGE,
                                    severity=Severity.WARNING,
                                    file_path=rec.path,
                                    score=float(dist),
                                    threshold=float(max_distance),
                                    message=(
                                        f"Perceptual leakage: visually similar image in "
                                        f"'{own_split}' matches '{other_split}' "
                                        f"(Hamming {dist})."
                                    ),
                                    related_files=[other.path],
                                    group_id=group_id,
                                    metadata={
                                        "split": own_split,
                                        "other_split": other_split,
                                        "hamming_distance": dist,
                                        "leakage_type": "perceptual",
                                    },
                                )
                            )

        return findings
