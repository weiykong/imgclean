"""Near-duplicate detection using CLIP embeddings (optional)."""

from __future__ import annotations

import uuid

from imgclean.checks.base import BaseCheck
from imgclean.models.dataset import Dataset
from imgclean.models.finding import Finding
from imgclean.models.issue_types import IssueType, Severity


class EmbeddingDuplicatesCheck(BaseCheck):
    name = "embedding_duplicates"
    description = (
        "Detect near-duplicates using CLIP image embeddings and cosine similarity. "
        "Requires the [embeddings] optional dependency group."
    )

    def run(self, dataset: Dataset) -> list[Finding]:
        try:
            import numpy as np
            from imgclean.features.embeddings import embed_image, cosine_similarity
            from imgclean.io.image_loader import load_image
        except ImportError as exc:
            raise RuntimeError(
                "embedding_duplicates check requires optional dependencies. "
                "Install with: pip install imgclean[embeddings]"
            ) from exc

        threshold = self.thresholds.embedding_similarity_min
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

        findings: list[Finding] = []
        n = len(records)
        paired: set[tuple[int, int]] = set()

        for i in range(n):
            for j in range(i + 1, n):
                sim = cosine_similarity(embeddings[i], embeddings[j])
                if sim >= threshold and (i, j) not in paired:
                    paired.add((i, j))
                    group_id = str(uuid.uuid4())[:8]
                    for rec, other in [(records[i], records[j]), (records[j], records[i])]:
                        findings.append(
                            Finding(
                                issue_type=IssueType.EMBEDDING_DUPLICATE,
                                severity=Severity.WARNING,
                                file_path=rec.path,
                                score=sim,
                                threshold=threshold,
                                message=(
                                    f"Embedding near-duplicate: cosine similarity "
                                    f"{sim:.3f} ≥ {threshold} with another image."
                                ),
                                related_files=[other.path],
                                group_id=group_id,
                                metadata={"cosine_similarity": sim},
                            )
                        )

        return findings
