from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from imgclean.models.finding import Finding
from imgclean.models.issue_types import IssueType


@dataclass
class ReportSummary:
    """Aggregated statistics for a completed scan."""

    total_files: int
    scanned_files: int
    corrupted_files: int
    findings_count: int
    issue_counts: dict[str, int]
    scan_root: str
    generated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    duration_seconds: float | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "total_files": self.total_files,
            "scanned_files": self.scanned_files,
            "corrupted_files": self.corrupted_files,
            "findings_count": self.findings_count,
            "issue_counts": self.issue_counts,
            "scan_root": self.scan_root,
            "generated_at": self.generated_at,
            "duration_seconds": self.duration_seconds,
        }


@dataclass
class ScanReport:
    """Full output of a scan run: summary + all findings."""

    summary: ReportSummary
    findings: list[Finding] = field(default_factory=list)

    def findings_by_type(self) -> dict[str, list[Finding]]:
        result: dict[str, list[Finding]] = {}
        for f in self.findings:
            key = f.issue_type.value
            result.setdefault(key, []).append(f)
        return result

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary.as_dict(),
            "findings": [f.as_dict() for f in self.findings],
        }
