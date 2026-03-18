"""Tests for blur detection feature."""

from __future__ import annotations

from PIL import Image

from imgclean.features.quality import laplacian_variance


class TestLaplacianVariance:
    def test_blurry_image_low_variance(self, blurry_image: Image.Image) -> None:
        score = laplacian_variance(blurry_image)
        # A uniform grey image should have near-zero variance
        assert score < 5.0

    def test_sharp_image_high_variance(self, sharp_image: Image.Image) -> None:
        score = laplacian_variance(sharp_image)
        # A checkerboard should have high variance
        assert score > 100.0

    def test_returns_float(self, blurry_image: Image.Image) -> None:
        result = laplacian_variance(blurry_image)
        assert isinstance(result, float)

    def test_non_negative(self, sharp_image: Image.Image) -> None:
        assert laplacian_variance(sharp_image) >= 0.0
