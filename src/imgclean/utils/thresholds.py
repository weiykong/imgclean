"""Helpers for applying thresholds and classifying values."""

from __future__ import annotations


def is_below(value: float, threshold: float) -> bool:
    return value < threshold


def is_above(value: float, threshold: float) -> bool:
    return value > threshold


def in_range(value: float, low: float, high: float) -> bool:
    return low <= value <= high


def percentile(values: list[float], p: float) -> float:
    """Return the p-th percentile of ``values`` (0 <= p <= 100)."""
    if not values:
        raise ValueError("Cannot compute percentile of an empty list")
    sorted_vals = sorted(values)
    idx = (len(sorted_vals) - 1) * p / 100
    lo, hi = int(idx), min(int(idx) + 1, len(sorted_vals) - 1)
    frac = idx - lo
    return sorted_vals[lo] + frac * (sorted_vals[hi] - sorted_vals[lo])
