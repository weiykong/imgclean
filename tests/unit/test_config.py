"""Tests for config loading and validation."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from imgclean.config.loader import load_config
from imgclean.config.schema import Config, ThresholdsConfig


class TestLoadConfig:
    def test_defaults_when_no_file(self) -> None:
        cfg = load_config()
        assert isinstance(cfg, Config)
        assert cfg.thresholds.min_width == 32

    def test_overrides_applied(self) -> None:
        cfg = load_config(overrides={"thresholds": {"min_width": 512}})
        assert cfg.thresholds.min_width == 512

    def test_yaml_file_loaded(self, tmp_path: Path) -> None:
        config_path = tmp_path / "config.yaml"
        config_path.write_text(
            yaml.dump({"thresholds": {"min_width": 128, "min_height": 128}}),
            encoding="utf-8",
        )
        cfg = load_config(config_path)
        assert cfg.thresholds.min_width == 128

    def test_overrides_win_over_file(self, tmp_path: Path) -> None:
        config_path = tmp_path / "config.yaml"
        config_path.write_text(
            yaml.dump({"thresholds": {"min_width": 128}}),
            encoding="utf-8",
        )
        cfg = load_config(config_path, overrides={"thresholds": {"min_width": 999}})
        assert cfg.thresholds.min_width == 999

    def test_file_not_found_raises(self) -> None:
        with pytest.raises(FileNotFoundError):
            load_config(Path("/nonexistent/config.yaml"))

    def test_unsupported_format_raises(self, tmp_path: Path) -> None:
        bad = tmp_path / "config.toml"
        bad.write_text("[settings]", encoding="utf-8")
        with pytest.raises(ValueError, match="Unsupported config format"):
            load_config(bad)


class TestThresholdsValidation:
    def test_valid_thresholds(self) -> None:
        t = ThresholdsConfig(exposure_dark_max=20, exposure_bright_min=220)
        assert t.exposure_dark_max == 20

    def test_invalid_exposure_order_raises(self) -> None:
        with pytest.raises(ValueError):
            ThresholdsConfig(exposure_dark_max=200, exposure_bright_min=100)
