"""Registry of all available checks, looked up by name."""

from __future__ import annotations

from typing import TYPE_CHECKING

from imgclean.checks.aspect_ratio import AspectRatioCheck
from imgclean.checks.base import BaseCheck
from imgclean.checks.blur import BlurCheck
from imgclean.checks.corruption import CorruptionCheck
from imgclean.checks.embedding_duplicates import EmbeddingDuplicatesCheck
from imgclean.checks.exact_duplicates import ExactDuplicatesCheck
from imgclean.checks.exposure import ExposureCheck
from imgclean.checks.outliers import OutliersCheck
from imgclean.checks.perceptual_duplicates import PerceptualDuplicatesCheck
from imgclean.checks.resolution import ResolutionCheck
from imgclean.checks.split_leakage import SplitLeakageCheck

if TYPE_CHECKING:
    from imgclean.config.schema import Config

# Ordered: cheaper / per-file checks first, group checks last.
_ALL_CHECKS: list[type[BaseCheck]] = [
    CorruptionCheck,
    ResolutionCheck,
    AspectRatioCheck,
    BlurCheck,
    ExposureCheck,
    ExactDuplicatesCheck,
    PerceptualDuplicatesCheck,
    EmbeddingDuplicatesCheck,
    SplitLeakageCheck,
    OutliersCheck,
]

_REGISTRY: dict[str, type[BaseCheck]] = {cls.name: cls for cls in _ALL_CHECKS}


def get_check(name: str) -> type[BaseCheck]:
    try:
        return _REGISTRY[name]
    except KeyError:
        raise ValueError(f"Unknown check: {name!r}. Available: {list(_REGISTRY)}")


def build_checks(config: "Config") -> list[BaseCheck]:
    """Instantiate and return all checks that are enabled in config."""
    instances: list[BaseCheck] = []
    for check_cls in _ALL_CHECKS:
        instance = check_cls(config)
        if instance.is_enabled():
            instances.append(instance)
    return instances


def all_check_names() -> list[str]:
    return list(_REGISTRY.keys())
