"""Default threshold and behaviour values for all checks."""

from __future__ import annotations

# ---- File integrity ----
SUPPORTED_EXTENSIONS: frozenset[str] = frozenset(
    {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff", ".tif", ".webp"}
)

# ---- Resolution ----
MIN_WIDTH: int = 32
MIN_HEIGHT: int = 32

# ---- Aspect ratio ----
ASPECT_RATIO_MIN: float = 0.1   # very tall / portrait extreme
ASPECT_RATIO_MAX: float = 10.0  # very wide / landscape extreme

# ---- Blur (Laplacian variance) ----
BLUR_LAPLACIAN_MIN: float = 60.0  # below this → blurry

# ---- Exposure (pixel intensity 0-255) ----
EXPOSURE_DARK_MAX: float = 25.0    # mean brightness below this → underexposed
EXPOSURE_BRIGHT_MIN: float = 230.0 # mean brightness above this → overexposed

# ---- Exact duplicates ----
HASH_ALGORITHM: str = "sha256"

# ---- Perceptual duplicates ----
PHASH_HAMMING_MAX: int = 8  # max Hamming distance for near-duplicates

# ---- Embedding duplicates ----
EMBEDDING_SIMILARITY_MIN: float = 0.95  # cosine similarity threshold

# ---- Outliers ----
OUTLIER_KNN_K: int = 5
OUTLIER_DISTANCE_PERCENTILE: float = 95.0  # flag images beyond this percentile

# ---- Parallel execution ----
MAX_WORKERS: int | None = None  # None → use cpu_count()

# ---- Cache ----
CACHE_DIR_NAME: str = ".imgclean_cache"
CACHE_ENABLED: bool = True
