"""Detect blurry images using Laplacian variance."""

from __future__ import annotations

from imgclean.checks.base import BaseCheck
from imgclean.features.quality import laplacian_variance
from imgclean.models.dataset import Dataset
from imgclean.models.finding import Finding
from imgclean.models.issue_types import IssueType, Severity


class BlurCheck(BaseCheck):
    name = "blur"
    description = "Flag images that appear blurry based on Laplacian variance."

    def run(self, dataset: Dataset) -> list[Finding]:
        from imgclean.io.image_loader import load_image

        findings: list[Finding] = []
        threshold = self.thresholds.blur_laplacian_min

        for record in dataset.valid():
            result = load_image(record.path)
            if result.is_corrupted or result.image is None:
                continue

            score = laplacian_variance(result.image)

            if score < threshold:
                findings.append(
                    Finding(
                        issue_type=IssueType.BLURRY,
                        severity=Severity.WARNING,
                        file_path=record.path,
                        score=score,
                        threshold=threshold,
                        message=(
                            f"Image appears blurry (Laplacian variance {score:.1f} "
                            f"< threshold {threshold:.1f})."
                        ),
                        metadata={"laplacian_variance": score},
                    )
                )

        return findings
