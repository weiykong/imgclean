"""CLI sub-command: clean — scan and quarantine flagged files in one step."""

from __future__ import annotations

from pathlib import Path

import typer

from imgclean.actions.quarantine import quarantine_findings
from imgclean.cli._common import (
    add_optional_workers_override,
    parse_issue_filter,
    print_summary,
    write_reports,
)
from imgclean.config.loader import load_config
from imgclean.core.orchestrator import run_scan
from imgclean.utils.logging import configure_logging, log

app = typer.Typer(help="Scan a dataset and quarantine flagged files in one command.")


@app.callback(invoke_without_command=True)
def clean(
    path: Path = typer.Argument(..., help="Dataset directory."),
    issues: str | None = typer.Option(
        None,
        "--issues",
        "-i",
        help="Comma-separated issue types to quarantine. Defaults to all ERROR findings.",
    ),
    out: Path = typer.Option(
        Path("quarantine"),
        "--out",
        "-o",
        help="Quarantine destination directory.",
    ),
    execute: bool = typer.Option(
        False,
        "--execute",
        help="Actually move files (default is dry-run).",
    ),
    config_file: Path | None = typer.Option(None, "--config", "-c"),
    report_dir: Path | None = typer.Option(
        None,
        "--report-dir",
        help="Directory for output reports (default: cwd).",
    ),
    workers: int | None = typer.Option(
        None,
        "--workers",
        "-w",
        min=1,
        help="Maximum number of worker threads for image scanning.",
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
) -> None:
    configure_logging(verbose)

    overrides = add_optional_workers_override(
        {
            "dataset": {"path": str(path)},
            "report": {"output_dir": str(report_dir or Path.cwd())},
        },
        workers,
    )
    config = load_config(config_file, overrides=overrides)

    report = run_scan(paths=[path.resolve()], config=config)
    print_summary(report)
    write_reports(report, Path(config.report.output_dir), config.report)

    moved = quarantine_findings(
        findings=report.findings,
        quarantine_dir=out.resolve(),
        issue_filter=parse_issue_filter(issues),
        root=path.resolve(),
        dry_run=not execute,
    )

    if execute:
        log.info(f"Quarantined {len(moved)} file(s) to {out.resolve()}")
    else:
        log.info(
            f"[DRY-RUN] Would quarantine {len(moved)} file(s). "
            "Pass --execute to perform the operation."
        )
