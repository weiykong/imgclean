"""Detect images with extreme or unusual aspect ratios."""

from __future__ import annotations

from imgclean.checks.base import BaseCheck
from imgclean.models.dataset import Dataset
from imgclean.models.finding import Finding
from imgclean.models.issue_types import IssueType, Severity


class AspectRatioCheck(BaseCheck):
    name = "aspect_ratio"
    description = "Flag images with extreme aspect ratios (very wide or very tall)."

    def run(self, dataset: Dataset) -> list[Finding]:
        findings: list[Finding] = []
        ar_min = self.thresholds.aspect_ratio_min
        ar_max = self.thresholds.aspect_ratio_max

        for record in dataset.valid():
            ratio = record.aspect_ratio
            if ratio is None:
                continue

            if ratio < ar_min or ratio > ar_max:
                direction = "tall/portrait" if ratio < 1 else "wide/landscape"
                findings.append(
                    Finding(
                        issue_type=IssueType.ASPECT_RATIO,
                        severity=Severity.WARNING,
                        file_path=record.path,
                        score=ratio,
                        message=(
                            f"Extreme aspect ratio {ratio:.2f} ({direction}). "
                            f"Expected between {ar_min} and {ar_max}."
                        ),
                        metadata={
                            "aspect_ratio": ratio,
                            "width": record.width,
                            "height": record.height,
                        },
                    )
                )

        return findings
