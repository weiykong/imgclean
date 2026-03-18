"""Render a ScanReport as an HTML file using Jinja2."""

from __future__ import annotations

import webbrowser
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from imgclean.models.report import ScanReport
from imgclean.utils.timing import format_duration

_TEMPLATES_DIR = Path(__file__).parent / "templates"


def write_html(report: ScanReport, output: Path, open_browser: bool = False) -> None:
    env = Environment(
        loader=FileSystemLoader(str(_TEMPLATES_DIR)),
        autoescape=select_autoescape(["html"]),
    )

    # Build a findings dict that Jinja can iterate (Finding objects not dicts)
    findings_by_type: dict[str, list] = {}
    for f in report.findings:
        findings_by_type.setdefault(f.issue_type.value, []).append(_finding_ctx(f))

    duration = (
        format_duration(report.summary.duration_seconds)
        if report.summary.duration_seconds is not None
        else "—"
    )

    template = env.get_template("report.html.j2")
    html = template.render(
        summary=report.summary,
        findings_by_type=findings_by_type,
        duration=duration,
    )

    output.write_text(html, encoding="utf-8")

    if open_browser:
        webbrowser.open(output.as_uri())


def _finding_ctx(finding) -> dict:
    """Convert a Finding to a simple dict for the template."""
    return {
        "issue_type": finding.issue_type.value,
        "severity": finding.severity.value,
        "file_path": str(finding.file_path),
        "message": finding.message,
        "score": finding.score,
        "threshold": finding.threshold,
        "related_files": [str(p) for p in finding.related_files],
        "group_id": finding.group_id,
        "metadata": finding.metadata,
    }
