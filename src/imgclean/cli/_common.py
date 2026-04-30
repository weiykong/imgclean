"""Shared CLI helpers: report writing, summary printing."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import typer
from rich.console import Console
from rich.table import Table

from imgclean.models.issue_types import IssueType
from imgclean.models.report import ScanReport
from imgclean.reports import write_csv, write_html, write_json
from imgclean.utils.logging import log

console = Console()


def add_optional_workers_override(
    overrides: dict[str, Any],
    workers: int | None,
) -> dict[str, Any]:
    if workers is not None:
        overrides["parallel"] = {"max_workers": workers}
    return overrides


def parse_issue_filter(issues: str | None) -> list[str] | None:
    if issues is None:
        return None

    parsed = [issue.strip() for issue in issues.split(",") if issue.strip()]
    valid_issue_types = {issue.value for issue in IssueType}
    invalid = sorted(set(parsed) - valid_issue_types)
    if invalid:
        valid = ", ".join(sorted(valid_issue_types))
        raise typer.BadParameter(
            f"unknown issue type(s): {', '.join(invalid)}. Valid issue types: {valid}",
            param_hint="--issues",
        )

    return parsed or None


def write_reports(report: ScanReport, output_dir: Path, cfg_report) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    if cfg_report.json_report:
        out = output_dir / "imgclean_report.json"
        write_json(report, out)
        log.info(f"JSON report → {out}")

    if cfg_report.csv_report:
        out = output_dir / "imgclean_report.csv"
        write_csv(report, out)
        log.info(f"CSV report  → {out}")

    if cfg_report.html:
        out = output_dir / "imgclean_report.html"
        write_html(report, out, open_browser=cfg_report.open_browser)
        log.info(f"HTML report → {out}")


def print_summary(report: ScanReport) -> None:
    s = report.summary
    table = Table(title="Scan Summary", show_header=True, header_style="bold")
    table.add_column("Metric", style="dim")
    table.add_column("Value", justify="right")

    table.add_row("Total files", str(s.total_files))
    table.add_row("Scanned OK", str(s.scanned_files))
    table.add_row("Corrupted", str(s.corrupted_files))
    table.add_row("Total findings", str(s.findings_count))

    for issue, count in sorted(s.issue_counts.items()):
        table.add_row(f"  ↳ {issue.replace('_', ' ')}", str(count))

    console.print(table)
