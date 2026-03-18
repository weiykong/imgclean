"""Detect images that are too small to be useful."""

from __future__ import annotations

from imgclean.checks.base import BaseCheck
from imgclean.models.dataset import Dataset
from imgclean.models.finding import Finding
from imgclean.models.issue_types import IssueType, Severity


class ResolutionCheck(BaseCheck):
    name = "resolution"
    description = "Flag images below the minimum width or height threshold."

    def run(self, dataset: Dataset) -> list[Finding]:
        findings: list[Finding] = []
        min_w = self.thresholds.min_width
        min_h = self.thresholds.min_height

        for record in dataset.valid():
            if record.width is None or record.height is None:
                continue

            if record.width < min_w or record.height < min_h:
                findings.append(
                    Finding(
                        issue_type=IssueType.LOW_RESOLUTION,
                        severity=Severity.WARNING,
                        file_path=record.path,
                        message=(
                            f"Image is {record.width}×{record.height}px, "
                            f"below the minimum {min_w}×{min_h}px."
                        ),
                        metadata={"width": record.width, "height": record.height},
                    )
                )

        return findings
