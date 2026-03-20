"""CLI sub-command: quarantine — move flagged files to a review folder."""

from __future__ import annotations

from pathlib import Path

import typer

from imgclean.actions.quarantine import quarantine_findings
from imgclean.cli._common import parse_issue_filter
from imgclean.config.loader import load_config
from imgclean.core.orchestrator import run_scan
from imgclean.utils.logging import configure_logging, log

app = typer.Typer(help="Move flagged images to a quarantine folder.")


@app.callback(invoke_without_command=True)
def quarantine(
    path: Path = typer.Argument(..., help="Dataset directory."),
    issues: str | None = typer.Option(
        None, "--issues", "-i",
        help="Comma-separated issue types to quarantine (e.g. corrupted,blurry). "
             "Defaults to all ERROR-severity findings.",
    ),
    out: Path = typer.Option(
        Path("quarantine"), "--out", "-o", help="Quarantine destination directory."
    ),
    execute: bool = typer.Option(
        False, "--execute", help="Actually move files (default is dry-run)."
    ),
    config_file: Path | None = typer.Option(None, "--config", "-c"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
) -> None:
    configure_logging(verbose)

    config = load_config(config_file, overrides={"dataset": {"path": str(path)}})
    report = run_scan(paths=[path.resolve()], config=config)

    dry_run = not execute

    moved = quarantine_findings(
        findings=report.findings,
        quarantine_dir=out.resolve(),
        issue_filter=parse_issue_filter(issues),
        root=path.resolve(),
        dry_run=dry_run,
    )

    if dry_run:
        log.info(
            f"[DRY-RUN] Would quarantine {len(moved)} file(s). "
            "Pass --execute to perform the operation."
        )
    else:
        log.info(f"Quarantined {len(moved)} file(s) to {out.resolve()}")
