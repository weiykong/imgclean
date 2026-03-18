from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from imgclean.models.issue_types import IssueType, Severity


@dataclass
class Finding:
    """A single detected issue for one or more image files."""

    issue_type: IssueType
    severity: Severity
    file_path: Path
    message: str
    score: float | None = None       # e.g. Laplacian variance, hamming distance
    threshold: float | None = None   # threshold that triggered this finding
    related_files: list[Path] = field(default_factory=list)  # e.g. duplicate partners
    group_id: str | None = None      # cluster / duplicate group identifier
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "issue_type": self.issue_type.value,
            "severity": self.severity.value,
            "file_path": str(self.file_path),
            "message": self.message,
            "score": self.score,
            "threshold": self.threshold,
            "related_files": [str(p) for p in self.related_files],
            "group_id": self.group_id,
            "metadata": self.metadata,
        }
