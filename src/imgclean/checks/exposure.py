"""Detect underexposed or overexposed images."""

from __future__ import annotations

from imgclean.checks.base import BaseCheck
from imgclean.features.quality import mean_brightness
from imgclean.models.dataset import Dataset
from imgclean.models.finding import Finding
from imgclean.models.issue_types import IssueType, Severity


class ExposureCheck(BaseCheck):
    name = "exposure"
    description = "Flag images that are too dark (underexposed) or too bright (overexposed)."

    def run(self, dataset: Dataset) -> list[Finding]:
        from imgclean.io.image_loader import load_image

        findings: list[Finding] = []
        dark_max = self.thresholds.exposure_dark_max
        bright_min = self.thresholds.exposure_bright_min

        for record in dataset.valid():
            result = load_image(record.path)
            if result.is_corrupted or result.image is None:
                continue

            brightness = mean_brightness(result.image)

            if brightness < dark_max:
                findings.append(
                    Finding(
                        issue_type=IssueType.UNDEREXPOSED,
                        severity=Severity.WARNING,
                        file_path=record.path,
                        score=brightness,
                        threshold=dark_max,
                        message=(
                            f"Image is underexposed (mean brightness {brightness:.1f} "
                            f"< threshold {dark_max:.1f})."
                        ),
                        metadata={"mean_brightness": brightness},
                    )
                )
            elif brightness > bright_min:
                findings.append(
                    Finding(
                        issue_type=IssueType.OVEREXPOSED,
                        severity=Severity.WARNING,
                        file_path=record.path,
                        score=brightness,
                        threshold=bright_min,
                        message=(
                            f"Image is overexposed (mean brightness {brightness:.1f} "
                            f"> threshold {bright_min:.1f})."
                        ),
                        metadata={"mean_brightness": brightness},
                    )
                )

        return findings
