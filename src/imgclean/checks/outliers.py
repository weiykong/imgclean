"""Detect visual outliers using embedding-based kNN distance."""

from __future__ import annotations

from imgclean.checks.base import BaseCheck
from imgclean.models.dataset import Dataset
from imgclean.models.finding import Finding
from imgclean.models.issue_types import IssueType, Severity
from imgclean.utils.thresholds import percentile


class OutliersCheck(BaseCheck):
    name = "outliers"
    description = (
        "Detect visually isolated images using embedding-based kNN distance. "
        "Requires the [embeddings] optional dependency group."
    )

    def run(self, dataset: Dataset) -> list[Finding]:
        try:
            import numpy as np
            from imgclean.features.embeddings import embed_image
            from imgclean.io.image_loader import load_image
        except ImportError as exc:
            raise RuntimeError(
                "outliers check requires optional dependencies. "
                "Install with: pip install imgclean[embeddings]"
            ) from exc

        k = self.thresholds.outlier_knn_k
        dist_percentile = self.thresholds.outlier_distance_percentile
        valid = dataset.valid()

        embeddings = []
        records = []
        for record in valid:
            result = load_image(record.path)
            if result.is_corrupted or result.image is None:
                continue
            emb = embed_image(result.image)
            embeddings.append(emb)
            records.append(record)

        if len(records) < k + 1:
            return []

        matrix = np.stack(embeddings)

        # Pairwise cosine similarity (dot product of normalised vectors)
        sim_matrix = matrix @ matrix.T
        knn_distances: list[float] = []

        for i in range(len(records)):
            sims = sim_matrix[i].copy()
            sims[i] = -1.0  # exclude self
            top_k = np.sort(sims)[::-1][:k]
            knn_distances.append(float(1.0 - top_k.mean()))  # convert to distance

        cutoff = percentile(knn_distances, dist_percentile)

        findings: list[Finding] = []
        for record, dist in zip(records, knn_distances):
            if dist >= cutoff:
                findings.append(
                    Finding(
                        issue_type=IssueType.OUTLIER,
                        severity=Severity.INFO,
                        file_path=record.path,
                        score=dist,
                        threshold=cutoff,
                        message=(
                            f"Visual outlier: mean kNN distance {dist:.4f} "
                            f"≥ {dist_percentile:.0f}th-percentile cutoff {cutoff:.4f}."
                        ),
                        metadata={"knn_distance": dist, "k": k},
                    )
                )

        return findings
