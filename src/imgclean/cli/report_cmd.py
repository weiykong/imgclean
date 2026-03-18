"""CLI sub-command: report — re-render an HTML report from a saved JSON result."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from imgclean.models.finding import Finding
from imgclean.models.issue_types import IssueType, Severity
from imgclean.models.report import ReportSummary, ScanReport
from imgclean.reports import write_html
from imgclean.utils.logging import log

app = typer.Typer(help="Re-render an HTML report from a saved JSON result.")


@app.callback(invoke_without_command=True)
def report(
    json_file: Path = typer.Argument(..., help="Path to imgclean_report.json"),
    output: Optional[Path] = typer.Option(None, "--html", help="Output HTML file path."),
    open_browser: bool = typer.Option(False, "--open", help="Open in browser after rendering."),
) -> None:
    if not json_file.exists():
        typer.echo(f"File not found: {json_file}", err=True)
        raise typer.Exit(1)

    data = json.loads(json_file.read_text(encoding="utf-8"))

    raw_summary = data["summary"]
    summary = ReportSummary(
        total_files=raw_summary["total_files"],
        scanned_files=raw_summary["scanned_files"],
        corrupted_files=raw_summary["corrupted_files"],
        findings_count=raw_summary["findings_count"],
        issue_counts=raw_summary["issue_counts"],
        scan_root=raw_summary["scan_root"],
        generated_at=raw_summary["generated_at"],
        duration_seconds=raw_summary.get("duration_seconds"),
    )

    findings: list[Finding] = []
    for f in data.get("findings", []):
        findings.append(
            Finding(
                issue_type=IssueType(f["issue_type"]),
                severity=Severity(f["severity"]),
                file_path=Path(f["file_path"]),
                message=f["message"],
                score=f.get("score"),
                threshold=f.get("threshold"),
                related_files=[Path(p) for p in f.get("related_files", [])],
                group_id=f.get("group_id"),
                metadata=f.get("metadata", {}),
            )
        )

    scan_report = ScanReport(summary=summary, findings=findings)
    html_out = output or json_file.with_suffix(".html")
    write_html(scan_report, html_out, open_browser=open_browser)
    log.info(f"HTML report written to {html_out}")
