"""CLI tests for worker flag overrides."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from imgclean.cli.main import app
from imgclean.config.schema import Config
from imgclean.models.report import ReportSummary, ScanReport


runner = CliRunner()


def _report() -> ScanReport:
    return ScanReport(
        summary=ReportSummary(
            total_files=0,
            scanned_files=0,
            corrupted_files=0,
            findings_count=0,
            issue_counts={},
            scan_root=".",
            duration_seconds=0.0,
        ),
        findings=[],
    )


def test_scan_workers_flag_overrides_config(monkeypatch, tmp_path: Path) -> None:
    captured: dict[str, object] = {}

    def fake_load_config(path, overrides):
        captured["overrides"] = overrides
        return Config.model_validate(overrides)

    monkeypatch.setattr("imgclean.cli.scan.configure_logging", lambda verbose: None)
    monkeypatch.setattr("imgclean.cli.scan.load_config", fake_load_config)
    monkeypatch.setattr("imgclean.cli.scan.run_scan", lambda paths, config: _report())
    monkeypatch.setattr("imgclean.cli.scan.print_summary", lambda report: None)
    monkeypatch.setattr(
        "imgclean.cli.scan.write_reports",
        lambda report, output_dir, cfg_report: None,
    )

    result = runner.invoke(app, ["scan", "--workers", "4", str(tmp_path)])

    assert result.exit_code == 0
    assert captured["overrides"]["parallel"]["max_workers"] == 4
