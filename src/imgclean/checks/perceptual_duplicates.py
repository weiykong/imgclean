"""Detect near-duplicate images using perceptual hashing (pHash)."""

from __future__ import annotations

import uuid
from collections import defaultdict, deque

from imgclean.checks.base import BaseCheck
from imgclean.io.hashing import hamming_distance
from imgclean.models.dataset import Dataset
from imgclean.models.finding import Finding
from imgclean.models.image_record import ImageRecord
from imgclean.models.issue_types import IssueType, Severity


class PerceptualDuplicatesCheck(BaseCheck):
    name = "perceptual_duplicates"
    description = (
        "Detect visually similar images using perceptual hashing (pHash) "
        "and Hamming distance."
    )

    def run(self, dataset: Dataset) -> list[Finding]:
        valid = [r for r in dataset.valid() if r.perceptual_hash is not None]
        if len(valid) < 2:
            return []

        max_distance = self.thresholds.phash_hamming_max
        clusters = self._cluster(valid, max_distance)
        return self._build_findings(clusters, max_distance)

    def _cluster(
        self, records: list[ImageRecord], max_distance: int
    ) -> list[list[ImageRecord]]:
        """
        Build clusters of near-duplicate records using a union-find approach
        on pairwise Hamming distances.
        """
        n = len(records)
        parent = list(range(n))

        def find(x: int) -> int:
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(x: int, y: int) -> None:
            parent[find(x)] = find(y)

        for i in range(n):
            for j in range(i + 1, n):
                dist = hamming_distance(
                    records[i].perceptual_hash,  # type: ignore[arg-type]
                    records[j].perceptual_hash,  # type: ignore[arg-type]
                )
                if dist <= max_distance:
                    union(i, j)

        groups: dict[int, list[ImageRecord]] = defaultdict(list)
        for i, record in enumerate(records):
            groups[find(i)].append(record)

        return [g for g in groups.values() if len(g) >= 2]

    def _build_findings(
        self, clusters: list[list[ImageRecord]], threshold: int
    ) -> list[Finding]:
        findings: list[Finding] = []

        for cluster in clusters:
            group_id = str(uuid.uuid4())[:8]
            paths = [r.path for r in cluster]

            for record in cluster:
                related = [p for p in paths if p != record.path]
                findings.append(
                    Finding(
                        issue_type=IssueType.NEAR_DUPLICATE,
                        severity=Severity.WARNING,
                        file_path=record.path,
                        threshold=float(threshold),
                        message=(
                            f"Near-duplicate: visually similar to "
                            f"{len(related)} other image(s) (pHash Hamming ≤ {threshold})."
                        ),
                        related_files=related,
                        group_id=group_id,
                        metadata={"phash": record.perceptual_hash, "cluster_size": len(cluster)},
                    )
                )

        return findings
