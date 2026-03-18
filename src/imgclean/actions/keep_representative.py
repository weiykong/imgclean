"""
For each duplicate cluster, select one representative to keep
and return the rest as candidates for removal or quarantine.
"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from imgclean.models.finding import Finding
from imgclean.models.issue_types import IssueType


_DUPLICATE_TYPES = {
    IssueType.EXACT_DUPLICATE,
    IssueType.NEAR_DUPLICATE,
    IssueType.EMBEDDING_DUPLICATE,
}


def select_representatives(
    findings: list[Finding],
) -> dict[str, dict[str, list[Path]]]:
    """
    For each duplicate cluster, pick one representative (the lexicographically
    first path) and return a mapping of:

        { group_id: { "keep": [path], "remove": [path, ...] } }
    """
    clusters: dict[str, set[Path]] = defaultdict(set)

    for f in findings:
        if f.issue_type not in _DUPLICATE_TYPES:
            continue
        if f.group_id is None:
            continue
        clusters[f.group_id].add(f.file_path)
        clusters[f.group_id].update(f.related_files)

    result: dict[str, dict[str, list[Path]]] = {}
    for group_id, paths in clusters.items():
        sorted_paths = sorted(paths)
        result[group_id] = {
            "keep": [sorted_paths[0]],
            "remove": sorted_paths[1:],
        }

    return result


def get_removal_candidates(findings: list[Finding]) -> list[Path]:
    """Return the flat list of files to remove (all but the representative)."""
    reps = select_representatives(findings)
    candidates: list[Path] = []
    for group in reps.values():
        candidates.extend(group["remove"])
    return candidates
