"""Pydantic configuration schema with validation and defaults."""

from __future__ import annotations

from pydantic import BaseModel, Field, model_validator

from imgclean.config import defaults as D


class DatasetConfig(BaseModel):
    path: str = "."
    recursive: bool = True
    splits: dict[str, str] = Field(default_factory=dict)  # name -> path


class ChecksConfig(BaseModel):
    corruption: bool = True
    resolution: bool = True
    aspect_ratio: bool = True
    blur: bool = True
    exposure: bool = True
    exact_duplicates: bool = True
    perceptual_duplicates: bool = True
    embedding_duplicates: bool = False
    split_leakage: bool = True
    outliers: bool = False


class ThresholdsConfig(BaseModel):
    min_width: int = D.MIN_WIDTH
    min_height: int = D.MIN_HEIGHT
    aspect_ratio_min: float = D.ASPECT_RATIO_MIN
    aspect_ratio_max: float = D.ASPECT_RATIO_MAX
    blur_laplacian_min: float = D.BLUR_LAPLACIAN_MIN
    exposure_dark_max: float = D.EXPOSURE_DARK_MAX
    exposure_bright_min: float = D.EXPOSURE_BRIGHT_MIN
    phash_hamming_max: int = D.PHASH_HAMMING_MAX
    embedding_similarity_min: float = D.EMBEDDING_SIMILARITY_MIN
    outlier_knn_k: int = D.OUTLIER_KNN_K
    outlier_distance_percentile: float = D.OUTLIER_DISTANCE_PERCENTILE

    @model_validator(mode="after")
    def validate_exposure(self) -> "ThresholdsConfig":
        if self.exposure_dark_max >= self.exposure_bright_min:
            raise ValueError(
                "exposure_dark_max must be less than exposure_bright_min"
            )
        return self


class ReportConfig(BaseModel):
    html: bool = True
    json_report: bool = True
    csv_report: bool = True
    output_dir: str = "."
    open_browser: bool = False


class ActionsConfig(BaseModel):
    quarantine: bool = False
    quarantine_dir: str = "quarantine"
    keep_representative: bool = False
    dry_run: bool = True


class ParallelConfig(BaseModel):
    max_workers: int | None = D.MAX_WORKERS


class CacheConfig(BaseModel):
    enabled: bool = D.CACHE_ENABLED
    dir_name: str = D.CACHE_DIR_NAME


class Config(BaseModel):
    dataset: DatasetConfig = Field(default_factory=DatasetConfig)
    checks: ChecksConfig = Field(default_factory=ChecksConfig)
    thresholds: ThresholdsConfig = Field(default_factory=ThresholdsConfig)
    report: ReportConfig = Field(default_factory=ReportConfig)
    actions: ActionsConfig = Field(default_factory=ActionsConfig)
    parallel: ParallelConfig = Field(default_factory=ParallelConfig)
    cache: CacheConfig = Field(default_factory=CacheConfig)
