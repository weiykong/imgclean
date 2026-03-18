"""Serialize a ScanReport to JSON."""

from __future__ import annotations

import json
from pathlib import Path

from imgclean.models.report import ScanReport


def write_json(report: ScanReport, output: Path) -> None:
    data = report.as_dict()
    output.write_text(json.dumps(data, indent=2), encoding="utf-8")
