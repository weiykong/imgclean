"""Serialize a ScanReport to CSV (one row per finding)."""

from __future__ import annotations

import csv
from pathlib import Path

from imgclean.models.report import ScanReport

_FIELDS = [
    "issue_type",
    "severity",
    "file_path",
    "message",
    "score",
    "threshold",
    "group_id",
    "related_files",
]


def write_csv(report: ScanReport, output: Path) -> None:
    with output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=_FIELDS, extrasaction="ignore")
        writer.writeheader()
        for finding in report.findings:
            row = finding.as_dict()
            row["related_files"] = "|".join(row["related_files"])
            writer.writerow(row)
