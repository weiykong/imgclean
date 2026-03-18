"""Detect corrupted or unreadable image files."""

from __future__ import annotations

from imgclean.checks.base import BaseCheck
from imgclean.models.dataset import Dataset
from imgclean.models.finding import Finding
from imgclean.models.issue_types import IssueType, Severity


class CorruptionCheck(BaseCheck):
    name = "corruption"
    description = "Detect corrupted, unreadable, or malformed image files."

    def run(self, dataset: Dataset) -> list[Finding]:
        findings: list[Finding] = []

        for record in dataset.records:
            if record.is_corrupted:
                findings.append(
                    Finding(
                        issue_type=IssueType.CORRUPTED,
                        severity=Severity.ERROR,
                        file_path=record.path,
                        message=(
                            f"File cannot be opened or decoded: {record.corruption_error}"
                        ),
                        metadata={"error": record.corruption_error},
                    )
                )

        return findings
