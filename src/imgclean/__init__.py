"""
imgclean — Audit and clean image datasets before training, labeling, or sharing.

Quick start::

    from imgclean import scan_dataset

    report = scan_dataset("./my_dataset")
    print(f"Found {report.summary.findings_count} issue(s)")
"""

from imgclean.api.public import scan_dataset

__version__ = "0.1.0"

__all__ = ["scan_dataset", "__version__"]
