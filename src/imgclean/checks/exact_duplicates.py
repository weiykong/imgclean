"""Detect exact duplicate files by SHA-256 hash."""

from __future__ import annotations

import uuid
from collections import defaultdict

from imgclean.checks.base import BaseCheck
from imgclean.models.dataset import Dataset
from imgclean.models.finding import Finding
from imgclean.models.issue_types import IssueType, Severity


class ExactDuplicatesCheck(BaseCheck):
    name = "exact_duplicates"
    description = "Detect files that are byte-for-byte identical (same SHA-256 hash)."

    def run(self, dataset: Dataset) -> list[Finding]:
        findings: list[Finding] = []

        # Group records by sha256
        hash_groups: dict[str, list] = defaultdict(list)
        for record in dataset.valid():
            if record.sha256:
                hash_groups[record.sha256].append(record)

        for file_hash, group in hash_groups.items():
            if len(group) < 2:
                continue

            group_id = str(uuid.uuid4())[:8]
            paths = [r.path for r in group]

            # Flag every file in the duplicate group
            for record in group:
                related = [p for p in paths if p != record.path]
                findings.append(
                    Finding(
                        issue_type=IssueType.EXACT_DUPLICATE,
                        severity=Severity.WARNING,
                        file_path=record.path,
                        message=(
                            f"Exact duplicate: SHA-256 {file_hash[:12]}… "
                            f"shared with {len(related)} other file(s)."
                        ),
                        related_files=related,
                        group_id=group_id,
                        metadata={"sha256": file_hash, "group_size": len(group)},
                    )
                )

        return findings
