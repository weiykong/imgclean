from enum import Enum


class IssueType(str, Enum):
    CORRUPTED = "corrupted"
    LOW_RESOLUTION = "low_resolution"
    ASPECT_RATIO = "aspect_ratio"
    BLURRY = "blurry"
    UNDEREXPOSED = "underexposed"
    OVEREXPOSED = "overexposed"
    EXACT_DUPLICATE = "exact_duplicate"
    NEAR_DUPLICATE = "near_duplicate"
    EMBEDDING_DUPLICATE = "embedding_duplicate"
    SPLIT_LEAKAGE = "split_leakage"
    OUTLIER = "outlier"


class Severity(str, Enum):
    ERROR = "error"       # File is unusable
    WARNING = "warning"   # File is degraded or suspicious
    INFO = "info"         # Informational, may want to review
