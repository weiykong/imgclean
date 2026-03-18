"""CLI sub-command: leakage — train/val/test contamination detection."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from imgclean.cli._common import print_summary, write_reports
from imgclean.config.loader import load_config
from imgclean.core.orchestrator import run_scan
from imgclean.utils.logging import configure_logging

app = typer.Typer(help="Detect data leakage across dataset splits.")


@app.callback(invoke_without_command=True)
def leakage(
    train: Path = typer.Argument(..., help="Train split directory."),
    val: Optional[Path] = typer.Argument(None, help="Validation split directory."),
    test: Optional[Path] = typer.Argument(None, help="Test split directory."),
    config_file: Optional[Path] = typer.Option(None, "--config", "-c"),
    report_dir: Optional[Path] = typer.Option(None, "--report-dir", "-o"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
) -> None:
    configure_logging(verbose)

    split_map: dict[str, Path] = {"train": train.resolve()}
    if val:
        split_map["val"] = val.resolve()
    if test:
        split_map["test"] = test.resolve()

    if len(split_map) < 2:
        typer.echo("Provide at least two split directories.", err=True)
        raise typer.Exit(1)

    config = load_config(
        config_file,
        overrides={
            "checks": {
                "corruption": False,
                "resolution": False,
                "aspect_ratio": False,
                "blur": False,
                "exposure": False,
                "exact_duplicates": False,
                "perceptual_duplicates": False,
                "embedding_duplicates": False,
                "split_leakage": True,
                "outliers": False,
            },
            "report": {"output_dir": str(report_dir or Path.cwd())},
        },
    )

    report = run_scan(paths=[train.resolve()], config=config, split_map=split_map)
    print_summary(report)
    write_reports(report, Path(config.report.output_dir), config.report)
