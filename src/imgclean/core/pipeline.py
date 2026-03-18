"""Define the check execution order and dependency rules."""

from __future__ import annotations

from imgclean.checks.base import BaseCheck
from imgclean.models.dataset import Dataset
from imgclean.models.finding import Finding
from imgclean.utils.logging import log
from imgclean.utils.timing import timer, format_duration


def run_pipeline(checks: list[BaseCheck], dataset: Dataset) -> list[Finding]:
    """
    Execute each check in order and collect all findings.

    Checks are independent of each other; each receives the full dataset.
    """
    all_findings: list[Finding] = []

    for check in checks:
        log.info(f"Running check: [bold]{check.name}[/bold] …")
        with timer() as elapsed:
            try:
                findings = check.run(dataset)
            except Exception as exc:  # noqa: BLE001
                log.warning(f"Check [bold]{check.name}[/bold] failed: {exc}")
                findings = []

        count = len(findings)
        duration = format_duration(elapsed[0])
        if count:
            log.info(
                f"  → [yellow]{count}[/yellow] finding(s) in {duration}"
            )
        else:
            log.info(f"  → [green]OK[/green] ({duration})")

        all_findings.extend(findings)

    return all_findings
