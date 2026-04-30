"""CLI sub-command: dedup — duplicate and near-duplicate detection."""

from __future__ import annotations

from pathlib import Path
import typer

from imgclean.cli._common import add_optional_workers_override, print_summary, write_reports
from imgclean.config.loader import load_config
from imgclean.core.orchestrator import run_scan
from imgclean.utils.logging import configure_logging

app = typer.Typer(help="Find exact and near-duplicate images.")


@app.callback(invoke_without_command=True)
def dedup(
    path: Path = typer.Argument(..., help="Dataset directory to check."),
    method: str = typer.Option(
        "phash",
        "--method",
        "-m",
        help="Duplicate method: phash for visual matches, sha256 for byte-identical files.",
    ),
    threshold: int = typer.Option(
        8,
        "--threshold",
        "-t",
        help="Max Hamming distance for near-duplicates.",
    ),
    config_file: Path | None = typer.Option(None, "--config", "-c"),
    report_dir: Path | None = typer.Option(None, "--report-dir", "-o"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
    workers: int | None = typer.Option(
        None,
        "--workers",
        "-w",
        min=1,
        help="Maximum number of worker threads for image scanning.",
    ),
) -> None:
    configure_logging(verbose)

    method = method.lower()
    if method not in {"phash", "sha256"}:
        raise typer.BadParameter(
            "method must be one of: phash, sha256",
            param_hint="--method",
        )

    overrides = add_optional_workers_override(
        {
            "dataset": {"path": str(path)},
            "checks": {
                "corruption": False,
                "resolution": False,
                "aspect_ratio": False,
                "blur": False,
                "exposure": False,
                "exact_duplicates": True,
                "perceptual_duplicates": method == "phash",
                "embedding_duplicates": False,
                "split_leakage": False,
                "outliers": False,
            },
            "thresholds": {"phash_hamming_max": threshold},
            "report": {"output_dir": str(report_dir or Path.cwd())},
        },
        workers,
    )
    config = load_config(config_file, overrides=overrides)

    report = run_scan(paths=[path.resolve()], config=config)
    print_summary(report)
    write_reports(report, Path(config.report.output_dir), config.report)
