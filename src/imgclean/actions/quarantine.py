"""Move flagged files to a quarantine folder for manual review."""

from __future__ import annotations

from pathlib import Path

from imgclean.actions.move import move_files
from imgclean.models.finding import Finding
from imgclean.models.issue_types import IssueType
from imgclean.utils.logging import log


def quarantine_findings(
    findings: list[Finding],
    quarantine_dir: Path,
    issue_filter: list[str] | None = None,
    root: Path | None = None,
    dry_run: bool = True,
) -> list[Path]:
    """
    Move files matching ``issue_filter`` to ``quarantine_dir``.

    Args:
        findings: All scan findings.
        quarantine_dir: Destination directory.
        issue_filter: List of issue type names to quarantine.  If None,
                      all ERROR-severity findings are quarantined.
        root: Source root for preserving relative paths.
        dry_run: When True, only log what would happen (no files moved).

    Returns:
        List of quarantined destination paths.
    """
    targets = _select_targets(findings, issue_filter)
    if not targets:
        log.info("No files selected for quarantine.")
        return []

    log.info(
        f"{'[DRY-RUN] ' if dry_run else ''}Quarantining "
        f"{len(targets)} file(s) to {quarantine_dir}"
    )
    return move_files(list(targets), quarantine_dir, root=root, dry_run=dry_run)


def _select_targets(
    findings: list[Finding],
    issue_filter: list[str] | None,
) -> set[Path]:
    if issue_filter is not None:
        allowed = {IssueType(name) for name in issue_filter}
        return {f.file_path for f in findings if f.issue_type in allowed}

    # Default: quarantine error-severity findings only
    from imgclean.models.issue_types import Severity
    return {f.file_path for f in findings if f.severity == Severity.ERROR}
