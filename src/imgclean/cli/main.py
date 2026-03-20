"""Main CLI entry-point. Registers all sub-commands."""

from __future__ import annotations

import typer

from imgclean.cli.clean import app as clean_app
from imgclean.cli.dedup import app as dedup_app
from imgclean.cli.leakage import app as leakage_app
from imgclean.cli.quality import app as quality_app
from imgclean.cli.quarantine_cmd import app as quarantine_app
from imgclean.cli.report_cmd import app as report_app
from imgclean.cli.scan import app as scan_app

app = typer.Typer(
    name="imgclean",
    help="Audit and clean image datasets before training, labeling, or sharing.",
    no_args_is_help=True,
    rich_markup_mode="rich",
)

app.add_typer(scan_app, name="scan")
app.add_typer(dedup_app, name="dedup")
app.add_typer(clean_app, name="clean")
app.add_typer(leakage_app, name="leakage")
app.add_typer(quality_app, name="quality")
app.add_typer(quarantine_app, name="quarantine")
app.add_typer(report_app, name="report")


@app.command("version")
def version() -> None:
    """Print the imgclean version."""
    from importlib.metadata import version as pkg_version

    typer.echo(f"imgclean {pkg_version('imgclean')}")


if __name__ == "__main__":
    app()
