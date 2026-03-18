"""Top-level orchestrator: ties scanning, pipeline, and reporting together."""

from __future__ import annotations

from pathlib import Path

from imgclean.config.schema import Config
from imgclean.core.pipeline import run_pipeline
from imgclean.core.registry import build_checks
from imgclean.core.scanner import scan_directory, scan_splits
from imgclean.models.finding import Finding
from imgclean.models.report import ReportSummary, ScanReport
from imgclean.utils.logging import log
from imgclean.utils.timing import timer, format_duration


def run_scan(
    paths: list[Path],
    config: Config,
    split_map: dict[str, Path] | None = None,
) -> ScanReport:
    """
    Orchestrate a full dataset scan.

    Args:
        paths: One or more root directories to scan (treated as a single dataset
               unless ``split_map`` is provided).
        config: Merged configuration object.
        split_map: Optional mapping of split_name -> directory.  When provided,
                   each directory is tagged with its split name for leakage detection.

    Returns:
        A :class:`ScanReport` containing the summary and all findings.
    """
    log.info("[bold]imgclean[/bold] — starting scan")

    with timer() as total_elapsed:
        dataset = _build_dataset(paths, config, split_map)
        checks = build_checks(config)

        if not checks:
            log.warning("No checks are enabled — nothing to run.")
            return _empty_report(dataset, config)

        log.info(
            f"Running [bold]{len(checks)}[/bold] check(s) "
            f"on [bold]{len(dataset)}[/bold] image(s)"
        )
        findings = run_pipeline(checks, dataset)

    summary = _build_summary(dataset, findings, paths, total_elapsed[0])
    log.info(
        f"Scan complete in [bold]{format_duration(total_elapsed[0])}[/bold]: "
        f"[yellow]{summary.findings_count}[/yellow] finding(s) across "
        f"[bold]{summary.scanned_files}[/bold] file(s)."
    )
    return ScanReport(summary=summary, findings=findings)


def _build_dataset(
    paths: list[Path],
    config: Config,
    split_map: dict[str, Path] | None,
) -> Dataset:
    if split_map:
        return scan_splits(split_map, config)

    if len(paths) == 1:
        return scan_directory(paths[0], config)

    # Multiple directories → merge into one dataset
    from imgclean.io.cache import FeatureCache

    cache = None
    if config.cache.enabled:
        cache_dir = paths[0] / config.cache.dir_name
        cache = FeatureCache(cache_dir)

    from imgclean.core.scanner import _build_records
    from imgclean.models.dataset import Dataset
    from imgclean.io.filesystem import discover_images

    all_records = []
    for root in paths:
        imgs = discover_images(root, recursive=config.dataset.recursive)
        records = _build_records(imgs, config, split=None, cache=cache)
        all_records.extend(records)

    if cache:
        cache.flush()

    return Dataset(records=all_records, root=paths[0])


def _build_summary(
    dataset: Dataset,
    findings: list[Finding],
    paths: list[Path],
    duration: float,
) -> ReportSummary:
    issue_counts: dict[str, int] = {}
    for f in findings:
        key = f.issue_type.value
        issue_counts[key] = issue_counts.get(key, 0) + 1

    return ReportSummary(
        total_files=len(dataset),
        scanned_files=len(dataset.valid()),
        corrupted_files=len(dataset.corrupted()),
        findings_count=len(findings),
        issue_counts=issue_counts,
        scan_root=str(paths[0]) if paths else ".",
        duration_seconds=duration,
    )


def _empty_report(dataset: Dataset, config: Config) -> ScanReport:
    summary = ReportSummary(
        total_files=len(dataset),
        scanned_files=len(dataset.valid()),
        corrupted_files=len(dataset.corrupted()),
        findings_count=0,
        issue_counts={},
        scan_root=config.dataset.path,
        duration_seconds=0.0,
    )
    return ScanReport(summary=summary)
