"""
Public Python API for imgclean.

Usage example::

    from imgclean import scan_dataset

    report = scan_dataset(
        path="./dataset",
        checks=["blur", "duplicates", "corruption"],
    )
    print(report.summary.findings_count)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from imgclean.config.loader import load_config
from imgclean.core.orchestrator import run_scan
from imgclean.models.report import ScanReport


def scan_dataset(
    path: str | Path,
    *,
    config_file: str | Path | None = None,
    checks: list[str] | None = None,
    thresholds: dict[str, Any] | None = None,
    splits: dict[str, str | Path] | None = None,
    cache: bool = True,
    verbose: bool = False,
) -> ScanReport:
    """
    Scan an image dataset and return a :class:`~imgclean.models.report.ScanReport`.

    Args:
        path: Root directory of the dataset.
        config_file: Optional path to a YAML/JSON config file.
        checks: List of check names to enable.  When provided, all other checks
                are disabled.  Available names: corruption, resolution,
                aspect_ratio, blur, exposure, exact_duplicates,
                perceptual_duplicates, embedding_duplicates,
                split_leakage, outliers.
        thresholds: Override specific threshold values.
        splits: Mapping of split_name -> directory for leakage detection.
                When provided, ``path`` is used only as the scan root.
        cache: Enable feature caching (default True).
        verbose: Enable debug-level logging.

    Returns:
        A :class:`~imgclean.models.report.ScanReport`.
    """
    if verbose:
        from imgclean.utils.logging import configure_logging
        configure_logging(verbose=True)

    overrides: dict[str, Any] = {
        "dataset": {"path": str(path)},
        "cache": {"enabled": cache},
        # Disable report outputs when using the Python API
        "report": {"html": False, "json_report": False, "csv_report": False},
    }

    if checks is not None:
        from imgclean.core.registry import all_check_names
        checks_override = {name: False for name in all_check_names()}
        for name in checks:
            # Accept shorthand like "duplicates" → enable both exact + perceptual
            if name == "duplicates":
                checks_override["exact_duplicates"] = True
                checks_override["perceptual_duplicates"] = True
            else:
                checks_override[name] = True
        overrides["checks"] = checks_override

    if thresholds:
        overrides["thresholds"] = thresholds

    config = load_config(config_file, overrides=overrides)

    root = Path(path).resolve()
    split_map: dict[str, Path] | None = None
    if splits:
        split_map = {name: Path(d).resolve() for name, d in splits.items()}

    return run_scan(paths=[root], config=config, split_map=split_map)
