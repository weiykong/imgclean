"""CLI sub-command: scan — full dataset audit."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from imgclean.cli._common import add_optional_workers_override, print_summary, write_reports
from imgclean.config.loader import load_config
from imgclean.core.orchestrator import run_scan
from imgclean.utils.logging import configure_logging

app = typer.Typer(help="Run a full dataset audit.")


@app.callback(invoke_without_command=True)
def scan(
    path: Path = typer.Argument(..., help="Dataset directory to scan."),
    config_file: Optional[Path] = typer.Option(
        None, "--config", "-c", help="Path to YAML/JSON config file."
    ),
    report_dir: Optional[Path] = typer.Option(
        None, "--report-dir", "-o", help="Directory for output reports (default: cwd)."
    ),
    no_html: bool = typer.Option(False, "--no-html", help="Skip HTML report."),
    no_json: bool = typer.Option(False, "--no-json", help="Skip JSON report."),
    no_csv: bool = typer.Option(False, "--no-csv", help="Skip CSV report."),
    open_browser: bool = typer.Option(False, "--open", help="Open HTML report in browser."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose logging."),
    no_cache: bool = typer.Option(False, "--no-cache", help="Disable feature cache."),
    workers: Optional[int] = typer.Option(
        None,
        "--workers",
        "-w",
        min=1,
        help="Maximum number of worker threads for image scanning.",
    ),
) -> None:
    configure_logging(verbose)

    overrides = add_optional_workers_override(
        {
            "dataset": {"path": str(path)},
            "report": {
                "html": not no_html,
                "json_report": not no_json,
                "csv_report": not no_csv,
                "output_dir": str(report_dir or Path.cwd()),
                "open_browser": open_browser,
            },
            "cache": {"enabled": not no_cache},
        },
        workers,
    )
    config = load_config(config_file, overrides=overrides)

    report = run_scan(paths=[path.resolve()], config=config)

    print_summary(report)
    write_reports(report, Path(config.report.output_dir), config.report)
