"""CLI sub-command: quality — per-image quality checks."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from imgclean.cli._common import print_summary, write_reports
from imgclean.config.loader import load_config
from imgclean.core.orchestrator import run_scan
from imgclean.utils.logging import configure_logging

app = typer.Typer(help="Run quality-specific checks (blur, exposure, resolution).")


@app.callback(invoke_without_command=True)
def quality(
    path: Path = typer.Argument(..., help="Dataset directory."),
    blur: bool = typer.Option(True, "--blur/--no-blur", help="Check for blur."),
    exposure: bool = typer.Option(True, "--exposure/--no-exposure", help="Check exposure."),
    resolution: bool = typer.Option(True, "--resolution/--no-resolution", help="Check resolution."),
    config_file: Optional[Path] = typer.Option(None, "--config", "-c"),
    report_dir: Optional[Path] = typer.Option(None, "--report-dir", "-o"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
) -> None:
    configure_logging(verbose)

    config = load_config(
        config_file,
        overrides={
            "dataset": {"path": str(path)},
            "checks": {
                "corruption": True,
                "resolution": resolution,
                "aspect_ratio": True,
                "blur": blur,
                "exposure": exposure,
                "exact_duplicates": False,
                "perceptual_duplicates": False,
                "embedding_duplicates": False,
                "split_leakage": False,
                "outliers": False,
            },
            "report": {"output_dir": str(report_dir or Path.cwd())},
        },
    )

    report = run_scan(paths=[path.resolve()], config=config)
    print_summary(report)
    write_reports(report, Path(config.report.output_dir), config.report)
