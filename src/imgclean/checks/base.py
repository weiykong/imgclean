"""Abstract base class for all imgclean checks."""

from __future__ import annotations

from abc import ABC, abstractmethod

from imgclean.config.schema import Config
from imgclean.models.dataset import Dataset
from imgclean.models.finding import Finding


class BaseCheck(ABC):
    """
    Every check must subclass ``BaseCheck`` and implement ``run``.

    Checks receive the full dataset and config; they return a list of
    findings (possibly empty).
    """

    #: Machine-readable name used in config and reports.
    name: str

    #: Human-readable description shown in the CLI and HTML report.
    description: str = ""

    def __init__(self, config: Config) -> None:
        self.config = config
        self.thresholds = config.thresholds

    @abstractmethod
    def run(self, dataset: Dataset) -> list[Finding]:
        """Execute the check and return findings."""

    def is_enabled(self) -> bool:
        """Return whether this check is enabled in config."""
        return bool(getattr(self.config.checks, self.name, True))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r})"
