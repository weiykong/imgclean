"""Load and merge configuration from YAML/JSON files and CLI overrides."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from imgclean.config.schema import Config


def load_config(path: Path | str | None = None, overrides: dict[str, Any] | None = None) -> Config:
    """
    Load configuration from an optional YAML or JSON file, then apply overrides.

    Priority (highest to lowest):
      1. ``overrides`` dict (typically from CLI flags)
      2. Config file at ``path``
      3. Built-in defaults
    """
    raw: dict[str, Any] = {}

    if path is not None:
        raw = _load_file(Path(path))

    if overrides:
        raw = _deep_merge(raw, overrides)

    return Config.model_validate(raw)


def _load_file(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    text = path.read_text(encoding="utf-8")
    suffix = path.suffix.lower()

    if suffix in {".yaml", ".yml"}:
        return yaml.safe_load(text) or {}
    if suffix == ".json":
        return json.loads(text)

    raise ValueError(f"Unsupported config format: {path.suffix!r}. Use .yaml or .json")


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Recursively merge override into base, returning a new dict."""
    result = dict(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result
