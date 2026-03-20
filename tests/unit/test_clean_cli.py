"""CLI tests for the clean command."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from imgclean.cli.main import app
from imgclean.models.finding import Finding
from imgclean.models.issue_types import IssueType, Severity
from imgclean.models.report import ReportSummary, ScanReport


runner = CliRunner()


def _report(*findings: Finding, root: Path) -> ScanReport:
    issue_counts: dict[str, int] = {}
    for finding in findings:
        key = finding.issue_type.value
        issue_counts[key] = issue_counts.get(key, 0) + 1

    return ScanReport(
        summary=ReportSummary(
            total_files=len(findings),
            scanned_files=len(findings),
            corrupted_files=sum(
                1 for finding in findings if finding.issue_type == IssueType.CORRUPTED
            ),
            findings_count=len(findings),
            issue_counts=issue_counts,
            scan_root=str(root),
            duration_seconds=0.1,
        ),
        findings=list(findings),
    )


def test_clean_dry_run_preserves_files_and_writes_reports(
    monkeypatch,
    tmp_path: Path,
) -> None:
    dataset = tmp_path / "dataset"
    report_dir = tmp_path / "reports"
    source = dataset / "broken.jpg"
    source.parent.mkdir(parents=True)
    source.write_bytes(b"broken")

    report = _report(
        Finding(
            issue_type=IssueType.CORRUPTED,
            severity=Severity.ERROR,
            file_path=source,
            message="Corrupted image.",
        ),
        root=dataset,
    )

    monkeypatch.setattr("imgclean.cli.clean.run_scan", lambda paths, config: report)

    result = runner.invoke(
        app,
        ["clean", "--report-dir", str(report_dir), str(dataset)],
    )

    assert result.exit_code == 0
    assert source.exists()
    assert not (tmp_path / "quarantine" / "broken.jpg").exists()
    assert (report_dir / "imgclean_report.html").exists()
    assert (report_dir / "imgclean_report.json").exists()
    assert (report_dir / "imgclean_report.csv").exists()


def test_clean_execute_moves_only_selected_issue_types(
    monkeypatch,
    tmp_path: Path,
) -> None:
    dataset = tmp_path / "dataset"
    quarantine_dir = tmp_path / "review"
    corrupted = dataset / "broken.jpg"
    blurry = dataset / "blurry.jpg"
    corrupted.parent.mkdir(parents=True)
    corrupted.write_bytes(b"broken")
    blurry.write_bytes(b"blurry")

    report = _report(
        Finding(
            issue_type=IssueType.CORRUPTED,
            severity=Severity.ERROR,
            file_path=corrupted,
            message="Corrupted image.",
        ),
        Finding(
            issue_type=IssueType.BLURRY,
            severity=Severity.WARNING,
            file_path=blurry,
            message="Blurry image.",
        ),
        root=dataset,
    )

    monkeypatch.setattr("imgclean.cli.clean.run_scan", lambda paths, config: report)

    result = runner.invoke(
        app,
        [
            "clean",
            "--issues",
            "corrupted",
            "--out",
            str(quarantine_dir),
            "--execute",
            str(dataset),
        ],
    )

    assert result.exit_code == 0
    assert not corrupted.exists()
    assert (quarantine_dir / "broken.jpg").exists()
    assert blurry.exists()
