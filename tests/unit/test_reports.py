"""Tests for report serialisation (JSON, CSV, HTML)."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from imgclean.models.finding import Finding
from imgclean.models.issue_types import IssueType, Severity
from imgclean.models.report import ReportSummary, ScanReport
from imgclean.reports.csv import write_csv
from imgclean.reports.html import write_html
from imgclean.reports.json import write_json


def _make_report(num_findings: int = 2) -> ScanReport:
    summary = ReportSummary(
        total_files=10,
        scanned_files=9,
        corrupted_files=1,
        findings_count=num_findings,
        issue_counts={"blurry": num_findings},
        scan_root="/tmp/dataset",
        duration_seconds=1.23,
    )
    findings = [
        Finding(
            issue_type=IssueType.BLURRY,
            severity=Severity.WARNING,
            file_path=Path(f"/tmp/dataset/img_{i}.jpg"),
            message=f"Image {i} is blurry",
            score=30.0,
            threshold=60.0,
        )
        for i in range(num_findings)
    ]
    return ScanReport(summary=summary, findings=findings)


class TestJsonReport:
    def test_writes_valid_json(self, tmp_path: Path) -> None:
        report = _make_report()
        out = tmp_path / "report.json"
        write_json(report, out)
        data = json.loads(out.read_text())
        assert "summary" in data
        assert "findings" in data

    def test_summary_fields_present(self, tmp_path: Path) -> None:
        report = _make_report()
        out = tmp_path / "report.json"
        write_json(report, out)
        data = json.loads(out.read_text())
        assert data["summary"]["total_files"] == 10
        assert data["summary"]["findings_count"] == 2

    def test_findings_count_matches(self, tmp_path: Path) -> None:
        report = _make_report(num_findings=3)
        out = tmp_path / "report.json"
        write_json(report, out)
        data = json.loads(out.read_text())
        assert len(data["findings"]) == 3


class TestCsvReport:
    def test_writes_valid_csv(self, tmp_path: Path) -> None:
        report = _make_report()
        out = tmp_path / "report.csv"
        write_csv(report, out)
        rows = list(csv.DictReader(out.open()))
        assert len(rows) == 2

    def test_csv_has_expected_columns(self, tmp_path: Path) -> None:
        report = _make_report(num_findings=1)
        out = tmp_path / "report.csv"
        write_csv(report, out)
        rows = list(csv.DictReader(out.open()))
        assert "issue_type" in rows[0]
        assert "file_path" in rows[0]
        assert "severity" in rows[0]

    def test_empty_findings_writes_header_only(self, tmp_path: Path) -> None:
        report = _make_report(num_findings=0)
        out = tmp_path / "report.csv"
        write_csv(report, out)
        rows = list(csv.DictReader(out.open()))
        assert len(rows) == 0


class TestHtmlReport:
    def test_writes_html_file(self, tmp_path: Path) -> None:
        report = _make_report()
        out = tmp_path / "report.html"
        write_html(report, out)
        assert out.exists()
        content = out.read_text()
        assert "<!DOCTYPE html>" in content

    def test_contains_summary_values(self, tmp_path: Path) -> None:
        report = _make_report()
        out = tmp_path / "report.html"
        write_html(report, out)
        content = out.read_text()
        assert "10" in content  # total_files

    def test_no_crash_on_zero_findings(self, tmp_path: Path) -> None:
        report = _make_report(num_findings=0)
        out = tmp_path / "report.html"
        write_html(report, out)
        assert out.exists()
